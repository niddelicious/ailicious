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
