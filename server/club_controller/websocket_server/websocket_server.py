#!/usr/bin/env python
import asyncio
import json
import threading

import websockets
from club_controller import config as app_config
from club_controller.protocol.message_ids import WebsocketActionId


class WebsocketServer:
    def __init__(self, client_handler, ui_config_manager):
        self.client_handler = client_handler
        self.websocket_clients = set()
        self.ui_config_manager = ui_config_manager

    async def on_message_received(self, websocket, message):
        if __debug__:
            print("Received websocket message: " + str(message))
        data = json.loads(message)
        message_id = WebsocketActionId(data["action"])
        if  message_id == WebsocketActionId.CLIENT_LIST_REQUEST:
            await websocket.send(self.get_client_list_message())
        elif message_id == WebsocketActionId.CLIENT_VALUE_UPDATED:
            # TODO only send updated data
            if __debug__:
                print("Received update from client: ", data)
            self.client_handler.update_client(data["data"]["client"])
            await self.send_to_all(self.get_client_list_message())
        elif message_id == WebsocketActionId.ALL_LED_STRIPS_UPDATED:
            self.client_handler.update_all(data["data"])
            await self.send_to_all(self.get_client_list_message())
        elif message_id == WebsocketActionId.UI_CONFIG_REQUEST:
            await websocket.send(self.get_ui_config_message())
        elif message_id == WebsocketActionId.UI_CONFIG_UPDATED:
            self.ui_config_manager.update(data["data"])
            await self.send_to_all(self.get_ui_config_message())
        else:
            if __debug__:
                print("Message id not implemented: ", message_id)


    def get_client_list_message(self):
        return json.dumps({"action": int(WebsocketActionId.CLIENT_LIST), "clients": list(map(lambda c: c.toJson(), self.client_handler.get_clients()))})


    def get_ui_config_message(self):
        return json.dumps({"action": int(WebsocketActionId.UI_CONFIG), "ui": self.ui_config_manager.get()})


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
        await websocket.send(json.dumps({"action": int(WebsocketActionId.HELLO)}))
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
        message = json.dumps({"action": int(WebsocketActionId.CLIENT_CONNECTED), "client": client.toJson()})
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        asyncio.get_event_loop().run_until_complete(self.send_to_all(message))


    def on_client_disonnected(self, client):
        message = json.dumps({"action": int(WebsocketActionId.CLIENT_DISCONNECTED), "client": client.toJson()})
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
