import configparser

config = configparser.ConfigParser()
config.read("config.ini")

sections = config.sections()
for section in sections:
    if section == "twitch":
        continue
    print(section)

    options = config.options(section)
    for option in options:
        print(option, config.get(section, option))

    print()
