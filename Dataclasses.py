import enum
from dataclasses import dataclass


@dataclass
class ConversationEntry:
    role: str
    content: str


@dataclass
class ConversationStatus(enum.Enum):
    IDLE = 0
    OCCUPIED = 1


@dataclass
class ModuleStatus(enum.Enum):
    IDLE = 0
    RUNNING = 1
    STOPPING = 2


@dataclass
class ChatLevel(enum.Enum):
    VIEWER = 0
    VIP = 1
    SUBSCRIBER = 2
    MODERATOR = 3
    BROADCASTER = 4
