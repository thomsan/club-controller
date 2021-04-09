
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

class WebsocketMessageId(IntEnum):
    CLIENT_LIST_REQUEST = 1
    CLIENT_LIST = 2
    CLIENT_CONNECTED = 3
    CLIENT_DISCONNECTED = 4
    CLIENT_VALUE_UPDATED = 5
    ALL_LED_STRIPS_UPDATED = 6
