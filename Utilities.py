import asyncio
import re
import logging
import httpx

from Config import Config


class Utilities:
    _lock = asyncio.Lock()

    @classmethod
    async def update_twitch_access_token(cls):
        async with cls._lock:
            (
                access_token,
                client_id,
                client_secret,
                refresh_token,
            ) = await cls.get_twitch_config()
            logging.debug("Refreshing Twitch Chat tokens")
            twitch_refresh_url = str(
                f"https://id.twitch.tv/oauth2/token?"
                f"grant_type=refresh_token&"
                f"refresh_token={refresh_token}&"
                f"client_id={client_id}&"
                f"client_secret={client_secret}"
            )
            async with httpx.AsyncClient() as client:
                refresh = await client.post(twitch_refresh_url)
            logging.debug(f"Refresh response: {refresh.json()}")
            Config.reload_config()
            Config.set("twitch", "access_token", refresh.json()["access_token"])
            Config.set("twitch", "refresh_token", refresh.json()["refresh_token"])
            Config.save_config()
            return refresh.json()["access_token"]

    @classmethod
    def find_username(cls, message) -> str:
        twitch_username_pattern = "@(\w+)"
        res = re.search(twitch_username_pattern, message)
        if not res:
            res = message.split(" ")
            if len(res) > 1:
                return res[1]
            else:
                return False
        return res.group(1)

    @classmethod
    async def get_twitch_config(cls):
        return (
            Config.get("twitch", "access_token"),
            Config.get("twitch", "client_id"),
            Config.get("twitch", "client_secret"),
            Config.get("twitch", "refresh_token"),
        )

    @classmethod
    async def get_twitch_headers(cls):
        (
            access_token,
            client_id,
            client_secret,
            refresh_token,
        ) = await cls.get_twitch_config()
        return {
            "Client-ID": client_id,
            "Authorization": f"Bearer {access_token}",
        }

    @classmethod
    async def get_twitch_user_info(cls, username: str = None):
        url = "https://api.twitch.tv/helix/users"
        headers = await cls.get_twitch_headers()
        params = {"login": username}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
        if len(response.json()["data"]) == 0:
            return None
        return response.json()["data"][0]

    @classmethod
    async def get_twitch_channel_info(cls, user_id: str = None):
        url = f"https://api.twitch.tv/helix/channels?broadcaster_id={user_id}"
        headers = await cls.get_twitch_headers()
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
        return response.json()["data"][0]

    @classmethod
    async def get_twitch_stream_info(
        cls,
        user_id: str = None,
        type: str = "all",
    ):
        url = "https://api.twitch.tv/helix/streams"
        headers = await cls.get_twitch_headers()
        params = {"user_id": user_id, "type": type}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
        if len(response.json()["data"]) == 0:
            return None
        return response.json()["data"][0]
