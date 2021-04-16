import time
import numpy as np
import pyaudio


""" Takes care of audio input sources"""
class AudioInput:
    def __init__(self, mic_rate, frames_per_buffer):
      self.is_running = False
      self.mic_rate = mic_rate
      self.frames_per_buffer = frames_per_buffer

    def run(self, callback):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=self.mic_rate,
                        input=True,
                        frames_per_buffer=self.frames_per_buffer)
        overflows = 0
        prev_ovf_time = time.time()
        self.is_running = True
        while self.is_running:
            try:
                y = np.frombuffer(stream.read(self.samples_per_frame, exception_on_overflow=False), dtype=np.int16)
                y = y.astype(np.float32)
                stream.read(stream.get_read_available(), exception_on_overflow=False)
                callback(y)
            except IOError:
                overflows += 1
                if time.time() > prev_ovf_time + 1:
                    prev_ovf_time = time.time()
                    print('Audio buffer has overflowed {} times'.format(overflows))
        stream.stop_stream()
        stream.close()
        p.terminate()

    def stop(self):
        self.is_running = False
