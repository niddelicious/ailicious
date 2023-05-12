import logging
import threading
from BotThreader import BotThreader

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

