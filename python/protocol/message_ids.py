
from enum import IntEnum

class ServerMessageId(IntEnum):
    CONNECT = 1
    DISCONNECT = 2
    KEEPALIVE = 3
    ALREADY_CONNECTED = 4
    LED_STRIP_UPDATE = 50

class ClientMessageId(IntEnum):
    CONNECT = 1
    KEEPALIVE = 3
