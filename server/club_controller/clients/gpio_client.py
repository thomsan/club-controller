from enum import IntEnum

import numpy as np
from club_controller.protocol.message_ids import ServerMessageId

from .client import Client
from .client_type_id import ClientTypeId


class GPIOMode(IntEnum):
    DISABLED = 0
    INPUT = 1
    OUTPUT = 2

class GPIOClient(Client):
    def __init__(self, uid, ip, port, mac, name, gpio_modes):
        self.gpio_modes = gpio_modes
        self.gpio_values = [False] * len(gpio_modes)
        super().__init__(uid, ip, port, mac, int(ClientTypeId.GPIO_CLIENT), name)


    def toJson(self):
        return {
            "uid": self.uid,
            "mac": self.mac,
            "ip": self.ip,
            "port": self.port,
            "name": self.name,
            "type_id": self.type_id,
            "is_connected": self.is_connected,
            "gpio_modes": self.gpio_modes,
            "gpio_values": self.gpio_values
        }


    def update_from_json(self, client_json):
        for key, value in client_json.items():
            setattr(self, key, value)
        self.send_gpio_data()


    def send_gpio_data(self):
        self.send_message(ServerMessageId.GPIO_UPDATE, bytearray([int(b) for b in self.gpio_values]))


    @staticmethod
    def get_default_properties():
        return {
            "gpio_modes": [int(GPIOMode.DISABLED)] * 16
        }
