import asyncio
import logging
import threading

from Config import Config


class BotThreader:
    def __init__(self):
        self.bot_initialized = threading.Event()
        self.shared_data = {}
        self.loop = asyncio.new_event_loop()  # initialize the event loop

    def init_bot(self):
        asyncio.set_event_loop(self.loop)

        # Initialize the bot
        from TwitchBot import TwitchBot

        bot = TwitchBot(
            Config.get("twitch", "access_token"),
            Config.get("twitch", "client_id"),
            Config.get("twitch", "client_secret"),
            Config.get("twitch", "bot_name"),
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
