"""Settings for Audio Server"""
from __future__ import division, print_function

SERVER_UDP_IP = '0.0.0.0'
SERVER_UDP_PORT = 8888
WEB_SOCKET_PORT = 6789

USE_GUI = True
"""Whether or not to display a PyQtGraph GUI plot of visualization"""

PRINT_UDP_STREAM_MESSAGES = False

SAMPLE_RATE = 44100
"""Sampling frequency of the audio source in Hz"""

PRINT_FPS = False
"""If True, print current fps every frame"""

FPS = 60
"""Desired refresh rate of the visualization (frames per second)"""

SETTINGS_FILE_PATH = "./settings.json"
CLIENTS_CONFIG_FILE_PATH = "./club_controller/clients/home_club_clients_config.json"
UI_CONFIG_FILE_PATH = "./club_controller/ui_configs/home_club_ui_config.json"
"""modify your ui with different config files"""

MIN_VOLUME_THRESHOLD = 1e-7
"""No music visualization displayed if input audio volume below threshold. Range 0 to 1."""
