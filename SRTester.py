import serial
import time
from collections import dequeu

class SRTester():
    def __init__(self, port=None, baudrate=19200, timeout=0):
        self.port = 'COM1' if port is None else port
        self.baudrate = baudrate
        self.timeout = timeout

        self.box = serial.Serial(port, baudrate=baudrate, timeout=timeout)

        self.read_items = deque()

    def start(self):
        self.box.flushInput()
        self.box.flushOutput()
        self.write(b'\xA0')

    def stop(self):
        self.box.flushInput()
        self.box.flushOutput()
        self.write(b'\x20')

    def read_indiv(self, ignore_blank=True):
        self.start()
        self.read_items = deque()

        start = time.monotonic()
        counter = 0
        while counter <= 15000:
            inchar = self.box.read(1)
            current = time.monotonic() - start
            if ignore_blank and inchar == '':
                continue

            counter += 1
            self.read_items.append((counter, current, inchar))

        self.stop()

    def read_chunk(self, ignore_blank=True):
        self.start()

        start = time.monotonic()
        while counter <= 15000:
            if time.monotonic() - start >= 10:
                chunk = self.box.read(5000)

                for inchar in chunk:
                    if ignore_blank and inchar == '':
                        continue

                    counter += 1
                    self.read_items.append((counter, (counter*1/800), inchar))
