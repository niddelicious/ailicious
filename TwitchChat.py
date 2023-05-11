import asyncio
import logging
import threading
import time
from Config import Config

from Dataclasses import ModuleStatus
from TwitchBot import TwitchBot


class TwitchChat:
    _bot:TwitchBot = None

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
        self.threader = BotThreader()  # Store the BotThreader instance
        self.set_bot(self.threader.create_bot())

        bot_run_thread = threading.Thread(
            target=self.threader.run_bot, args=(self._bot,)
        )
        bot_run_thread.start()
        self.bot_thread = bot_run_thread

    async def stop(self, *args, **kwargs):
        logging.debug("TwitchChat stop initiated")
        self.set_status(ModuleStatus.STOPPING)

        self.threader.stop_bot(
            self._bot
        )  # Use the stored BotThreader instance

        self.bot_thread.join()

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
        logging.info(f"{cls._bot.active_channels}")
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

        # Create a Task object for the bot.run() coroutine
        bot_task = self.loop.create_task(bot.run())

        # Store the bot_task in the shared_data dictionary
        self.shared_data["bot_task"] = bot_task

        # Run the event loop
        self.loop.run_until_complete(bot_task)

    def stop_bot(self, bot):
        if self.loop:
            logging.debug("Bot Stop initiated")
            # Call the bot.stop_bot() method to perform necessary clean-up tasks
            future = asyncio.run_coroutine_threadsafe(
                bot.stop_bot(), self.loop
            )
            future.result()  # Wait for the coroutine to complete
            logging.debug("Routines cancelled")

            # Wait for the bot.run() coroutine to complete
            bot_task = self.shared_data["bot_task"]
            asyncio.run_coroutine_threadsafe(bot_task, self.loop)
            bot_task.result()
            del bot
            self.loop.stop()  # Stop the event loop
            logging.debug("Loop stopped")

    def create_bot(self):
        # Initialize the bot in a new thread
        bot_init_thread = threading.Thread(target=self.init_bot)
        bot_init_thread.start()

        # Wait for the bot to be initialized
        self.bot_initialized.wait()

        # Retrieve the bot instance from the shared_data dictionary
        bot = self.shared_data["bot"]

        return bot
