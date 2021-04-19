import copy
from enum import IntEnum
from threading import Lock

import python.config as app_config
import numpy as np
from python.clients.client import Client, ClientConfig, ClientTypeId
from python.audio_udp_server.filters import ExpFilter
from python.protocol.message_ids import ServerMessageId
from scipy.ndimage.filters import gaussian_filter1d
from python.audio_udp_server.dsp import interpolate
class EffectId(IntEnum):
    COLORED_ENERGY = 1
    ENERGY = 2
    SCROLL = 3
    SPECTRUM = 4

class LedStripClient(Client):
    #TODO check if a max refreshrate is necessary
    #_max_led_FPS = int(((N_PIXELS * 30e-6) + 50e-6)**-1.0)
    #assert FPS <= _max_led_FPS, 'FPS must be <= {}'.format(_max_led_FPS)

    def __init__(self, config, led_strip_params):
        # TODO validate config
        self.led_strip_params = led_strip_params
        self.led_strip_params_lock = Lock()
        self.pixels = np.tile(1, (3, self.led_strip_params["num_pixels"]))
        self.pixel_lock = Lock()
        self.p = np.tile(1.0, (3, self.led_strip_params["num_pixels"] // 2))
        self.p_filt = ExpFilter(np.tile(0, (3, self.led_strip_params["num_pixels"] // 2)),
                        alpha_decay=0.1, alpha_rise=0.99)
        self.gain = ExpFilter(np.tile(0.01, self.led_strip_params["num_pixels"] // 2),
                        alpha_decay=0.001, alpha_rise=0.99)
        self.prev_pixels = np.tile(0, (3, self.led_strip_params["num_pixels"]))
        self.prev_spectrum = np.tile(0.01, self.led_strip_params["num_pixels"] // 2)
        self.r_filt = ExpFilter(np.tile(0.01, self.led_strip_params["num_pixels"] // 2),
                            alpha_decay=0.2, alpha_rise=0.99)
        self.g_filt = ExpFilter(np.tile(0.01, self.led_strip_params["num_pixels"] // 2),
                            alpha_decay=0.05, alpha_rise=0.3)
        self.b_filt = ExpFilter(np.tile(0.01, self.led_strip_params["num_pixels"] // 2),
                            alpha_decay=0.1, alpha_rise=0.5)
        self.common_mode = ExpFilter(np.tile(0.01, self.led_strip_params["num_pixels"] // 2),
                            alpha_decay=0.99, alpha_rise=0.01)
        super().__init__(ClientTypeId.LED_STRIP_CLIENT, config)


    def process(self, fft_data):
        """Transforms the given fft data into pixel values based on the current config.

        Args:
            fft_data (np.ndarray): Fft data in the range 0 - 1
        """

        self.led_strip_params_lock.acquire()
        effect_id = EffectId(self.led_strip_params["effect_id"])

        # get chosen frequency range
        # fft_data spans from 0 to SAMPLING_RATE/2 Hz with spacing SAMPLING_RATE/len(fft_dat)
        spacing = app_config.SAMPLE_RATE / 2 / len(fft_data)
        i_min_freq = int(self.led_strip_params["frequency"]["min"] / spacing)
        i_max_freq = int(self.led_strip_params["frequency"]["max"] / spacing)
        mapped_fft_data = fft_data[i_min_freq:i_max_freq]

        if(effect_id == EffectId.COLORED_ENERGY):
            pixel_values = self.get_pixel_values_colored_energy(mapped_fft_data)
        elif(effect_id == EffectId.ENERGY):
            pixel_values = self.get_pixel_values_energy(mapped_fft_data)
        elif(effect_id == EffectId.SCROLL):
            pixel_values = self.get_pixel_values_scroll(mapped_fft_data)
        elif(effect_id == EffectId.SPECTRUM):
            pixel_values = self.get_pixel_values_spectrum(mapped_fft_data)
        else:
            if __debug__:
                print("Unkown effectId: " + str(effect_id))
            pixel_values = np.zeros(self.led_strip_params["num_pixels"])

        self.led_strip_params_lock.release()
        self.pixel_lock.acquire()
        self.pixels = pixel_values
        self.pixel_lock.release()


    def update_parameters(self, new_parameters):
        self.led_strip_params_lock.acquire()
        self.led_strip_params = new_parameters
        self.led_strip_params_lock.release()


    def get_pixel_values_colored_energy(self, fft_data):
        """Effect that expands from the center with increasing sound energy and set color"""
        y = interpolate(fft_data, self.led_strip_params["num_pixels"]//2)
        #y = np.copy(fft_data)
        self.gain.update(y)
        # TODO check what's the difference to above: self.gain.update(np.max(gaussian_filter1d(interpolated_fft_data, sigma=1.0)))
        y /= self.gain.value
        # Scale by the width of the LED strip
        y *= float((self.led_strip_params["num_pixels"] // 2) - 1)
        # Map color channels according to set color and the energy over the freq bands
        color = self.led_strip_params["color"]
        i_on = int(np.mean(y))

        # Assign color to different frequency regions
        self.p[0, :i_on] = color["r"]
        self.p[0, i_on:] = 0.0
        self.p[1, :i_on] = color["g"]
        self.p[1, i_on:] = 0.0
        self.p[2, :i_on] = color["b"]
        self.p[2, i_on:] = 0.0
        self.p_filt.update(self.p)
        p = np.round(self.p_filt.value)
        # Apply substantial blur to smooth the edges
        p[0, :] = gaussian_filter1d(p[0, :], sigma=float(self.led_strip_params["sigma"]))
        p[1, :] = gaussian_filter1d(p[1, :], sigma=float(self.led_strip_params["sigma"]))
        p[2, :] = gaussian_filter1d(p[2, :], sigma=float(self.led_strip_params["sigma"]))
        return np.concatenate((p[:, ::-1], p), axis=1)


    def get_pixel_values_energy(self, mel_data):
        """Effect that expands from the center with increasing sound energy"""
        y = np.copy(mel_data)
        self.gain.update(y)
        y /= self.gain.value
        # Scale by the width of the LED strip
        y *= float((self.led_strip_params["num_pixels"] // 2) - 1)
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
        y = np.copy(interpolate(mel_data, self.led_strip_params["num_pixels"] // 2))
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


    def send_pixel_data(self):
        self.pixel_lock.acquire()
        p = np.copy(self.pixels)
        self.pixel_lock.release()
        if(len(self.pixels) < 2):
            if __debug__:
                print("Can't send pixel data. len(self.pixels): " + str(len(self.pixels)))
            return

        # Truncate values and cast to integer
        p = np.clip(p, 0, 255).astype(int)
        # Pixel indices
        idx = range(p.shape[1])
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
