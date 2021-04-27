import time
from .filters import ExpFilter

class FpsCounter:
    """Frames per second counter"""
    def __init__(self, print_fps, desired_fps):
        """The previous time that the update() function was called"""
        self.prev_ms = time.time() * 1000
        """The low-pass filter used to estimate frames-per-second"""
        self.fps_counter = ExpFilter(val=desired_fps, alpha_decay=0.2, alpha_rise=0.2)
        self.print_fps = print_fps
        self.desired_fps = desired_fps

    def update(self):
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
        now_ms = time.time() * 1000
        dt = now_ms - self.prev_ms
        self.prev_ms = now_ms
        if dt == 0.0:
            return self.fps_counter.value
        fps = self.fps_counter.update(1000.0 / dt)
        if self.print_fps:
            print("dt: {}".format(dt))
            print('FPS {:.0f} / {:.0f}'.format(fps, self.desired_fps))
        return fps
