import time


class BackgroundTimer():
    def __init__(self, fn):
        self.fn = fn

    def run(self):
        while 1:
            time.sleep(60)
            self.fn()
