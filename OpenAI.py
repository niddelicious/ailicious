import openai
import logging

from openai import OpenAIError
from Dataclasses import ConversationEntry, ConversationStatus
from Utilities import Utilities


class OpenAI:
    def __init__(
        self,
        org,
        key,
        prompt_message,
        thinking_message,
        error_message,
        memory_size=10,
    ) -> None:
        openai.organization = org
        openai.api_key = key
        self.prompt = prompt_message
        self.thinking = thinking_message
        self.error = error_message
        self.tokens = 0
        self.conversations = {}
        self.conversations_status = {}
        self.memory_size = int(memory_size)

    def start_conversation(self, username):
        self.conversations[username] = [
            ConversationEntry("system", self.prompt.format(username=username))
        ]
        self.conversations_status[username] = ConversationStatus.IDLE

    def reprompt_conversation(self, username, prompt: str = None):
        self.clean_conversation(username)
        conversation_prompt = (
            prompt if prompt else self.prompt.format(username=username)
        )
        self.conversations[username] = [
            ConversationEntry("system", conversation_prompt)
        ]
        self.conversations_status[username] = ConversationStatus.IDLE

    def clean_conversation(self, username):
        if username in self.conversations:
            del self.conversations[username]
        if username in self.conversations_status:
            del self.conversations_status[username]

    def add_message(self, username, role, message):
        self.conversations[username].append(ConversationEntry(role, message))
        if len(self.conversations[username]) > self.memory_size:
            del self.conversations[username][1:3]

    def get_conversation(self, username):
        logging.debug(self.conversations[username])
        return self.conversations[username]

    def get_conversations_status(self, username):
        if username not in self.conversations_status:
            self.start_conversation(username)
        logging.debug(
            f"Conversation status for {username} is {self.conversations_status[username]}"
        )
        return self.conversations_status[username]

    def set_conversations_status(self, username, status):
        self.conversations_status[username] = status

    async def request_chat(self, messages):
        """
        $0.002 per 1000 tokens using gpt-3.5-turbo
        Which is 1/10th of the cost of text-davinci-003
        Meaning that even with a larger prompt, this is still cheaper
        """
        try:
            json_messages = [message.__dict__ for message in messages]
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=json_messages,
            )
            logging.info(response)
            return response
        except OpenAIError as e:
            logging.error(e)
            return False

    async def chat(self, username: str = None, message: str = None):
        if self.get_conversations_status(username) == ConversationStatus.IDLE:
            self.set_conversations_status(
                username, ConversationStatus.OCCUPIED
            )
            self.add_message(username, "user", message)
            response = await self.request_chat(self.get_conversation(username))
            if response:
                reply = response["choices"][0]["message"]["content"]
                self.add_message(username, "assistant", reply)
            else:
                reply = self.error.format(username=username)
            self.set_conversations_status(username, ConversationStatus.IDLE)
        else:
            reply = self.thinking.format(username=username)
        return reply

    async def shoutout(self, content: str = None, author: str = None):
        """
        Returns success, username, reply, and avatar_url
        Or None, None, None, None if the module is not running
        """
        system_name = "ai_shoutout_generator"
        system_prompt = "Hype Twitch Streamer Shoutout Generator"
        username = Utilities.find_username(content)
        if username:
            user = await Utilities.get_twitch_user_info(username=username)
        else:
            user = None
            username = None
        if not user:
            system_prompt = "Hype Twitch Streamer Shoutout Generator"
            system_message = f"Give a snarky reply about how @{author} tried to shoutout @{username}, but that user doesn't exist."
            avatar_url = None
            success = False
        else:
            user_id = user["id"]
            avatar_url = user["profile_image_url"]
            user_description = user["description"]
            channel_info = await Utilities.get_twitch_channel_info(
                user_id=user_id
            )
            game_name = channel_info["game_name"]
            title = channel_info["title"]
            tags = channel_info["tags"]
            stream_info = await Utilities.get_twitch_stream_info(
                user_id=user_id, type="live"
            )
            live_message = (
                "is currently live and is"
                if stream_info
                else "is currently not live, but was last seen"
            )
            system_message = f"Write a shoutout for a Twitch streamer named {username} who {live_message} playing {game_name} with the stream title {title}. This is their description: {user_description}.  These are their tags: {tags}. Do not list the tags in the reply. Make sure to end the reply with their url: https://twitch.tv/{username}. Keep the reply under 490 characters."
            success = True

        self.reprompt_conversation(system_name, prompt=system_prompt)
        self.add_message(system_name, "assistant", system_message)
        response = await self.request_chat(self.get_conversation(system_name))
        reply = response["choices"][0]["message"]["content"]

        return success, username, reply, avatar_url
