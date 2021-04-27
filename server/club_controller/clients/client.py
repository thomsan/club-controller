import json
import socket
import threading
from abc import ABC, abstractmethod

import eventhandler
from club_controller import config as app_config
from club_controller.protocol.message_ids import ServerMessageId

ON_TIMEOUT_EVENT_MESSAGE = "onTimeout"

class Client(ABC):
    def __init__(self, uid, ip, port, mac, type_id, name, is_connected=False):
        self.uid = uid
        self.type_id = type_id
        self.ip = ip
        self.port = port
        self.mac = mac
        self.name = name
        self.is_connected = is_connected
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.event_handler = eventhandler.EventHandler(ON_TIMEOUT_EVENT_MESSAGE)
        self.timeout = threading.Timer(5.0, self.on_client_timeout)
        self.timeout.start()
        super().__init__()


    @abstractmethod
    def toJson(self) -> str:
        pass


    @abstractmethod
    def update_from_json(self, client_json):
        pass


    def stop(self):
        if self.is_connected:
            self.send_message_id(ServerMessageId.DISCONNECT)
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except:
                print("Error while shutting down client socket: " + self.name)
        try:
            self.sock.close()
        except:
            print("Error while closing client socket: " + self.name)


    def send_raw(self, data):
        self.sock.sendto(data, (self.ip, self.port))


    def send_message_id(self, val):
        if __debug__ and app_config.PRINT_UDP_STREAM_MESSAGES:
            print("Sending " + str(val) + " to " + str((self.ip, self.port)))
        self.send_raw(bytes([int(val)]))


    def send_message(self, message_id, data_bytes):
        message_id_bytes = bytes([int(message_id)])
        if __debug__ and app_config.PRINT_UDP_STREAM_MESSAGES:
            print("Sending message with id " + str(message_id) + " and length: " + str(len(data_bytes)) + " to " + str((self.ip, self.port)))
        self.send_raw(message_id_bytes + data_bytes)


    def send_connection_message(self):
        self.send_message(ServerMessageId.CONNECT, json.dumps(self.toJson()).encode('utf-8'))


    def on_client_timeout(self):
        self.event_handler.fire(ON_TIMEOUT_EVENT_MESSAGE, self)


    def keep_alive(self):
        self.timeout.cancel()
        self.timeout = threading.Timer(5.0, self.on_client_timeout)
        self.send_message_id(ServerMessageId.KEEPALIVE)
        self.timeout.start()
