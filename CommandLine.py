class CommandLine:
    @classmethod
    def commander(cls):
        command = input("Command: \n")
        if command.startswith("join "):
            event.join_channel(command[5:])
        if command.startswith("leave "):
            event.leave_channel(command[6:])
        if command.startswith("reload config"):
            config.reload()