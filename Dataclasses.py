import enum
from dataclasses import dataclass


@dataclass
class ConversationEntry:
    role: str
    content: str


@dataclass
class ConversationStatus(enum.Enum):
    IDLE = 0
    THINKING = 1
    ERROR = 2


class ModuleStatus(enum.Enum):
    IDLE = 0
    RUNNING = 1
    STOPPING = 2


class ChatLevel(enum.Enum):
    VIEWER = 0
    VIP = 1
    SUBSCRIBER = 2
    MODERATOR = 3
    BROADCASTER = 4
