import logging
from Config import Config
from Threader import Threader
from TwitchChat import TwitchChat
from Modules import Modules


class CommandLine:
    @classmethod
    def commander(cls):
        command = input("Command: \n")
        if command.startswith("start "):
            Modules.start_module(command[6:])
        if command.startswith("join "):
            Threader.run_coroutine(TwitchChat.join_channel(command[5:]))
        if command.startswith("leave "):
            Threader.run_coroutine(TwitchChat.leave_channel(command[6:]))
        if command.startswith("exit"):
            for module in Modules._modules.keys():
                Modules.stop_module(module)
            return False
        if command.startswith("stop "):
            Modules.stop_module(command[5:])
        if command.startswith("status"):
            Modules.get_module_status()
        if command.startswith("update"):
            Config.reload_config()
        if command.startswith("configured"):
            logging.info(f"Configured: {Config.sections()}")
        if command.startswith("list"):
            Threader.run_coroutine(TwitchChat.list_channels())
        if command.startswith("connect all"):
            active_channels = TwitchChat.list_channels()
            configured_channels = Config.get_twitch_channels()
            for channel in configured_channels:
                if channel not in active_channels:
                    Threader.run_coroutine(TwitchChat.join_channel(channel))
        return True
