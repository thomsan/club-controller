from enum import IntEnum
from threading import Lock

import numpy as np
import club_controller.config as app_config
from club_controller.protocol.message_ids import ServerMessageId

from .client import Client
from .client_type_id import ClientTypeId

class NecLedEffectId(IntEnum):
    BEAT = 0

class NECLedStripClient(Client):
    def __init__(self, uid, ip, port, mac, name, color, color_templates, effect_id, frequency):
        self.color = color
        self.color_templates = color_templates
        self.effect_id = effect_id
        self.frequency = frequency
        self.lock = Lock()
        super().__init__(uid, ip, port, mac, int(ClientTypeId.NEC_LED_STRIP_CLIENT), name)


    def toJson(self):
        return {
            "uid": self.uid,
            "mac": self.mac,
            "ip": self.ip,
            "port": self.port,
            "name": self.name,
            "type_id": self.type_id,
            "is_connected": self.is_connected,
            "color": self.color,
            "color_templates": self.color_templates,
            "effect_id": self.effect_id,
            "frequency": self.frequency
        }


    def update_from_json(self, client_json):
        for key, value in client_json.items():
            setattr(self, key, value)


    def process(self, fft_data):
        """Transforms the given fft data into pixel values based on the current config.

        Args:
            fft_data (np.ndarray): Fft data in the range 0 - 1
        """

        self.lock.acquire()

        # get chosen frequency range
        # fft_data spans from 0 to SAMPLING_RATE/2 Hz with spacing SAMPLING_RATE/len(fft_dat)
        spacing = app_config.SAMPLE_RATE / 2 / len(fft_data)
        i_min_freq = int(self.frequency["min"] / spacing)
        i_max_freq = int(self.frequency["max"] / spacing)
        mapped_fft_data = fft_data[i_min_freq:i_max_freq]
        effect_id = NecLedEffectId(self.effect_id)
        #if(effect_id == NecLedEffectId.BEAT):
        #    TODO
        #else:
        #    if __debug__:
        #        print("Unkown effectId: " + str(self.effect_id))
        #    pixel_values = np.zeros(self.num_pixels)


    def update_properties(self, new_properties):
        for key in new_properties:
            setattr(self, key, new_properties[key])


    @staticmethod
    def get_default_properties():
        return {
            "effect_id": 0,
            "color": {
                "nec": "0xff1ae5",
                "r": 255,
                "g": 0,
                "b": 0
            },
            "color_templates": [
                {
                    "nec": "0xff1ae5",
                    "r": 255,
                    "g": 0,
                    "b": 0
                },
                {
                    "nec": "0xff9a65",
                    "r": 0,
                    "g": 255,
                    "b": 0
                },
                {
                    "nec": "0xffa25d",
                    "r": 0,
                    "g": 0,
                    "b": 255
                },
                {
                    "nec": "0xFF22DD",
                    "r": 255,
                    "g": 255,
                    "b": 255
                },
                {
                    "nec": "0xF710EF",
                    "r": 255,
                    "g": 118,
                    "b": 0
                },
                {
                    "nec": "0xF7906F",
                    "r": 159,
                    "g": 176,
                    "b": 245
                },
                {
                    "nec": "0xF730CF",
                    "r": 163,
                    "g": 64,
                    "b": 255
                },
                {
                    "nec": "0xF7B04F",
                    "r": 77,
                    "g": 222,
                    "b": 255
                },
                {
                    "nec": "0xF7708F",
                    "r": 212,
                    "g": 169,
                    "b": 252
                }
            ],
            "frequency": {
                "min": 0,
                "max": 12000
            }
        }


    def send_nec_command(self, nec_command_string):
        int_command = int(nec_command_string, 0)
        print("int_command:  " + str(int_command) + "\nbytes_command: ")
        bytes_command = int_command.to_bytes(4, "big")
        print(bytes_command)
        self.send_message(ServerMessageId.LED_STRIP_NEC_UPDATE, bytes_command)
