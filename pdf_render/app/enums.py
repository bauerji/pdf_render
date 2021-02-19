from enum import IntEnum


class DocumentStatus(IntEnum):
    PROCESSING = 1
    DONE = 2
    FAILED = 3
