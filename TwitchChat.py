import asyncio
import logging
import re
from twitchio.ext import commands
from Config import Config

from Dataclasses import ChatLevel, ModuleStatus
from OpenAI import OpenAI


class TwitchChat:
    _bot = None

    def __init__(
        self,
        access_token,
        client_id,
        client_secret,
        *args,
        **kwargs,
    ):
        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret
        self._status = ModuleStatus.IDLE

    def set_status(self, status: ModuleStatus):
        self._status = status

    def get_status(self):
        return self._status

    async def start(self, *args, **kwargs):
        self.set_status(ModuleStatus.RUNNING)
        self.bot = TwitchBot(
            self.access_token,
            self.client_id,
            self.client_secret,
        )
        self.set_bot(self.bot)
        await self.bot.start()

    async def stop(self, *args, **kwargs):
        self.set_status(ModuleStatus.STOPPING)
        await self.bot.close()
        self.set_status(ModuleStatus.IDLE)

    @classmethod
    def get_bot(cls):
        return cls.bot

    @classmethod
    def set_bot(cls, bot):
        cls.bot = bot

    @classmethod
    async def join_channel(cls, channel):
        await cls.bot.join_channels([channel])

    @classmethod
    async def leave_channel(cls, channel):
        await cls.bot.send_message_to_channel(channel, "Bye, world!")
        await cls.bot.part_channels([channel])


class TwitchBot(commands.Bot):
    def __init__(
        self,
        access_token,
        client_id,
        client_secret,
        *args,
        **kwargs,
    ):
        super().__init__(
            token=access_token,
            prefix="!",
            client_id=client_id,
            client_secret=client_secret,
            case_insensitive=True,
        )
        self._pattern = f"@?botdelicious[:;, ]"
        self.ai_instances = {}

    async def event_ready(self):
        logging.info(f"Ready | {self.nick}")
        channels = Config.sections()
        channels.remove("twitch")
        await self.join_channels(channels)

    async def event_channel_joined(self, channel):
        logging.info(f"Join event! Channel:{channel}")
        await self.send_message_to_channel(channel.name, f"Hello, world!")
        self.ai_instances[channel.name] = OpenAI(
            Config.get(channel.name, "org"),
            Config.get(channel.name, "key"),
            Config.get(channel.name, "prompt_message"),
            Config.get(channel.name, "thinking_message"),
            Config.get(channel.name, "error_message"),
            Config.get(channel.name, "memory_size"),
        )

    async def event_message(self, message):
        logging.info(message.content)

        if re.match(self._pattern, message.content):
            logging.info("Matched")
            logging.info(message.author)
            if self.author_meets_level_requirements(
                message.channel.name, message.author, "chat_level"
            ):
                reply = await self.ai_instances[message.channel.name].chat(
                    username=message.author.name, message=message.content
                )
                if reply:
                    await self.send_message_to_channel(
                        message.channel.name, reply
                    )

        if message.content[0] == "!":
            await self.handle_commands(message)
            return

    @commands.command()
    async def so(self, ctx: commands.Context):
        (
            success,
            username,
            message,
            avatar_url,
        ) = await self.ai_instances[
            ctx.channel.name
        ].shoutout(content=ctx.message.content, author=ctx.author.name)
        if message:
            await self.send_message_to_channel(ctx.channel.name, message)

    async def send_message_to_channel(self, channel, message):
        chan = self.get_channel(channel)

        # Split the message into chunks of up to 500 characters
        message_chunks = []
        while message:
            if len(message) > 500:
                last_space_or_punctuation = re.search(
                    r"[\s\.,;!?-]{1,}[^\s\.,;!?-]*$", message[:500]
                )
                if last_space_or_punctuation:
                    split_at = last_space_or_punctuation.start()
                else:
                    split_at = 500

                chunk = message[:split_at]
                message = message[split_at:].lstrip()
            else:
                chunk = message
                message = ""

            message_chunks.append(chunk)

        # Send each chunk as a separate message
        for chunk in message_chunks:
            self.loop.create_task(chan.send(chunk))
            await asyncio.sleep(2)

    def author_meets_level_requirements(
        self, channel, chatter, type="chat_level"
    ):
        chatter_level = self.translate_chatter_level(chatter)
        type_level = ChatLevel[Config.get(channel, type)]
        return self.compare_levels(chatter_level, type_level)

    def translate_chatter_level(self, chatter):
        if chatter.is_broadcaster:
            return ChatLevel.BROADCASTER
        if chatter.is_mod:
            return ChatLevel.MODERATOR
        if chatter.is_subscriber:
            return ChatLevel.SUBSCRIBER
        if chatter.is_vip:
            return ChatLevel.VIP
        return ChatLevel.VIEWER

    def compare_levels(self, chatter_level, required_level):
        return chatter_level.value >= required_level.value
