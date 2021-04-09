import asyncio
import sys
from threading import Thread
from time import sleep

import python.config as app_config
from python.audio_udp_server.audio_server import AudioServer
from python.clients.client_udp_listener import ClientUDPListener
from flask import Flask, jsonify, render_template, request, send_from_directory
from python.websocket_server.websocket_server import WebsocketServer


app = Flask(__name__, static_url_path='/static')
color = "#ffff"


@app.route('/')
def index():
    return render_template('index.html')


def byte_to_bool_array(bytes):
    values = []
    b_values = bytearray(bytes)
    for value in b_values:
        values.append(bool(value))
    return values


def run_audio_server_async():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    run_audio_server = audio_server.run()

    asyncio.get_event_loop().run_until_complete(run_audio_server)
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    try:
        client_handler = ClientUDPListener()
        client_handler_thread = Thread(target=client_handler.run, name="UDP-Listener-Thread")

        audio_server = AudioServer(
            client_handler=client_handler,
            print_fps=False,
            use_gui=True,
            gui_dsp_config=app_config.DEFAULT_DSP_CONFIG,
            desired_fps=app_config.FPS,
            mic_rate=app_config.MIC_RATE,
            min_volume_threshold=app_config.MIN_VOLUME_THRESHOLD)
        websocket_server = WebsocketServer(client_handler=client_handler)
        websocket_server.run()
        flask_server_thread = Thread(target=app.run, kwargs={'host': "0.0.0.0"}, name="Flask-Server-Thread")
        flask_server_thread.setDaemon(True)
        flask_server_thread.start()
        audio_server_thread = Thread(target=audio_server.run, name="Audio-Server-Thread")
        audio_server_thread.start()
        #audio_server.run()
        client_handler_thread.start()
        #app.run()
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
        # TODO stop websockets gracefully
        is_running = False
        print("BYE BYE")
        sys.exit(0)
    print("THIS IS THE END")
