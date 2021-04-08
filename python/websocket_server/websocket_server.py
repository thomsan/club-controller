#!/usr/bin/env python

# WS server example that synchronizes state across clients

import asyncio
import json
import threading
from enum import IntEnum
from python import config as app_config
import websockets

class WebsocketMessageId(IntEnum):
    CLIENT_LIST_REQUEST = 1
    CLIENT_LIST = 2
    CLIENT_CONNECTED = 3
    CLIENT_DISCONNECTED = 4
    CLIENT_VALUE_UPDATED = 5


class WebsocketServer:
    def __init__(self, client_handler):
        self.client_handler = client_handler
        self.websocket_clients = set()


    async def on_message_received(self, websocket, message):
        data = json.loads(message)
        if WebsocketMessageId(data["type"]) == WebsocketMessageId.CLIENT_LIST_REQUEST:
            await self.websocket.send(self.get_client_list_message())
        elif WebsocketMessageId(data["type"]) == WebsocketMessageId.CLIENT_VALUE_UPDATED:
            # TODO only send updated data
            if __debug__:
                print("Received update from client:  {}", data)
            self.client_handler.update_config(data["config"])
            await self.send_to_all_but_this(websocket, self.get_client_list_message())
        else:
            if __debug__:
                print("unsupported event: {}", data)


    def get_client_list_message(self):
        return json.dumps({"type": int(WebsocketMessageId.CLIENT_LIST), "client_configs": self.client_handler.get_client_configs()})


    async def send_to_all_but_this(self, websocket, message):
        other_ws = list(filter(lambda ws: ws != websocket, self.websocket_clients))
        if other_ws:  # asyncio.wait doesn't accept an empty list
            await asyncio.wait([ws.send(message) for ws in other_ws])


    async def send_to_all(self, message):
        if self.websocket_clients:  # asyncio.wait doesn't accept an empty list
            await asyncio.wait([ws.send(message) for ws in self.websocket_clients])


    async def register(self, websocket):
        self.websocket_clients.add(websocket)


    async def unregister(self, websocket):
        self.websocket_clients.remove(websocket)


    async def handler(self, websocket, path):
        await self.register(websocket)
        if __debug__:
            print("websocket connected on path: " + str(path))
            print("All connected websockets: " + str(self.websocket_clients))
        await websocket.send(self.get_client_list_message())

        try:
            async for message in websocket:
                await self.on_message_received(websocket, message)

        finally:
            await self.unregister(websocket)
            if __debug__:
                print("websocket disconnected on path: " + str(path))
                print("All connected websockets: " + str(self.websocket_clients))


    def start_server_async(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(self.handler, "0.0.0.0", app_config.WEB_SOCKET_PORT)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()


    def on_client_connected(self, client):
        message = json.dumps({"type": int(WebsocketMessageId.CLIENT_CONNECTED), "config": client.config})
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        asyncio.get_event_loop().run_until_complete(self.send_to_all(message))


    def on_client_disonnected(self, client):
        message = json.dumps({"type": int(WebsocketMessageId.CLIENT_DISCONNECTED), "config": client.config})
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        asyncio.get_event_loop().run_until_complete(self.send_to_all(message))


    def run(self):
        self.client_handler.subscribe_on_client_connected(self.on_client_connected)
        self.client_handler.subscribe_on_client_disconnected(self.on_client_disonnected)
        self.server_thread = threading.Thread(target=self.start_server_async, name="Websocket-Server-Thread")
        self.server_thread.start()


    def stop(self):
        self.server_thread.join()
