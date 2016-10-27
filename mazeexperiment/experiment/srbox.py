import serial
import time
from decimal import Decimal

class SRBox():
    def __init__(self, port=None, baudrate=19200, timeout=0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout

        if port is None:
            for p in serial.tools.list_ports.comports():
                dev = p.device
                try:
                    self._box = serial.Serial(dev, baudrate=self.baudrate, timeout=self.timeout)
                    self.port = dev
                    break
                except:
                    self._box = None
                    self.port = None
                    continue

        if self._box is None:
            raise RuntimeError('Could not connect to SRBox')

        self._light_codes = [0b00001, 0b00010, 0b00100, 0b01000, 0b10000]
        self._lights = [False]*5
        self.update_lights()

        self._button_codes = [0b00001, 0b00010, 0b00100, 0b01000, 0b10000]

        self._reading = False

        return self.port

    def _signal(self, byte):
        return self._box.write(byte)

    def _read(self):
        byte == ''
        while byte == '':
            byte = self._box.read(1)

        return byte

    def start_input(self):
        self._box.reset_input_buffer()
        self._box.reset_output_buffer()
        self._signal(chr(0b10100000))
        self._reading = True

    def stop_input(self):
        self._box.reset_input_buffer()
        self._box.reset_output_buffer()
        self._signal(chr(0b00100000))
        self._reading = False

    def close(self):
        self._box.reset_input_buffer()
        self._box.reset_output_buffer()
        self._reading = False
        self._box.close()

    def wait_keys(self):
        if not self._reading:
            self.start()

        while True:
            keys = ord(self._read())
            if keys == 0:
                continue
            else:
                self.stop()
                return self._keys_pressed(keys)

    def get_keys(self, timeout=-1):
        if not self._reading:
            self.start()

        pressed = []

        start_time = time.time()
        current_time = start_time
        last_keys= 0
        while current_time - start_time < timeout:
            current_time = time.time()
            keys = ord(self._read())
            if keys == last_keys:
                continue
            else:
                pressed.append((current_time-start_time, self._keys_pressed(keys)))
                last_keys = keys

        if abs(pressed[-1][0] - (current_time-start_time)) > 0.00125:
            pressed.append((current_time-start_time, self.keys_pressed(last_keys)))

        return presseds

    def _keys_pressed(self, keys):
        pressed = []
        for bit in range(5):
            if ((keys&(self._button_codes[bit]))!=0):
                pressed.append(bit + 1)

        return pressed

    # def _get_bit(self, byte, bit):
    #     return ((byte&(self.masks[bit-1]))!=0)

    def update_lights(self):
        status = 0b1100000
        for i, light in enumerate(self._lights):
            if light:
                status += self._light_codes[i]

        self._box.write(ord(status))

    def set_light(self, light, on, update=False):
        self._lights[light-1] = on
        if update:
            self.update_lights()

    def set_lights(self, lights, update=False):
        if type(lights) is list and len(lights) == len(self._lights):
            self._lights = lights
        elif type(lights) is dict:
            for light, on in lights:
                self.set_light(light, on)

        if update:
            self.update_lights()

    def blink_lights(self, lights, interval=0.25, duration=1):
        if type(lights) is int:
            lights = tuple(lights)

        set_on = True
        start = time.time()
        interval_start = start
        while time.time() - start < duration:
            if time.time() - interval_start >= interval:
                for light in lights:
                    self.set_light(light, set_on)
                self.update_lights()
                interval_start = time.time()
                set_on = False

        for light in lights:
            self.set_light(light, False)
        self.update_lights()
