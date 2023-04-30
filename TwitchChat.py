import asyncio
import logging
import threading
from Config import Config

from Dataclasses import ModuleStatus


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
        self.module_name = "twitch_chat"

    def set_status(self, status: ModuleStatus):
        self._status = status

    def get_status(self):
        return self._status

    async def start(self, *args, **kwargs):
        self.set_status(ModuleStatus.RUNNING)
        threader = BotThreader()
        self.set_bot(threader.create_bot())

        bot_run_thread = threading.Thread(
            target=threader.run_bot, args=(self._bot,)
        )
        bot_run_thread.start()

    async def stop(self, *args, **kwargs):
        self.set_status(ModuleStatus.STOPPING)
        # await self._bot.close()

        threader = BotThreader()
        threader.stop_bot()

        self.set_status(ModuleStatus.IDLE)

    @classmethod
    def get_bot(cls):
        return cls._bot

    @classmethod
    def set_bot(cls, bot):
        cls._bot = bot

    @classmethod
    async def join_channel(cls, channel):
        await cls._bot.join_channels([channel])

    @classmethod
    async def leave_channel(cls, channel):
        await cls._bot.send_message_to_channel(channel, "Bye, world!")
        await cls._bot.part_channels([channel])
        cls._bot.active_channels.remove(channel)

    @classmethod
    def list_channels(cls):
        logging.info(f"{cls.bot.active_channels}")
        return cls._bot.active_channels


class BotThreader:
    def __init__(self):
        self.bot_initialized = threading.Event()
        self.shared_data = {}
        self.loop = None

    def init_bot(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # Initialize the bot
        from TwitchBot import TwitchBot

        bot = TwitchBot(
            Config.get("twitch", "access_token"),
            Config.get("twitch", "client_id"),
            Config.get("twitch", "client_secret"),
        )

        # Store the bot instance in the shared_data dictionary
        self.shared_data["bot"] = bot

        # Set the event to signal that the bot is initialized
        self.bot_initialized.set()

    def run_bot(self, bot):
        # Set the loop as the current event loop for this thread
        asyncio.set_event_loop(self.loop)

        self.loop.run_until_complete(bot.run())

    def stop_bot(self):
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)

    def create_bot(self):
        # Initialize the bot in a new thread
        bot_init_thread = threading.Thread(target=self.init_bot)
        bot_init_thread.start()

        # Wait for the bot to be initialized
        self.bot_initialized.wait()

        # Retrieve the bot instance from the shared_data dictionary
        bot = self.shared_data["bot"]

        return bot
