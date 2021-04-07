from __future__ import print_function
import numpy as np
import copy
from .filters import ExpFilter
from .melbank import compute_melmat
import scipy.fft
from scipy.ndimage.filters import gaussian_filter1d

"""
Digital signal processor
"""
class Dsp:
    def __init__(self, dsp_config, mic_rate):
        self.dsp_config = copy.deepcopy(dsp_config)
        self.mic_rate = mic_rate
        self.create_mel_bank()
        self.mel_gain = ExpFilter(np.tile(1e-1, dsp_config["n_fft_bins"]), alpha_decay=0.01, alpha_rise=0.99)
        self.mel_smoothing = ExpFilter(np.tile(1e-1, dsp_config["n_fft_bins"]), alpha_decay=0.5, alpha_rise=0.99)
        self.fft_window = np.hamming(int(self.mic_rate / self.dsp_config["fps"]) * dsp_config["n_rolling_history"])


    def rfft(self, data, window=None):
        window = 1.0 if window is None else window(len(data))
        ys = np.abs(np.fft.rfft(data * window))
        xs = np.fft.rfftfreq(len(data), 1.0 / self.mic_rate)
        return xs, ys


    def fft(self, data, window=None):
        window = 1.0 if window is None else window(len(data))
        ys = np.fft.fft(data * window)
        xs = np.fft.fftfreq(len(data), 1.0 / self.mic_rate)
        return xs, ys


    def create_mel_bank(self):
        samples = int(self.mic_rate * self.dsp_config["n_rolling_history"] / (2.0 * self.dsp_config["fps"]))
        self.mel_y, (_, self.mel_x) = compute_melmat(num_mel_bands=self.dsp_config["n_fft_bins"],
                                                freq_min=self.dsp_config["frequency"]["min"],
                                                freq_max=self.dsp_config["frequency"]["max"],
                                                num_fft_bands=samples,
                                                sample_rate=self.mic_rate)


    def update_mel_bank(self, freq_min, freq_max):
        self.freq_min = freq_min
        self.freq_max = freq_max
        self.create_mel_bank()


    def get_mel_bank(self, audio_samples):
        # Transform audio input into the frequency domain
        N = len(audio_samples)
        N_zeros = 2**int(np.ceil(np.log2(N))) - N
        # Pad with zeros until the next power of two
        audio_samples *= self.fft_window
        y_padded = np.pad(audio_samples, (0, N_zeros), mode='constant')
        # TODO use self.fft or self.rfft
        YS = np.abs(scipy.fft.fft(y_padded)[:N // 2])
        # Construct a Mel filterbank from the FFT data
        mel = np.atleast_2d(YS).T * self.mel_y.T
        # Scale data to values more suitable for visualization
        # mel = np.sum(mel, axis=0)
        mel = np.sum(mel, axis=0)
        mel = mel**2.0
        # Gain normalization
        self.mel_gain.update(np.max(gaussian_filter1d(mel, sigma=1.0)))
        mel /= self.mel_gain.value
        mel = self.mel_smoothing.update(mel)
        return mel
