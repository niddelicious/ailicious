import logging
from Threader import Threader
from Dataclasses import ModuleStatus


class Modules:
    _modules = {}

    @classmethod
    def add_module(cls, module_name, module):
        cls._modules[module_name] = module

    @classmethod
    def start_module(cls, module_name=None, *args, **kwargs):
        module = cls.get_module(module_name)
        if module.get_status() is ModuleStatus.IDLE:
            logging.debug(f"Starting module: {module_name}")
            Threader.run_coroutine(module.start(*args, **kwargs))

    @classmethod
    def stop_module(cls, module_name=None):
        module = cls.get_module(module_name)
        if module.get_status() is ModuleStatus.RUNNING:
            logging.debug(f"Stopping module: {module_name}")
            Threader.run_coroutine(module.stop())

    @classmethod
    def get_module(cls, module_name):
        return cls._modules.get(module_name) or None

    @classmethod
    def get_module_status(cls):
        logging.info(f"Module status:")
        for name, module in cls._modules.items():
            logging.info(f"Module: {name} - Status: {module.get_status()}")
