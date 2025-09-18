from enum import StrEnum


class AIRequestStatus(StrEnum):
    IDLE = "idle"
    PENDING = "pending"
    DONE = "done"
    ERROR = "error"
