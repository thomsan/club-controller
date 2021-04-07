import copy
import json
import socket
from threading import Lock

import python.config as app_config
from eventhandler import EventHandler
from python.protocol.message_ids import ClientMessageId, ServerMessageId

from .client import ClientTypeId
from .controller_client import ControllerClient
from .led_strip_client import LedStripClient

ON_CLIENT_CONNECTED_EVENT_MESSAGE = "onClientConnected"
ON_CLIENT_DISCONNECTED_EVENT_MESSAGE = "onClientDisconnected"


class ClientUDPListener:
    def __init__(self):
        self.clients_dict_lock = Lock()
        self.clients_dict = {}
        self.event_handler = EventHandler(ON_CLIENT_CONNECTED_EVENT_MESSAGE, ON_CLIENT_DISCONNECTED_EVENT_MESSAGE)
        self.buffer_size = 1024
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((app_config.SERVER_UDP_IP, app_config.SERVER_UDP_PORT))
        self.is_running = True


    def subscribe_on_client_connected(self, callback):
        self.event_handler.link(callback, ON_CLIENT_CONNECTED_EVENT_MESSAGE)


    def subscribe_on_client_disconnected(self, callback):
        self.event_handler.link(callback, ON_CLIENT_DISCONNECTED_EVENT_MESSAGE)


    def get_client_configs(self):
        clients = self.get_clients()
        return list(map(lambda c: c.config, clients))


    def get_clients(self):
        self.clients_dict_lock.acquire()
        clients = list(self.clients_dict.values())
        self.clients_dict_lock.release()
        return clients


    def stop(self):
        for client in self.get_clients():
            client.stop()
        self.clients_dict = {}
        self.is_running = False

        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except:
            print("Error while shutting down server socket")
        try:
            self.sock.close()
        except:
            print("Error while closing server socket")


    def run(self):
        while(self.is_running):
            if __debug__:
                print("Waiting for new UDP message")
            value_pair = self.sock.recvfrom(self.buffer_size)
            message = value_pair[0]
            address = value_pair[1]
            if message.__len__() == 0:
                print("Received message with len 0")
                return

            message_id = message[0]
            message = message[1:]
            if __debug__:
                print("Received messageId: " + str(message_id) + " with message: " + str(message))
            if(ClientMessageId(message_id) == ClientMessageId.CONNECT):
                config = json.loads(message)
                if __debug__:
                    print("Received connect message with config: " + str(config))
                self.handle_client_connection(config)
            else:
                if __debug__:
                    print("Received message: " + str(message) + " from: " + str(address))
                    print("Unkown messageId: " + str(message_id))


    def handle_client_connection(self, config):
        if __debug__:
            print(config)
        type_id = config["typeId"]
        try:
            client_type_id = ClientTypeId(type_id)
        except ValueError:
            print("Unkown client typeId: " + str(type_id))

        if(client_type_id == ClientTypeId.LED_STRIP_CLIENT):
            client = LedStripClient(config)
        elif(client_type_id == ClientTypeId.CONTROLLER_CLIENT):
            client = ControllerClient(config)
        else:
            print("client_type_id " + client_type_id + " is not implemented")
            return


        self.clients_dict_lock.acquire()
        if config["ip"] in self.clients_dict:
            self.clients_dict_lock.release()
            if __debug__:
                print("Client " + config["name"] + " is already connected")
            client.send_int_as_byte(ServerMessageId.ALREADY_CONNECTED)
        else:
            if __debug__:
                print("New Client connected: " + str(config["ip"]))
            self.clients_dict[config["ip"]] = client
            self.clients_dict_lock.release()
            client.send_int_as_byte(ServerMessageId.CONNECT)
            if __debug__:
                print("Client list: " + str(list(map(lambda c: c["name"], self.get_client_configs()))))
            self.event_handler.fire(ON_CLIENT_CONNECTED_EVENT_MESSAGE, client)
