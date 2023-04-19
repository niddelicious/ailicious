import configparser
import requests
import re
import logging

from Config import Config


class Utilities:
    @classmethod
    def update_twitch_acccess_token(
        self, client_id, client_secret, refresh_token
    ):
        logging.debug("Refreshing Twitch Chat tokens")
        twitch_refresh_url = str(
            f"https://id.twitch.tv/oauth2/token?"
            f"grant_type=refresh_token&"
            f"refresh_token={refresh_token}&"
            f"client_id={client_id}&"
            f"client_secret={client_secret}"
        )
        refresh = requests.post(twitch_refresh_url).json()
        logging.debug(f"Refresh response: {refresh}")
        return refresh["access_token"], refresh["refresh_token"]

    @classmethod
    def find_username(cls, message):
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
        )

    @classmethod
    async def get_twitch_headers(cls):
        access_token, client_id, client_secret = await cls.get_twitch_config()
        return {
            "Client-ID": client_id,
            "Authorization": f"Bearer {access_token}",
        }

    @classmethod
    async def get_twitch_user_info(cls, username: str = None):
        url = "https://api.twitch.tv/helix/users"
        headers = await cls.get_twitch_headers()
        params = {"login": username}
        response = requests.get(url, headers=headers, params=params)
        if len(response.json()["data"]) == 0:
            return None
        return response.json()["data"][0]

    @classmethod
    async def get_twitch_channel_info(cls, user_id: str = None):
        url = f"https://api.twitch.tv/helix/channels?broadcaster_id={user_id}"
        headers = await cls.get_twitch_headers()
        response = requests.get(url, headers=headers)
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
        response = requests.get(url, headers=headers, params=params)
        if len(response.json()["data"]) == 0:
            return None
        return response.json()["data"][0]
