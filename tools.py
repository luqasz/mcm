# -*- coding: UTF-8 -*-

# by default try to use monotonic timer witch is not subjected to local machine time changes
try:
    from time import monotonic as timer
except ImportError:
    from time import time as timer



class StopWatch:

    runtime = None
    stop = None
    start = None

    def __enter__(self):
        self.start = timer()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop = timer()
        self.calc()
        return False

    def calc(self):
        self.runtime = round( (self.stop - self.start), 2 )

