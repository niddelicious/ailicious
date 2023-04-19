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
            return False
        return True
