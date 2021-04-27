import asyncio
import sys
from threading import Thread

from club_controller import config as app_config
import numpy as np
from club_controller.audio_udp_server.dsp import interpolate
from club_controller.clients.client_udp_listener import ClientUDPListener
from scipy.ndimage.filters import gaussian_filter1d

from .audio_input import AudioInput
from .dsp import Dsp
from .filters import ExpFilter
from .fps import FpsCounter

"""
Audio server
processes the audio input for each client and sends data via UDP connection.
"""
class AudioServer:
    def __init__(self, client_handler, show_gui):
        self.client_handler = client_handler
        self.show_gui = show_gui
        self.samples_per_frame = int(app_config.SAMPLE_RATE / app_config.FPS)
        self.gui_freq_min = 0
        self.gui_freq_max = app_config.SAMPLE_RATE/2
        self.n_gui_fft_bins = int(self.gui_freq_max - self.gui_freq_min)
        self.fft_plot_filter = ExpFilter(np.tile(1e-1, self.n_gui_fft_bins), alpha_decay=0.5, alpha_rise=0.99)
        self.volume = ExpFilter(app_config.MIN_VOLUME_THRESHOLD, alpha_decay=0.02, alpha_rise=0.02)
        self.fps_counter = FpsCounter(app_config.PRINT_FPS, app_config.FPS)
        self.dsp = Dsp(app_config.SAMPLE_RATE)
        self.previous_samples = []
        self.fft_gain = ExpFilter(np.tile(1e-1, self.n_gui_fft_bins), alpha_decay=0.01, alpha_rise=0.99)


    def run(self):
        if self.show_gui:
            self.setup_gui()
        self.audio_input = AudioInput(app_config.SAMPLE_RATE, self.samples_per_frame)
        self.audio_input.run(self.on_microphone_update)


    def run_audio_input_async(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        run_audio_input = self.audio_input.run(self.on_microphone_update)

        asyncio.get_event_loop().run_until_complete(run_audio_input)
        asyncio.get_event_loop().run_forever()


    def setup_gui(self):
        # Create GUI window
        from pyqtgraph.Qt import QtGui
        import pyqtgraph as pg
        self.app = QtGui.QApplication([])
        self.view = pg.GraphicsView()
        self.layout = pg.GraphicsLayout(border=(100,100,100))
        self.view.setCentralItem(self.layout)
        self.view.show()
        self.view.setWindowTitle('Audio processing')
        self.view.resize(1280,800)
        # FFT filterbank plot
        self.fft_plot = self.layout.addPlot(title='FFT Output', colspan=4)
        self.fft_plot.setRange(yRange=[-0.1, 1.2])
        self.fft_plot.disableAutoRange(axis=pg.ViewBox.YAxis)
        self.fft_curve = pg.PlotCurveItem()
        x_data = np.array(range(1, app_config.SAMPLE_RATE//2 + 1))
        self.fft_curve.setData(x=x_data, y=x_data*0)
        self.fft_plot.addItem(self.fft_curve)


    def on_microphone_update(self, normalized_samples):
        rolling_window_samples = np.append(self.previous_samples, normalized_samples)
        self.previous_samples = normalized_samples

        # TODO check if filter is necessary: vol = self.volume.update(np.max(np.abs(y_data)))
        vol = np.max(np.abs(rolling_window_samples))
        if vol < app_config.MIN_VOLUME_THRESHOLD:
            fft_data = np.zeros(len(normalized_samples))
            if __debug__:
                print("Volume below threshold")
        else:
            fft_data = self.dsp.get_fft(rolling_window_samples)

        # send to all connected clients
        # TODO measure times and check if things need to be done asynchronous
        for client in self.client_handler.get_led_strip_clients():
            if(client.is_connected):
                client.process(fft_data)
                client.send_pixel_data()

        if self.show_gui:
            # map to gui freq range
            spacing = app_config.SAMPLE_RATE / 2 / len(fft_data)
            i_min_freq = int(self.gui_freq_min / spacing)
            i_max_freq = int(self.gui_freq_max / spacing)
            mapped_fft_data = fft_data[i_min_freq:i_max_freq]
            # interpolate variable fft_data length to number of gui fft bins
            interpolated_fft_data = interpolate(mapped_fft_data, self.n_gui_fft_bins)
            # gain normalization
            self.fft_gain.update(np.max(gaussian_filter1d(interpolated_fft_data, sigma=1.0)))
            interpolated_fft_data /= self.fft_gain.value
            x = np.linspace(self.gui_freq_min, self.gui_freq_max, len(interpolated_fft_data))
            #self.fft_curve.setData(x=x, y=self.fft_plot_filter.update(interpolated_fft_data))
            self.fft_curve.setData(x=x, y=interpolated_fft_data)
            self.app.processEvents()

        self.fps_counter.update()


    def stop(self):
        self.audio_input.stop()

if __name__ == '__main__':
    audio_server = None
    try:
        client_handler = ClientUDPListener()
        client_handler_thread = Thread(target=client_handler.run, name="UDP-Listener-Thread")
        client_handler_thread.start()
        audio_server = AudioServer(client_handler)
    except KeyboardInterrupt:
        print('Interrupted by keyboard')
        audio_server.stop()
        client_handler.stop()
        client_handler_thread.join()
        sys.exit(0)
