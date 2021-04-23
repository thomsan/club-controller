
from enum import IntEnum

class ServerMessageId(IntEnum):
    CONNECT = 0
    DISCONNECT = 1
    KEEPALIVE = 2
    ALREADY_CONNECTED = 3
    LED_STRIP_UPDATE = 50

class ClientMessageId(IntEnum):
    CONNECT = 0
    KEEPALIVE = 1

class WebsocketActionId(IntEnum):
    HELLO = 0
    CLIENT_LIST_REQUEST = 1
    CLIENT_LIST = 2
    CLIENT_CONNECTED = 3
    CLIENT_DISCONNECTED = 4
    CLIENT_VALUE_UPDATED = 5
    ALL_LED_STRIPS_UPDATED = 6
