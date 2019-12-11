import analogio
import board

class AnalogJoystick:
    def __init__(self, pin_x=None, pin_y=None, x_invert=False, y_invert=True, deadzone=8000):
        self._x = analogio.AnalogIn(pin_x or board.JOYSTICK_X)
        self._y = analogio.AnalogIn(pin_y or board.JOYSTICK_Y)
        self.x_invert = x_invert
        self.y_invert = y_invert
        self.deadzone = deadzone
        self.recenter()
        self.poll()

    def poll(self):
        self.x = (self._x.value - self.x_center) * (-1 if self.x_invert else 1)
        self.y = (self._y.value - self.y_center) * (-1 if self.y_invert else 1)
        return [self.up, self.down, self.left, self.right]

    @property
    def up(self):
        return self.y > self.deadzone

    @property
    def down(self):
        return self.y < -self.deadzone

    @property
    def left(self):
        return self.x < -self.deadzone

    @property
    def right(self):
        return self.x > self.deadzone

    def recenter(self):
        self.x_center = self._x.value
        self.y_center = self._y.value
