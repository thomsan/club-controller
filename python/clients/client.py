import socket
import threading
from enum import IntEnum

import eventhandler

from python.protocol.message_ids import ServerMessageId

ON_TIMEOUT_EVENT_MESSAGE = "onTimeout"

class ClientTypeId(IntEnum):
    LED_STRIP_CLIENT = 1
    CONTROLLER_CLIENT = 2
    GPIO_CLIENT = 3
    SMOKE_MACHINE_CLIENT = 4


class Client:
    def __init__(self, type, config):
        self.type = type
        self.config = config
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.event_handler = eventhandler.EventHandler(ON_TIMEOUT_EVENT_MESSAGE)
        self.timeout = threading.Timer(5.0, self.on_client_timeout)
        self.timeout.start()

    def stop(self):
        self.send_int_as_byte(ServerMessageId.DISCONNECT)
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except:
            print("Error while shutting down client socket: " + self.config["name"])
        try:
            self.sock.close()
        except:
            print("Error while closing client socket: " + self.config["name"])


    def send_raw(self, data):
        self.sock.sendto(data, (self.config["ip"], self.config["port"]))


    def send_int_as_byte(self, val):
        if __debug__:
            print("Sending " + str(val) + " to " + str((self.config["ip"], self.config["port"])))
        self.send_raw(bytes([int(val)]))


    def send_message(self, message_id, data_bytes):
        message_id_bytes = bytes([int(message_id)])
        if __debug__ and False:
            print("Sending message with id " + str(message_id) + " and length: " + str(len(data_bytes)) + " to " + str((self.config["ip"], self.config["port"])))
        self.send_raw(message_id_bytes + data_bytes)


    def on_client_timeout(self):
        self.event_handler.fire(ON_TIMEOUT_EVENT_MESSAGE, self)


    def keep_alive(self):
        self.timeout.cancel()
        self.timeout = threading.Timer(5.0, self.on_client_timeout)
        self.timeout.start()

class ClientConfig:
    def __init__(self, ip, port, mac, name):
        self.ip = ip
        self.port = port
        self.mac = mac
        self.name = name
