import openai
import logging

from openai import OpenAIError
from Dataclasses import ConversationEntry, ConversationStatus


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
        self.memory_size = memory_size

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

    def get_conversation_status(self, username):
        if username not in self.conversations_status:
            self.start_conversation(username)
        logging.debug(
            f"Conversation status for {username} is {self.conversations_status[username]}"
        )
        return self.conversations_status[username]

    def set_conversation_status(self, username, status):
        self._conversation_status[username] = status

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
