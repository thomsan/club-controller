import asyncio
import json
import sys
from threading import Thread
from time import sleep

import club_controller.config as app_config
from club_controller.audio_udp_server.audio_server import AudioServer
from club_controller.clients.client_udp_listener import ClientUDPListener
from club_controller.misc.config_manager import ConfigManager
from club_controller.websocket_server.websocket_server import WebsocketServer


def run_audio_server_async():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    run_audio_server = audio_server.run()

    asyncio.get_event_loop().run_until_complete(run_audio_server)
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    try:
        with open("club_controller/ui_configs/default_ui_config.json") as config_file:
            ui_config_manager = ConfigManager(app_config.UI_CONFIG_FILE_PATH, default_config=json.load(config_file))
        with open("club_controller/clients/default_clients_config.json") as config_file:
            clients_config_manager = ConfigManager(app_config.CLIENTS_CONFIG_FILE_PATH, default_config=json.load(config_file))
        client_handler = ClientUDPListener(clients_config_manager)
        client_handler_thread = Thread(target=client_handler.run, name="UDP-Listener-Thread")
        client_handler_thread.start()

        audio_server = AudioServer(client_handler)
        audio_server_thread = Thread(target=audio_server.run, name="Audio-Server-Thread")
        audio_server_thread.start()

        websocket_server = WebsocketServer(client_handler=client_handler, ui_config_manager=ui_config_manager)
        websocket_server.run()

        if __debug__:
            print("DEBUG MODE")

        is_running = True
        while is_running:
            sleep(1000)


    except KeyboardInterrupt:
        print('\nInterrupted via Keyboard\n')
        audio_server.stop()
        print("AUDIO SERVER STOPPED")
        audio_server_thread.join()
        print("AUDIO SERVER THREAD JOINED")
        client_handler.stop()
        print("CLIENT HANDLER STOPPED")
        client_handler_thread.join()
        print("CLIENT HANDLER THREAD JOINED")
        # TODO stop websockets gracefully (it already has a event loop internally)
        #websocket_server.stop()
        is_running = False
        ui_config_manager.save()
        clients_config_manager.save()
        print("BYE BYE")
        sys.exit(0)
    print("THIS IS THE END")
