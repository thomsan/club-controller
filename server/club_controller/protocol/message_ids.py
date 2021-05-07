
from enum import IntEnum

class ServerMessageId(IntEnum):
    CONNECT = 0
    DISCONNECT = 1
    KEEPALIVE = 2
    ALREADY_CONNECTED = 3
    LED_STRIP_UPDATE = 100,
    LED_STRIP_NEC_UPDATE = 101
    GPIO_UPDATE = 200

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
    UI_CONFIG_REQUEST = 7
    UI_CONFIG = 8
    UI_CONFIG_UPDATED = 9,
    NEC_COMMAND = 10
