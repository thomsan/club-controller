import time
import numpy as np
import pyaudio


class AudioInput:
    """AudiInput takes care of audio input sources"""

    def __init__(self, sample_rate, frames_per_buffer):
        self.is_running = False
        self.sample_rate = sample_rate
        self.frames_per_buffer = frames_per_buffer

    def run(self, callback):
        """Start the audio input source stream

        Args:
            callback (function): Callback receives normalized samples in the range 0 to 1.
        """
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=self.sample_rate,
                        input=True,
                        frames_per_buffer=self.frames_per_buffer)
        overflows = 0
        prev_ovf_time = time.time()
        self.is_running = True
        while self.is_running:
            try:
                # read at least self.frames_per_buffer frames
                samples_string = stream.read(self.frames_per_buffer, exception_on_overflow=__debug__)
                # read everthing that is left in the buffer
                n_samples = stream.get_read_available()
                while n_samples > 0:
                    additional_samples_string = stream.read(stream.get_read_available(), exception_on_overflow=__debug__)
                    samples_string += additional_samples_string
                    n_samples = stream.get_read_available()
                normalized_samples = self.samples_string_to_normalized(samples_string)
                callback(normalized_samples)
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


    def samples_string_to_normalized(self, samples_string):
        '''Returned samples are normalized between 0 and 1.'''
        samples = np.frombuffer(samples_string, dtype=np.int16)
        samples = samples.astype(np.float32)
        return samples / 2.0**15
