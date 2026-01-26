from enum import Enum, auto


class Mode(Enum):
    IDLE = auto(),
    GETADDR = auto(),
    GETDATA_TX = auto(),
    GETDATA_BLOCK = auto(),
    GETHEADERS = auto(),
    GETBLOCKS = auto(),
    EXIT = auto()
