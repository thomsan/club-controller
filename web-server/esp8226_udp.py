from __future__ import print_function
from __future__ import division

import numpy as np
import config

# ESP8266 uses WiFi communication
import socket
_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

values = bytearray(config.N_GPIO_PINS)
"""IO values for the DIO pins"""

def update():
    global values
    print("Sending:" )
    print(values)
    _sock.sendto(values, (config.UDP_IP, config.UDP_PORT))

# Execute this file to run a IO pin strand test
# If everything is working, you should see GPIO5 pin toggleing with 500ms
if __name__ == '__main__':
    import time
    print('Starting GPIO strand test')
    while True:
        values[5] = not values[5]
        update()
        time.sleep(.5)
