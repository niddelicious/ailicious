import os
import sys
from Modules import Modules
from Threader import Threader
from TwitchChat import TwitchChat
from Utilities import Utilities
from CommandLine import CommandLine
from Config import Config
import logging
import coloredlogs


def main():
    logger = logging.getLogger()
    logger.setLevel("DEBUG")
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s", "%m-%d-%Y %H:%M:%S"
    )
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)
    coloredlogs.install(level="DEBUG", logger=logger)

    Threader.run_coroutine(Utilities.update_twitch_access_token())

    twitch_chat = TwitchChat(
        Config.get("twitch", "access_token"),
        Config.get("twitch", "client_id"),
        Config.get("twitch", "client_secret"),
    )

    Modules.add_module("twitch_chat", twitch_chat)
    Modules.start_module("twitch_chat")

    while CommandLine.commander():
        pass
    Threader.stop_loop()
    logger.info(f"Botdelicious ended")
    os._exit(0)


if __name__ == "__main__":
    """This is executed when run from the command line"""
    main()
