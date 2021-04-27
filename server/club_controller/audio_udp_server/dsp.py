from __future__ import print_function
import numpy as np
import copy
from .filters import ExpFilter
from .melbank import compute_melmat
import scipy.fft
from scipy.ndimage.filters import gaussian_filter1d

class Dsp:
    """Digital signal processor
    """
    def __init__(self, sample_rate):
        self.sample_rate = sample_rate
        """Number of audio samples to read every time frame"""
        #self.create_mel_bank()
        #self.mel_gain = ExpFilter(np.tile(1e-1, self.dsp_config["n_fft_bins"]), alpha_decay=0.01, alpha_rise=0.99)
        #self.mel_smoothing = ExpFilter(np.tile(1e-1, self.dsp_config["n_fft_bins"]), alpha_decay=0.5, alpha_rise=0.99)


    def rfft(self, data, window=None):
        window = 1.0 if window is None else window(len(data))
        ys = np.abs(np.fft.rfft(data * window))
        xs = np.fft.rfftfreq(len(data), 1.0 / self.sample_rate)
        return xs, ys


    def fft(self, data, window=None):
        window = 1.0 if window is None else window(len(data))
        ys = np.fft.fft(data * window)
        xs = np.fft.fftfreq(len(data), 1.0 / self.sample_rate)
        return xs, ys


    #def create_mel_bank(self):
    #    samples = int(self.sample_rate * self.dsp_config["n_rolling_history"] / (2.0 * self.dsp_config["fps"]))
    #    self.mel_y, (_, self.mel_x) = compute_melmat(num_mel_bands=self.dsp_config["n_fft_bins"],
    #                                            freq_min=self.dsp_config["frequency"]["min"],
    #                                            freq_max=self.dsp_config["frequency"]["max"],
    #                                            num_fft_bands=samples,
    #                                            sample_rate=self.sample_rate)


    #def update_mel_bank(self, freq_min, freq_max):
    #    self.dsp_config["frequency"]["min"] = freq_min
    #    self.dsp_config["frequency"]["max"] = freq_max
    #    print("new dsp_frequencies min:" + str(self.dsp_config["frequency"]["min"]) + ", max: " + str(self.dsp_config["frequency"]["max"]))
    #    self.create_mel_bank()


    def get_fft(self, normalized_samples):
        hamming_data = normalized_samples * np.hamming(len(normalized_samples))
        fft_data = scipy.fft.fft(hamming_data)
        n = len(fft_data)
        fft_data = 2.0/n * np.abs(fft_data[:n//2])
        # Transform audio input into the frequency domain
        #N = len(y_data)
        #N_zeros = 2**int(np.ceil(np.log2(N))) - N
        ## Pad with zeros until the next power of two
        #y_data *= self.fft_window
        #y_padded = np.pad(y_data, (0, N_zeros), mode='constant')
        # TODO use self.fft or self.rfft
        #scipy.fft.fft(y_padded)
        return fft_data


    #def get_mel_bank(self, normalized_audio_samples):
    #    fft_data = self.get_fft(normalized_audio_samples)
    ##    if fft_data is None:
    #        return None
    #    else:
    #        YS = np.abs(fft_data[:N // 2])
    #        # Construct a Mel filterbank from the FFT data
    #        mel = np.atleast_2d(YS).T * self.mel_y.T
    #        # Scale data to values more suitable for visualization
    #        # mel = np.sum(mel, axis=0)
    #        mel = np.sum(mel, axis=0)
    #        mel = mel**2.0
    #        # Gain normalization
    #        self.mel_gain.update(np.max(gaussian_filter1d(mel, sigma=1.0)))
    #        mel /= self.mel_gain.value
    #        mel = self.mel_smoothing.update(mel)
    #        return mel


def interpolate(y, new_length):
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
    x_old = np.linspace(0, 1, len(y))
    x_new = np.linspace(0, 1, new_length)
    z = np.interp(x_new, x_old, y)
    return z
