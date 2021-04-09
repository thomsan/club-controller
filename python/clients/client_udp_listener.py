import copy
import json
import socket
from threading import Lock

import python.config as app_config
from eventhandler import EventHandler
from python.protocol.message_ids import ClientMessageId, ServerMessageId

from .client import ClientTypeId, ON_TIMEOUT_EVENT_MESSAGE
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


    def get_client_by_ip(self, ip):
        self.clients_dict_lock.acquire()
        if ip in self.clients_dict:
            self.clients_dict_lock.release()
            return self.clients_dict[ip]
        else:
            self.clients_dict_lock.release()
            return None


    def stop(self):
        for client in self.get_clients():
            client.stop()
        self.clients_dict_lock.aquire()
        self.clients_dict = {}
        self.clients_dict_lock.release()
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
            if __debug__ and app_config.PRINT_UDP_STREAM_MESSAGES:
                print("Waiting for new UDP message")
            value_pair = self.sock.recvfrom(self.buffer_size)
            message = value_pair[0]
            address = value_pair[1]
            if message.__len__() == 0:
                print("Received message with len 0")
                return

            message_id = message[0]
            message = message[1:]
            if __debug__ and app_config.PRINT_UDP_STREAM_MESSAGES:
                print("Received messageId: " + str(message_id) + " with message: " + str(message))
            client_message_id = ClientMessageId(message_id)
            if(client_message_id == ClientMessageId.CONNECT):
                config = json.loads(message)
                if __debug__:
                    print("Received connect message with config: " + str(config))
                self.handle_client_connection(config)
            elif(client_message_id == ClientMessageId.KEEPALIVE):
                if __debug__ and app_config.PRINT_UDP_STREAM_MESSAGES:
                    print("Received KEEPALIVE from : " + str(address))
                client = self.get_client_by_ip(address[0])
                if client != None:
                    client.keep_alive()
                else:
                    if __debug__ and app_config.PRINT_UDP_STREAM_MESSAGES:
                        print("Got KEEPALIVE from unregistered client: " + str(address))

            else:
                if __debug__:
                    print("Received message: " + str(message) + " from: " + str(address))
                    print("Unkown messageId: " + str(message_id))


    def disconnect(self, client):
        if __debug__:
            print("Client disconnected: " + str(client.config["ip"]))
        client.send_int_as_byte(ServerMessageId.DISCONNECT)
        self.event_handler.fire(ON_CLIENT_DISCONNECTED_EVENT_MESSAGE, client)
        self.clients_dict_lock.acquire()
        del self.clients_dict[client.config["ip"]]
        self.clients_dict_lock.release()
        if __debug__:
            print("Client config list: " + str(list(map(lambda c: c["name"], self.get_client_configs()))))


    def on_client_timeout(self, client):
        if __debug__:
            print("Client timeout: " + str(client.config["ip"]))
        self.disconnect(client)


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

        tmp_client = self.get_client_by_ip(config["ip"])
        if tmp_client == None:
            if __debug__:
                print("New client connected: " + str(config["ip"]))
            self.clients_dict_lock.acquire()
            self.clients_dict[config["ip"]] = client
            self.clients_dict_lock.release()
            client.send_int_as_byte(ServerMessageId.CONNECT)
            if __debug__:
                print("Client config list: " + str(list(map(lambda c: c["name"], self.get_client_configs()))))
            self.event_handler.fire(ON_CLIENT_CONNECTED_EVENT_MESSAGE, client)
            client.event_handler.link(self.on_client_timeout, ON_TIMEOUT_EVENT_MESSAGE)
        else:
            if __debug__:
                print("Client " + config["name"] + " with ip " + config["ip"] + " is already connected")
            client.send_int_as_byte(ServerMessageId.ALREADY_CONNECTED)


    def update_config(self, config):
        client = self.get_client_by_ip(config["ip"])
        if client:
            client.config = config


    def update_all(self, data):
        self.clients_dict_lock.acquire()
        for key, value in data.items():
            if key == "effect_id":
                for ip, client in self.clients_dict.items():
                    client.config["led_strip_params"]["effect_id"] = int(value)
            if key == "color":
                for ip, client in self.clients_dict.items():
                    client.config["led_strip_params"]["color"] = value
        self.clients_dict_lock.release()
