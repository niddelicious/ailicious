import asyncio
import threading
import logging


class Threader:
    _loop = None
    _thread = None

    @classmethod
    def get_event_loop(cls):
        logging.debug(f"Current loop: {cls._loop}")
        return cls._loop

    @classmethod
    def start_loop(cls):
        logging.debug(f"Starting loop")
        cls._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls._loop)
        logging.debug(f"Loop: {cls._loop}")
        logging.debug(f"Starting thread")
        cls._thread = threading.Thread(target=cls._loop.run_forever)
        cls._thread.start()
        logging.debug(f"Thread: {cls._thread}")

    @classmethod
    def stop_loop(cls):
        if cls._loop is not None:
            logging.debug(f"Stopping loop: {cls._loop}")
            cls._loop.call_soon_threadsafe(cls._loop.stop)
            cls._thread.join()
            cls._loop = None
            cls._thread = None

    @classmethod
    def run_coroutine(cls, coro):
        if cls._loop is None:
            cls.start_loop()
        logging.debug(f"Starting coroutine {coro} on loop {cls._loop}")
        asyncio.run_coroutine_threadsafe(coro, cls._loop)
