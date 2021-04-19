"""Settings for Audio Server"""
from __future__ import division, print_function

SERVER_UDP_IP = '0.0.0.0'
SERVER_UDP_PORT = 8888
WEB_SOCKET_PORT = 6789

USE_GUI = True
"""Whether or not to display a PyQtGraph GUI plot of visualization"""

PRINT_UDP_STREAM_MESSAGES = False

MAX_PIXELS_PER_PACKET = 126
"""Max number of pixels per UDP packet sent to a client """

SAMPLE_RATE = 44100
"""Sampling frequency of the audio source in Hz"""

PRINT_FPS = False
"""If True, print current fps every frame"""

FPS = 30
"""Desired refresh rate of the visualization (frames per second)"""

SETTINGS_FILE_PATH = "./settings.json"

MIN_VOLUME_THRESHOLD = 1e-7
"""No music visualization displayed if input audio volume below threshold. Range 0 to 1."""

DEFAULT_LED_STRIP_PARAMS = {
    "num_pixels": 80,
    "effect_id": 1,
    "sigma": 1,
    "color": {
        "r": 255,
        "g": 0,
        "b": 0
    },
    "frequency": {
        "min": 0,
        "max": 100
    },
    "fps": 30
}
