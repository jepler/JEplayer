import time
class KeyRepeat:
    def __init__(self, getter, rate=0.5):
        self.getter = getter
        self.rate_ns = round(rate * 1e9)
        self.next = -1

    @property
    def value(self):
        state = self.getter()
        if not state:
            self.next = -1
            return False
        now = time.monotonic_ns()
        if state and now > self.next:
            self.next = now + self.rate_ns
            return True
        return False
