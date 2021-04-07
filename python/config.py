"""Settings for audio reactive LED strip"""
from __future__ import print_function
from __future__ import division
import os

SERVER_UDP_IP = '0.0.0.0'
SERVER_UDP_PORT = 8888
WEB_SOCKET_PORT = 6789

DEVICE = 'esp8266'
#DEVICE = 'pi'
"""Device used to control LED strip. Must be 'pi',  'esp8266' or 'blinkstick'

'esp8266' means that you are using an ESP8266 module to control the LED strip
and commands will be sent to the ESP8266 over WiFi.

'pi' means that you are using a Raspberry Pi as a standalone unit to process
audio input and control the LED strip directly.

'blinkstick' means that a BlinkstickPro is connected to this PC which will be used
to control the leds connected to it.
"""

if DEVICE == 'esp8266':
    UDP_IP = '192.168.178.44'
    """IP address of the ESP8266. Must match IP in ws2812_controller.ino"""
    UDP_PORT = 7777
    """Port number used for socket communication between Python and ESP8266"""
    SOFTWARE_GAMMA_CORRECTION = False
    """Set to False because the firmware handles gamma correction + dither"""

if DEVICE == 'pi':
    LED_PIN = 18
    """GPIO pin connected to the LED strip pixels (must support PWM)"""
    LED_FREQ_HZ = 800000
    """LED signal frequency in Hz (usually 800kHz)"""
    LED_DMA = 5
    """DMA channel used for generating PWM signal (try 5)"""
    BRIGHTNESS = 255
    """Brightness of LED strip between 0 and 255"""
    LED_INVERT = True
    """Set True if using an inverting logic level converter"""
    SOFTWARE_GAMMA_CORRECTION = True
    """Set to True because Raspberry Pi doesn't use hardware dithering"""

if DEVICE == 'blinkstick':
    SOFTWARE_GAMMA_CORRECTION = True
    """Set to True because blinkstick doesn't use hardware dithering"""

USE_GUI = True
"""Whether or not to display a PyQtGraph GUI plot of visualization"""

DISPLAY_FPS = False
"""Whether to display the FPS when running (can reduce performance)"""

MAX_PIXELS_PER_PACKET = 126
"""Max number of pixels per UDP packet sent to a client """

# TODO DELETE:
N_PIXELS = 80
"""Number of pixels in the LED strip (must match ESP8266 firmware)"""

GAMMA_TABLE_PATH = os.path.join(os.path.dirname(__file__), 'audio_udp_server/gamma_table.npy')
"""Location of the gamma correction table"""

MIC_RATE = 44100
"""Sampling frequency of the microphone in Hz"""

FPS = 30
"""Desired refresh rate of the visualization (frames per second)

FPS indicates the desired refresh rate, or frames-per-second, of the audio
visualization. The actual refresh rate may be lower if the computer cannot keep
up with desired FPS value.

Higher framerates improve "responsiveness" and reduce the latency of the
visualization but are more computationally expensive.

Low framerates are less computationally expensive, but the visualization may
appear "sluggish" or out of sync with the audio being played if it is too low.

The FPS should not exceed the maximum refresh rate of the LED strip, which
depends on how long the LED strip is.
"""
# TODO check if want to add this check on client side
_max_led_FPS = int(((N_PIXELS * 30e-6) + 50e-6)**-1.0)
assert FPS <= _max_led_FPS, 'FPS must be <= {}'.format(_max_led_FPS)

MIN_VOLUME_THRESHOLD = 1e-7
"""No music visualization displayed if recorded audio volume below threshold"""

DEFAULT_DSP_CONFIG = {
    "n_rolling_history": 2,
    "n_fft_bins": 24,
    "frequency": {
        "min": 50,
        "max": 12000
    },
    "fps": 30
}

DEFAULT_LED_STRIP_PARAMS = {
    "num_pixels": 0,
    "effect_id": 1,
    "sigma": 1,
    "color": {
        "r": 255,
        "g": 0,
        "b": 0
    },
    "dsp": DEFAULT_DSP_CONFIG
}

PRINT_UDP_STREAM_MESSAGES = False
