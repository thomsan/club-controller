import argparse
import json
import sys
from threading import Thread
from time import sleep

import config as app_config
from audio_udp_server.audio_server import AudioServer
from clients.client_udp_listener import ClientUDPListener
from misc.config_manager import ConfigManager
from websocket_server.websocket_server import WebsocketServer

parser = argparse.ArgumentParser(description='Club controller')
parser.add_argument('--gui', dest='gui', action='store_true')
parser.add_argument('--no-gui', dest='gui', action='store_false')
parser.set_defaults(gui=False)
args = parser.parse_args()
print(args)


if __name__ == '__main__':
    try:
        with open("club_controller/ui_configs/default_ui_config.json") as config_file:
            ui_config_manager = ConfigManager(app_config.UI_CONFIG_FILE_PATH, default_config=json.load(config_file))
        with open("club_controller/clients/default_clients_config.json") as config_file:
            clients_config_manager = ConfigManager(app_config.CLIENTS_CONFIG_FILE_PATH, default_config=json.load(config_file))
        client_handler = ClientUDPListener(clients_config_manager)
        client_handler_thread = Thread(target=client_handler.run, name="UDP-Listener-Thread")
        client_handler_thread.start()

        audio_server = AudioServer(client_handler, args.gui)
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
        audio_server_thread.join()
        client_handler.stop()
        client_handler_thread.join()
        # TODO stop websockets gracefully (it already has a event loop internally)
        #websocket_server.stop()
        is_running = False
        ui_config_manager.save()
        clients_config_manager.save()
        print("BYE BYE")
        sys.exit(0)
    print("THIS IS THE END")
