import configparser
import logging


class Config:
    _config = configparser.ConfigParser()
    _config.read("config.ini")

    @classmethod
    def get(cls, section, option):
        return cls._config.get(section, option, fallback=None)

    @classmethod
    def set(cls, section, option, value):
        if not cls._config.has_section(section):
            cls._config.add_section(section)
        cls._config.set(section, option, value)

    @classmethod
    def add_section(cls, section):
        cls._config.add_section(section)

    @classmethod
    def sections(cls):
        return cls._config.sections()

    @classmethod
    def get_twitch_channels(cls):
        channels = Config.sections()
        channels.remove("twitch")
        return channels

    @classmethod
    def read_config(cls):
        config = configparser.ConfigParser()
        config.read("config.ini")
        return config

    @classmethod
    def reload_config(cls):
        logging.debug("Reloading config")
        cls._config = configparser.ConfigParser()
        cls._config.read("config.ini")
        logging.info(f"Config reloaded: {cls._config.sections()}")

    @classmethod
    def save_config(cls):
        with open("config.ini", "w") as configfile:
            cls._config.write(configfile)
