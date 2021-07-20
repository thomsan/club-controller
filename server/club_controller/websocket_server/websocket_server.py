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
        elif message_id == WebsocketActionId.NEC_COMMAND:
            nec_led_strip_client = self.client_handler.get_client_by_value("uid", data["data"]["client"]["uid"])
            nec_led_strip_client.send_nec_command(data["data"]["command"])
        elif message_id == WebsocketActionId.MAIN_UI_COMPONENT_UPDATED:
            uid = data["data"]["uid"]
            ui_config = self.ui_config_manager.get()
            if ui_config.get("main_ui_components") is None:
                ui_config["main_ui_components"] = []
            ui_component = None
            for ui_c in ui_config["main_ui_components"]:
                if ui_c["uid"] == uid:
                    ui_component = ui_c
            if ui_component == None:
                ui_component = {"uid": uid, "show_in_main_ui": data["data"]["show_in_main_ui"]}
                ui_config["main_ui_components"].append(ui_component)
            else:
                ui_component["show_in_main_ui"] = data["data"]["show_in_main_ui"]
            await self.send_to_all(self.get_ui_config_message())
        elif message_id == WebsocketActionId.SAVE_AS_LED_STRIP_PRESET:
            preset_client = self.client_handler.get_client_by_value("uid", data["data"]["client_uid"])
            ui_config = self.ui_config_manager.get()
            if ui_config.get("led_strip_presets") is None:
                ui_config["led_strip_presets"] = []
            max_uid = -1
            for preset in ui_config["led_strip_presets"]:
                if preset["uid"] >= max_uid:
                    max_uid = preset["uid"]
            preset = {"uid": max_uid + 1, "title": data["data"]["title"], "filter": preset_client.filter, "frequency": preset_client.frequency}
            ui_config["led_strip_presets"].append(preset)
            await self.send_to_all(self.get_ui_config_message())
        elif message_id == WebsocketActionId.APPLY_PRESET:
            client_uid = data["data"]["uid"]
            preset_uid = data["data"]["preset_uid"]
            if client_uid == None:
                print("APPLY_PRESET: client_uid == None")
                return
            if preset_uid == None:
                print("APPLY_PRESET: preset_uid == None")
                return

            ui_config = self.ui_config_manager.get()
            if ui_config.get("led_strip_presets") is None:
                ui_config["led_strip_presets"] = []
            preset = ui_config["led_strip_presets"][preset_uid]
            if preset == None:
                print("APPLY_PRESET: prese == None")
                return
            client = self.client_handler.get_client_by_value("uid", client_uid)
            if client == None:
                print("APPLY_PRESET: client == None")
                return

            client.update_from_json(preset)
            await self.send_to_all(self.get_client_list_message())
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
