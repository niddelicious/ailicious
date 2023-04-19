import configparser
from Threader import Threader
from Modules import Modules
from TwitchChat import TwitchChat
from Utilities import Utilities
from CommandLine import CommandLine
from Config import Config
import logging

logger = logging.getLogger()
logger.setLevel("DEBUG")

access_token, refresh_token = Utilities.update_twitch_acccess_token(
    Config.get("twitch", "client_id"),
    Config.get("twitch", "client_secret"),
    Config.get("twitch", "refresh_token"),
)
Config.set("twitch", "access_token", access_token)
Config.set("twitch", "refresh_token", refresh_token)

print(Config.sections())

twitch_chat = TwitchChat(
    Config.get("twitch", "access_token"),
    Config.get("twitch", "client_id"),
    Config.get("twitch", "client_secret"),
)

Modules.add_module("twitch_chat", twitch_chat)
Modules.start_module("twitch_chat")

while CommandLine.commander():
    pass
