import logging
from twitchio.ext import commands


class TwitchChat(commands.Bot):
    def __init__(
        self,
        access_token,
        bot_prefix,
        channels,
        client_id,
        client_secret,
        *args,
        **kwargs,
    ):
        super().__init__(
            token=access_token,
            prefix=bot_prefix,
            initial_channels=channels,
            client_id=client_id,
            client_secret=client_secret,
            case_insensitive=True,
        )

    async def event_ready(self):
        logging.info(f"Ready | {self.nick}")

    async def event_message(self, message):
        logging.info(message.content)

        await self.handle_commands(message)

    @commands.command(name="test")
    async def my_command(self, ctx):
        await ctx.send("Hello World!")
