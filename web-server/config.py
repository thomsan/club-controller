"""Settings for audio reactive LED strip"""
from __future__ import print_function
from __future__ import division
import os

N_GPIO_PINS = 16

UDP_IP = '192.168.178.43'
"""IP address of the ESP8266. Must match IP in ws2812_controller.ino"""

UDP_PORT = 7777
"""Port number used for socket communication between Python and ESP8266"""

USE_GUI = True
"""Whether or not to display a PyQtGraph GUI plot of visualization"""
