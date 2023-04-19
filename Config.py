import configparser


class Config:
    _config = configparser.ConfigParser()
    _config.read("config.ini")

    @classmethod
    def get(cls, section, option):
        return cls._config.get(section, option)

    @classmethod
    def set(cls, section, option, value):
        cls._config.set(section, option, value)

    @classmethod
    def sections(cls):
        return cls._config.sections()

    @classmethod
    def read_config(cls):
        config = configparser.ConfigParser()
        config.read("config.ini")
        return config

    @classmethod
    def save_config(cls, config):
        with open("config.ini", "w") as configfile:
            config.write(configfile)
