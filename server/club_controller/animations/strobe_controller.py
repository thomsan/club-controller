from club_controller.clients.client_mode_id import ClientModeId
import numpy as np
from time import sleep
from threading import Thread

"""
Triggers led strips with strope
"""
class StrobeController:
    is_strobe_on = False
    is_running = False
    strobe_thread = None

    def __init__(self, delay_ms, client_handler):
        self.delay_ms = delay_ms
        self.client_handler = client_handler


    def set_delay(self, delay_ms: int):
        self.delay_ms = delay_ms


    def set_color(self, color):
        self.color = color


    def run(self):
        self.is_running = True
        while self.is_running:
            for client in self.client_handler.get_led_strip_clients():
                if(client.is_connected and client.mode == int(ClientModeId.STROBE)):
                    if self.is_strobe_on:
                        client.set_pixel_data(np.tile(0, (3, client.num_pixels)))
                    else:
                        # TODO set color
                        client.set_pixel_data(np.tile((int)(255/50), (3, client.num_pixels)))
                    client.send_pixel_data()
                    self.is_strobe_on = not self.is_strobe_on
            sleep(self.delay_ms/1000.0)


    def start(self):
        self.stop()
        self.strobe_thread = Thread(target=self.run, name="Strobe-Thread")
        self.strobe_thread.start()


    def stop(self):
        self.is_running = False
        if self.strobe_thread is not None:
            self.strobe_thread.join()
