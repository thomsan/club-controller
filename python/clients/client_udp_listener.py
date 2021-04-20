import copy
import json
import os
import socket
from threading import Lock

import python.config as app_config
from eventhandler import EventHandler
from python.protocol.message_ids import ClientMessageId, ServerMessageId

from .client import ON_TIMEOUT_EVENT_MESSAGE, ClientTypeId
from .controller_client import ControllerClient
from .led_strip_client import LedStripClient

ON_CLIENT_CONNECTED_EVENT_MESSAGE = "onClientConnected"
ON_CLIENT_DISCONNECTED_EVENT_MESSAGE = "onClientDisconnected"


class ClientUDPListener:
    def __init__(self):
        self.clients_lock = Lock()
        self.clients = []
        self.event_handler = EventHandler(ON_CLIENT_CONNECTED_EVENT_MESSAGE, ON_CLIENT_DISCONNECTED_EVENT_MESSAGE)
        self.buffer_size = 1024
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((app_config.SERVER_UDP_IP, app_config.SERVER_UDP_PORT))
        self.is_running = True
        if not os.path.exists(app_config.SETTINGS_FILE_PATH):
            self.save_settings_file()

        with open(app_config.SETTINGS_FILE_PATH) as json_file:
            data = json.load(json_file)
            for client_config in data['client_configs']:
                client = self.create_client(client_config)
                if client != None:
                    client.is_connected = False


    def subscribe_on_client_connected(self, callback):
        self.event_handler.link(callback, ON_CLIENT_CONNECTED_EVENT_MESSAGE)


    def subscribe_on_client_disconnected(self, callback):
        self.event_handler.link(callback, ON_CLIENT_DISCONNECTED_EVENT_MESSAGE)


    def get_client_configs(self):
        clients = self.get_clients()
        return list(map(lambda c: c.config, clients))


    def get_clients(self):
        return self.clients


    def get_led_strip_clients(self):
        return list(filter(lambda c: c.type == ClientTypeId.LED_STRIP_CLIENT, self.clients))


    def get_client_by_ip(self, ip):
        self.clients_lock.acquire()
        for client in self.clients:
            if client.config["ip"] == ip:
                self.clients_lock.release()
                return client
        self.clients_lock.release()
        return None


    def get_client_by_mac(self, mac):
        self.clients_lock.acquire()
        for client in self.clients:
            if client.config["mac"] == mac:
                self.clients_lock.release()
                return client
        self.clients_lock.release()
        return None


    def stop(self):
        for client in self.get_clients():
            client.stop()
        self.clients_lock.acquire()
        self.clients = {}
        self.clients_lock.release()
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
        self.clients_lock.acquire()
        del self.clients[self.get_client_by_mac(client.config["mac"])]
        self.clients_lock.release()
        if __debug__:
            print("Client config list: " + str(list(map(lambda c: c["name"], self.get_client_configs()))))


    def on_client_timeout(self, client):
        if __debug__:
            print("Client timeout: " + str(client.config["ip"]))
        self.disconnect(client)


    def handle_client_connection(self, config):
        if __debug__:
            print(config)

        # check if client is already known
        client = self.get_client_by_mac(config["mac"])
        if(client == None):
            if __debug__:
                print("New client connected with ip: " + str(config["ip"]))
            client = self.create_client(config)
            if client == None:
                return
            client.is_connected = True
            client.send_int_as_byte(ServerMessageId.CONNECT)
            self.save_settings_file()
        else:
            if client.is_connected:
                client.send_int_as_byte(ServerMessageId.ALREADY_CONNECTED)
            else:
                if __debug__:
                    print("Client re-connected: " + str(client.config["name"]))
                client.is_connected = True
                client.send_int_as_byte(ServerMessageId.CONNECT)
                self.save_settings_file()



        if __debug__:
            print("Client list: " + str(list(map(lambda c: c["name"], self.get_client_configs()))))
        self.event_handler.fire(ON_CLIENT_CONNECTED_EVENT_MESSAGE, client)
        client.event_handler.link(self.on_client_timeout, ON_TIMEOUT_EVENT_MESSAGE)


    def create_client(self, config):
        type_id = config["typeId"]
        try:
            client_type_id = ClientTypeId(type_id)
        except ValueError:
            print("Unkown client typeId: " + str(type_id))
            return None

        if(client_type_id == ClientTypeId.LED_STRIP_CLIENT):
            config["name"] = "DEFAULT NAME LED STRIP"
            config["led_strip_params"] = copy.deepcopy(app_config.DEFAULT_LED_STRIP_PARAMS)
            client = LedStripClient(config)
        elif(client_type_id == ClientTypeId.CONTROLLER_CLIENT):
            config["name"] = "DEFAULT NAME Controller"
            client = ControllerClient(config)
        else:
            print("client_type_id " + client_type_id + " is not implemented")
            return None
        self.clients_lock.acquire()
        self.clients.append(client)
        self.clients_lock.release()
        return client

    def update_config(self, config):
        client = self.get_client_by_mac(config["mac"])
        if client:
            client.update_config(config)


    def update_all(self, data):
        self.clients_lock.acquire()
        for key, value in data.items():
            if key == "effect_id":
                for client in self.get_led_strip_clients():
                    client.config["led_strip_params"]["effect_id"] = int(value)
            if key == "color":
                for client in self.get_led_strip_clients():
                    client.config["led_strip_params"]["color"] = value
        self.clients_lock.release()

    def save_settings_file(self):
        data = {}
        data["client_configs"] = list(map(lambda c : c.config, self.clients))
        with open(app_config.SETTINGS_FILE_PATH, "w") as f:
            json.dump(data, f)
