import asyncio
import copy
import sys
import time
from threading import Thread

import python.config as app_config
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from scipy.ndimage.filters import gaussian_filter1d

from .audio_input import AudioInput
from python.clients.client import ClientTypeId
from .dsp import Dsp
from .filters import ExpFilter
from python.clients.client_udp_listener import ClientUDPListener

"""
Audio server
processes the audio input for each client and sends data via UDP connection.
"""
class AudioServer:
    def __init__(self, client_handler, print_fps, use_gui, gui_dsp_config, desired_fps, mic_rate, min_volume_threshold):
        """The previous time that the frames_per_second() function was called"""
        self._time_prev = time.time() * 1000.0
        """The low-pass filter used to estimate frames-per-second"""
        self._fps = ExpFilter(val=desired_fps, alpha_decay=0.2, alpha_rise=0.2)
        """Number of audio samples to read every time frame"""
        self.samples_per_frame = int(mic_rate / desired_fps)
        """Array containing the rolling audio sample window"""
        self.y_roll = np.random.rand(gui_dsp_config["n_rolling_history"], self.samples_per_frame) / 1e16
        self.fft_plot_filter = ExpFilter(np.tile(1e-1, gui_dsp_config["n_fft_bins"]), alpha_decay=0.5, alpha_rise=0.99)
        self.volume = ExpFilter(min_volume_threshold, alpha_decay=0.02, alpha_rise=0.02)
        self.prev_fps_update = time.time()
        self.client_handler = client_handler
        self.print_fps = print_fps
        self.gui_dsp_config = copy.deepcopy(gui_dsp_config)
        self.desired_fps = desired_fps
        self.mic_rate = mic_rate
        self.use_gui = use_gui

    def run(self):
        if self.use_gui:
            self.setup_gui()
        self.audio_input = AudioInput(self.mic_rate, self.samples_per_frame)
        self.audio_input.run(self.on_microphone_update)

    def run_audio_input_async(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        run_audio_input = self.audio_input.run(self.on_microphone_update)

        asyncio.get_event_loop().run_until_complete(run_audio_input)
        asyncio.get_event_loop().run_forever()


    def setup_gui(self):
        self.gui_freq_min = self.gui_dsp_config["frequency"]["min"]
        self.gui_freq_max = self.gui_dsp_config["frequency"]["max"]
        self.gui_dsp = Dsp(self.gui_dsp_config, self.mic_rate)
        # Create GUI window
        self.app = QtGui.QApplication([])
        self.view = pg.GraphicsView()
        self.layout = pg.GraphicsLayout(border=(100,100,100))
        self.view.setCentralItem(self.layout)
        self.view.show()
        self.view.setWindowTitle('Audio processing')
        self.view.resize(1280,800)
        # Mel filterbank plot
        self.fft_plot = self.layout.addPlot(title='Filterbank Output', colspan=4)
        self.fft_plot.setRange(yRange=[-0.1, 1.2])
        self.fft_plot.disableAutoRange(axis=pg.ViewBox.YAxis)
        x_data = np.array(range(1, self.gui_dsp_config["n_fft_bins"] + 1))
        self.mel_curve = pg.PlotCurveItem()
        self.mel_curve.setData(x=x_data, y=x_data*0)
        self.fft_plot.addItem(self.mel_curve)


    def on_microphone_update(self, audio_samples):
        # Normalize samples between 0 and 1
        y = audio_samples / 2.0**15
        # Construct a rolling window of audio samples
        self.y_roll[:-1] = self.y_roll[1:]
        self.y_roll[-1, :] = np.copy(y)
        rolling_window_data = np.concatenate(self.y_roll, axis=0).astype(np.float32)
        led_clients = list(filter(lambda c: c.type == ClientTypeId.LED_STRIP_CLIENT, self.client_handler.get_clients()))
        for client in led_clients:
            client.update_mel_bank(rolling_window_data)
            client.send_pixel_data()

        if self.use_gui:
            self.update_gui_fft_graph(rolling_window_data)
            self.app.processEvents()

        if self.print_fps:
            fps = self.frames_per_second()
            if time.time() - 0.5 > self.prev_fps_update:
                self.prev_fps_update = time.time()
                if __debug__:
                    print('FPS {:.0f} / {:.0f}'.format(fps, self.desired_fps))


    def update_gui_fft_graph(self, rolling_window_data):
        mel = self.gui_dsp.get_mel_bank(rolling_window_data)
        # Plot filterbank output
        x = np.linspace(self.gui_freq_min, self.gui_freq_max, len(mel))
        self.mel_curve.setData(x=x, y=self.fft_plot_filter.update(mel))


    def frames_per_second(self):
        """Return the estimated frames per second

        Returns the current estimate for frames-per-second (FPS).
        FPS is estimated by measured the amount of time that has elapsed since
        this function was previously called. The FPS estimate is low-pass filtered
        to reduce noise.

        This function is intended to be called one time for every iteration of
        the program's main loop.

        Returns
        -------
        fps : float
            Estimated frames-per-second. This value is low-pass filtered
            to reduce noise.
        """
        time_now = time.time() * 1000.0
        dt = time_now - self._time_prev
        self._time_prev = time_now
        if dt == 0.0:
            return self._fps.value
        return self._fps.update(1000.0 / dt)


    def stop(self):
        self.audio_input.stop()

if __name__ == '__main__':
    audio_server = None
    try:
        client_handler = ClientUDPListener()
        client_handler_thread = Thread(target=client_handler.run, name="UDP-Listener-Thread")
        client_handler_thread.start()
        audio_server = AudioServer(
            client_handler=client_handler,
            print_fps=False,
            use_gui=True,
            gui_dsp_config=app_config.DEFAULT_DSP_CONFIG,
            desired_fps=app_config.FPS,
            mic_rate=app_config.MIC_RATE,
            min_volume_threshold=app_config.MIN_VOLUME_THRESHOLD)
    except KeyboardInterrupt:
        print('Interrupted by keyboard')
        audio_server.stop()
        client_handler.stop()
        client_handler_thread.join()
        sys.exit(0)
