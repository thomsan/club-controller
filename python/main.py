import asyncio
import sys
from threading import Thread
from time import sleep

from python.audio_udp_server.audio_server import AudioServer
from python.clients.client_udp_listener import ClientUDPListener
from python.websocket_server.websocket_server import WebsocketServer


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
        client_handler_thread.start()

        audio_server = AudioServer(client_handler)
        audio_server_thread = Thread(target=audio_server.run, name="Audio-Server-Thread")
        audio_server_thread.start()

        websocket_server = WebsocketServer(client_handler=client_handler)
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
        print("BYE BYE")
        sys.exit(0)
    print("THIS IS THE END")
