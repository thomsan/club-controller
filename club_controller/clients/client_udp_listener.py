import copy
import json
import os
import socket
from threading import Lock

import club_controller.config as app_config
from club_controller.protocol.message_ids import (ClientMessageId,
                                                  ServerMessageId)
from eventhandler import EventHandler

from .client import ON_TIMEOUT_EVENT_MESSAGE
from .client_provider import client_provider
from .client_type_id import ClientTypeId

ON_CLIENT_CONNECTED_EVENT_MESSAGE = "onClientConnected"
ON_CLIENT_DISCONNECTED_EVENT_MESSAGE = "onClientDisconnected"


class ClientUDPListener:
    def __init__(self, client_config_manager):
        self.clients_lock = Lock()
        self.clients = []
        self.client_config_manager = client_config_manager
        self.event_handler = EventHandler(ON_CLIENT_CONNECTED_EVENT_MESSAGE, ON_CLIENT_DISCONNECTED_EVENT_MESSAGE)
        self.buffer_size = 1024
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((app_config.SERVER_UDP_IP, app_config.SERVER_UDP_PORT))
        self.is_running = True

        try:
            for client_json in client_config_manager.get()['clients']:
                known_client = client_provider.get(client_json["type_id"], **client_json)
                if known_client != None:
                    self.clients.append(known_client)
            print("\nSettings file was loaded successfully\n")
        except:
            print("\nSettings file is corrupt\n")


    def get_new_client_uid(self):
        uid = 0
        while any(c.uid == uid for c in self.clients):
            uid += 1
        return uid

    def subscribe_on_client_connected(self, callback):
        self.event_handler.link(callback, ON_CLIENT_CONNECTED_EVENT_MESSAGE)


    def subscribe_on_client_disconnected(self, callback):
        self.event_handler.link(callback, ON_CLIENT_DISCONNECTED_EVENT_MESSAGE)


    def get_clients(self):
        return self.clients


    def get_led_strip_clients(self):
        return list(filter(lambda c: c.type_id == int(ClientTypeId.LED_STRIP_CLIENT), self.clients))


    def get_client_by_value(self, key, value):
        for client in self.clients:
            if client.__dict__[key] == value:
                return client
        return None


    def stop(self):
        for client in self.get_clients():
            client.stop()
        self.is_running = False
        self.update_clients_config()

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
                self.handle_client_connection(message)
            elif(client_message_id == ClientMessageId.KEEPALIVE):
                if __debug__ and app_config.PRINT_UDP_STREAM_MESSAGES:
                    print("Received KEEPALIVE from : " + str(address))
                self.clients_lock.acquire()
                client = self.get_client_by_value("ip", address[0])
                self.clients_lock.release()
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
            print("Client disconnected: " + str(client.ip))
        client.send_message_id(ServerMessageId.DISCONNECT)
        self.event_handler.fire(ON_CLIENT_DISCONNECTED_EVENT_MESSAGE, client)
        self.clients_lock.acquire()
        self.get_client_by_value("uid", client.uid).is_connected = False
        self.clients_lock.release()
        if __debug__:
            self.print_client_list()


    def on_client_timeout(self, client):
        if __debug__:
            print("Client timeout: " + str(client.ip))
        self.disconnect(client)


    def handle_client_connection(self, message):
        message_json = json.loads(message)
        if __debug__:
            print("\nhandle_client_connection message_json: " + str(message_json))
        # check if client is already known
        self.clients_lock.acquire()
        known_client = self.get_client_by_value("mac", message_json["mac"])
        self.clients_lock.release()
        if __debug__:
            try:
                print("known_client: " + str(known_client))
            except:
                print("known_client is None")
        client_already_known = known_client != None
        if client_already_known:
            if __debug__:
                    print("Client is already known with mac: " + str(known_client.mac))
            if known_client.is_connected:
                known_client.send_int_as_byte(ServerMessageId.ALREADY_CONNECTED)
                return
            else:
                self.clients_lock.acquire()
                known_client.is_connected = True
                self.clients_lock.release()
                known_client.send_connection_message()
                self.event_handler.fire(ON_CLIENT_CONNECTED_EVENT_MESSAGE, known_client)
                known_client.event_handler.link(self.on_client_timeout, ON_TIMEOUT_EVENT_MESSAGE)

                self.update_clients_config()
                if __debug__:
                    print("Client re-connected: " + str(known_client.name))
        else:
            if not "name" in message_json:
                message_json["name"] = "NAME NOT SET"
            # get and assign a new uid
            message_json["uid"] = self.get_new_client_uid()
            new_client = client_provider.get(ClientTypeId(message_json["type_id"]), **message_json)
            assert new_client != None
            self.clients_lock.acquire()
            new_client.is_connected = True
            self.clients.append(new_client)
            self.clients_lock.release()
            new_client.send_connection_message()
            self.event_handler.fire(ON_CLIENT_CONNECTED_EVENT_MESSAGE, new_client)
            new_client.event_handler.link(self.on_client_timeout, ON_TIMEOUT_EVENT_MESSAGE)
            self.update_clients_config()
            if __debug__:
                print("New client connected with ip: " + str(new_client.ip))

        if __debug__:
            self.print_client_list()


    def update_client(self, client_json):
        self.clients_lock.acquire()
        client = self.get_client_by_value("uid", client_json["uid"])
        if client:
            client.update_from_json(client_json)
        self.clients_lock.release()


    def update_all(self, data):
        self.clients_lock.acquire()
        # TODO update all available keys
        for key, value in data.items():
            if key == "effect_id":
                for client in self.get_led_strip_clients():
                    client.effect_id = int(value)
            if key == "color":
                for client in self.get_led_strip_clients():
                    client.color = value
        self.clients_lock.release()


    def update_clients_config(self):
        data = {}
        self.clients_lock.acquire()
        data["clients"] = list(map(lambda c : c.toJson(), self.clients))
        self.clients_lock.release()
        self.client_config_manager.update(data)


    def print_client_list(self):
        print("\nClient list: " + str(list(map(lambda c: c.toJson(), self.get_clients()))) + "\n")
