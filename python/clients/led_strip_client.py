import copy
from enum import IntEnum
from threading import Lock

import python.config as app_config
import numpy as np
from python.clients.client import Client, ClientConfig, ClientTypeId
from python.audio_udp_server.dsp import Dsp
from python.audio_udp_server.filters import ExpFilter
from python.protocol.message_ids import ServerMessageId
from scipy.ndimage.filters import gaussian_filter1d

_gamma = np.load(app_config.GAMMA_TABLE_PATH)
"""Gamma lookup table used for nonlinear brightness correction"""

class EffectId(IntEnum):
    COLORED_ENERGY = 1
    ENERGY = 2
    SCROLL = 3
    SPECTRUM = 4


class LedStripConfig(ClientConfig):
    def __init__(self, ip, port, name, led_strip_params):
        self.led_strip_params = led_strip_params
        super().__init__(self, ip, port, name)


    @staticmethod
    def object_decoder(self, obj):
        if '__type__' in obj and obj['__type__'] == 'LedStripConfig':

            return LedStripConfig(obj['ip'], obj['port'], obj['name'], obj['led_strip_params'])
        return obj


class LedStripClient(Client):
    def __init__(self, config):
        # TODO check config
        self.config = config
        self.config_lock = Lock()
        self.p = np.tile(1.0, (3, self.config["led_strip_params"]["num_pixels"] // 2))
        self.p_filt = ExpFilter(np.tile(1, (3, self.config["led_strip_params"]["num_pixels"] // 2)),
                        alpha_decay=0.1, alpha_rise=0.99)
        self.gain = ExpFilter(np.tile(0.01, self.config["led_strip_params"]["dsp"]["n_fft_bins"]),
                        alpha_decay=0.001, alpha_rise=0.99)
        self.pixels = np.tile(1, (3, self.config["led_strip_params"]["num_pixels"]))
        self.prev_pixels = np.tile(253, (3, self.config["led_strip_params"]["num_pixels"]))
        self.prev_spectrum = np.tile(0.01, self.config["led_strip_params"]["num_pixels"] // 2)
        self.dsp = Dsp(config["led_strip_params"]["dsp"], app_config.MIC_RATE)
        self.r_filt = ExpFilter(np.tile(0.01, self.config["led_strip_params"]["num_pixels"] // 2),
                            alpha_decay=0.2, alpha_rise=0.99)
        self.g_filt = ExpFilter(np.tile(0.01, self.config["led_strip_params"]["num_pixels"] // 2),
                            alpha_decay=0.05, alpha_rise=0.3)
        self.b_filt = ExpFilter(np.tile(0.01, self.config["led_strip_params"]["num_pixels"] // 2),
                            alpha_decay=0.1, alpha_rise=0.5)
        self.common_mode = ExpFilter(np.tile(0.01, self.config["led_strip_params"]["num_pixels"] // 2),
                            alpha_decay=0.99, alpha_rise=0.01)
        super().__init__(ClientTypeId.LED_STRIP_CLIENT, self.config)


    def update_config(self, new_config):
        self.config_lock.acquire()
        self.config = new_config
        self.config_lock.release()


    def get_pixel_values(self, mel_data):
        self.config_lock.acquire()
        effect_id = EffectId(self.config["led_strip_params"]["effect_id"])

        if(effect_id == EffectId.COLORED_ENERGY):
            pixel_values = self.get_pixel_values_colored_energy(mel_data)
        elif(effect_id == EffectId.ENERGY):
            pixel_values = self.get_pixel_values_energy(mel_data)
        elif(effect_id == EffectId.SCROLL):
            pixel_values = self.get_pixel_values_scroll(mel_data)
        elif(effect_id == EffectId.SPECTRUM):
            pixel_values = self.get_pixel_values_spectrum(mel_data)
        else:
            if __debug__:
                print("Unkown effectId: " + str(effect_id))
            pixel_values = []
        self.config_lock.release()
        return pixel_values

    def get_pixel_values_colored_energy(self, mel_data):
        """Effect that expands from the center with increasing sound energy and set color"""
        y = np.copy(mel_data)
        self.gain.update(y)
        y /= self.gain.value
        # Scale by the width of the LED strip
        y *= float((self.config["led_strip_params"]["num_pixels"] // 2) - 1)
        # Map color channels according to set color and the energy over the whole freq bands
        scale = 0.9
        color = self.config["led_strip_params"]["color"]
        r = int(np.mean(y**scale * int(color["r"])/256))
        g = int(np.mean(y**scale * int(color["g"])/256))
        b = int(np.mean(y**scale * int(color["b"])/256))

        # Assign color to different frequency regions
        self.p[0, :r] = 255.0
        self.p[0, r:] = 0.0
        self.p[1, :g] = 255.0
        self.p[1, g:] = 0.0
        self.p[2, :b] = 255.0
        self.p[2, b:] = 0.0
        self.p_filt.update(self.p)
        p = np.round(self.p_filt.value)
        # Apply substantial blur to smooth the edges
        p[0, :] = gaussian_filter1d(p[0, :], sigma=float(self.config["led_strip_params"]["sigma"]))
        p[1, :] = gaussian_filter1d(p[1, :], sigma=float(self.config["led_strip_params"]["sigma"]))
        p[2, :] = gaussian_filter1d(p[2, :], sigma=float(self.config["led_strip_params"]["sigma"]))
        return np.concatenate((p[:, ::-1], p), axis=1)


    def get_pixel_values_energy(self, mel_data):
        """Effect that expands from the center with increasing sound energy"""
        y = np.copy(mel_data)
        self.gain.update(y)
        y /= self.gain.value
        # Scale by the width of the LED strip
        y *= float((self.config["led_strip_params"]["num_pixels"] // 2) - 1)
        # Map color channels according to energy in the different freq bands
        scale = 0.9
        r = int(np.mean(y[:len(y) // 3]**scale))
        g = int(np.mean(y[len(y) // 3: 2 * len(y) // 3]**scale))
        b = int(np.mean(y[2 * len(y) // 3:]**scale))
        # Assign color to different frequency regions
        self.p[0, :r] = 255.0
        self.p[0, r:] = 0.0
        self.p[1, :g] = 255.0
        self.p[1, g:] = 0.0
        self.p[2, :b] = 255.0
        self.p[2, b:] = 0.0
        self.p_filt.update(self.p)
        self.p = np.round(self.p_filt.value)
        # Apply substantial blur to smooth the edges
        self.p[0, :] = gaussian_filter1d(self.p[0, :], sigma=4.0)
        self.p[1, :] = gaussian_filter1d(self.p[1, :], sigma=4.0)
        self.p[2, :] = gaussian_filter1d(self.p[2, :], sigma=4.0)
        return np.concatenate((self.p[:, ::-1], self.p), axis=1)


    def get_pixel_values_scroll(self, mel_data):
        """Effect that originates in the center and scrolls outwards"""
        y = np.copy(mel_data)
        y = y**2.0
        self.gain.update(y)
        y /= self.gain.value
        y *= 255.0
        r = int(np.max(y[:len(y) // 3]))
        g = int(np.max(y[len(y) // 3: 2 * len(y) // 3]))
        b = int(np.max(y[2 * len(y) // 3:]))
        # Scrolling effect window
        self.p[:, 1:] = self.p[:, :-1]
        self.p *= 0.98
        self.p = gaussian_filter1d(self.p, sigma=0.2)
        # Create new color originating at the center
        self.p[0, 0] = r
        self.p[1, 0] = g
        self.p[2, 0] = b
        return np.concatenate((self.p[:, ::-1], self.p), axis=1)


    def get_pixel_values_spectrum(self, mel_data):
        """Effect that maps the Mel filterbank frequencies onto the LED strip"""
        y = np.copy(self.interpolate(mel_data, self.config["led_strip_params"]["num_pixels"] // 2))
        self.common_mode.update(y)
        diff = y - self.prev_spectrum
        self.prev_spectrum = np.copy(y)
        # Color channel mappings
        r = self.r_filt.update(y - self.common_mode.value)
        g = np.abs(diff)
        b = self.b_filt.update(np.copy(y))
        # Mirror the color channels for symmetric output
        r = np.concatenate((r[::-1], r))
        g = np.concatenate((g[::-1], g))
        b = np.concatenate((b[::-1], b))
        output = np.array([r, g,b]) * 255
        return output


    def update_mel_bank(self, rolling_window_data):
        vol = np.max(np.abs(rolling_window_data))
        if vol < app_config.MIN_VOLUME_THRESHOLD:
            if __debug__:
                print('No audio input. Volume below threshold. Volume:', vol)
            self.mel_data = np.tile(0, (3, self.config["led_strip_params"]["num_pixels"]))
        else:
            self.mel_data = self.dsp.get_mel_bank(rolling_window_data)


    def send_pixel_data(self):
        self.pixels = self.get_pixel_values(self.mel_data)
        if(len(self.pixels) < 2):
            if __debug__:
                print("Can't send pixel data. len(self.pixels): " + str(len(self.pixels)))
            return

        # Truncate values and cast to integer
        self.pixels = np.clip(self.pixels, 0, 255).astype(int)
        # Optionally apply gamma correction
        p = _gamma[self.pixels] if app_config.SOFTWARE_GAMMA_CORRECTION else np.copy(self.pixels)
        # Pixel indices
        idx = range(self.pixels.shape[1])
        idx = [i for i in idx if not np.array_equal(p[:, i], self.prev_pixels[:, i])]
        n_packets = len(idx) // app_config.MAX_PIXELS_PER_PACKET + 1
        idx = np.array_split(idx, n_packets)
        for packet_indices in idx:
            m = []
            for i in packet_indices:
                m.append(i)  # Index of pixel to change
                m.append(p[0][i])  # Pixel red value
                m.append(p[1][i])  # Pixel green value
                m.append(p[2][i])  # Pixel blue value
            m = bytes(m)
            self.send_message(ServerMessageId.LED_STRIP_UPDATE, m)
        self.prev_pixels = np.copy(p)


    def memoize(function):
        """Provides a decorator for memoizing functions"""
        from functools import wraps
        memo = {}

        @wraps(function)
        def wrapper(*args):
            if args in memo:
                return memo[args]
            else:
                rv = function(*args)
                memo[args] = rv
                return rv
        return wrapper


    @memoize
    def _normalized_linspace(self, size):
        return np.linspace(0, 1, size)


    def interpolate(self, y, new_length):
        """Intelligently resizes the array by linearly interpolating the values

        Parameters
        ----------
        y : np.array
            Array that should be resized

        new_length : int
            The length of the new interpolated array

        Returns
        -------
        z : np.array
            New array with length of new_length that contains the interpolated
            values of y.
        """
        if len(y) == new_length:
            return y
        x_old = self._normalized_linspace(len(y))
        x_new = self._normalized_linspace(new_length)
        z = np.interp(x_new, x_old, y)
        return z
