import serial
import time
from collections import deque
from decimal import Decimal

class SRTester():
    def __init__(self, port=None, baudrate=19200, timeout=0):
        self.port = 'COM1' if port is None else port
        self.baudrate = baudrate
        self.timeout = timeout

        self.box = serial.Serial(self.port, baudrate=self.baudrate, timeout=self.timeout)

        self.read_items = deque()

    def start(self):
        self.box.flushInput()
        self.box.flushOutput()
        self.box.write(b'\x61')
        time.sleep(0.1)
        self.box.write(b'\x62')
        time.sleep(0.1)
        self.box.write(b'\x64')
        time.sleep(0.1)
        self.box.write(b'\x68')
        time.sleep(0.1)
        self.box.write(b'\x70')
        time.sleep(0.1)
        self.box.write(b'\xA0')

    def stop(self):
        self.box.flushInput()
        self.box.flushOutput()
        self.box.write(b'\x20')
        self.box.write(b'\x70')
        time.sleep(0.1)
        self.box.write(b'\x68')
        time.sleep(0.1)
        self.box.write(b'\x64')
        time.sleep(0.1)
        self.box.write(b'\x62')
        time.sleep(0.1)
        self.box.write(b'\x61')

    def read_indiv(self, ignore_blank=True):
        self.start()
        self.read_items = deque()

        start = time.perf_counter()
        last = time.perf_counter()
        counter = 0
        while counter <= 15000:
            current = time.perf_counter() - start
            inchar = self.box.read(1)
            if True: #if inchar != b'':

                counter += 1
                if counter % 770 == 0:
                   print(current - last)
                   print(current)
                   last = current
                   print()
                #if time.perf_counter() - last >= 1:
                #    print(counter)
                #    print(current)
                #    last = time.perf_counter()
                #    print()

                self.read_items.append((counter, current, inchar))

        self.stop()

    def read_test(self):
        self.read_items = deque()


        self.start()
        start = Decimal(time.perf_counter())
        last = start
        counter = 0
        diffs = []
        while counter <= 16000:
            if counter == 0:
                start = Decimal(time.perf_counter())
                last = start
            inchar = self.box.read(1)
            if inchar != b'':
                counter += 1
                curr = Decimal(time.perf_counter())
                diffs.append(curr - last)
                last = curr

        stop = Decimal(time.perf_counter())
        self.stop()
        print('Total time: ', Decimal(stop-start))
        print('Avg B/s: ', Decimal(counter) / Decimal(stop-start))
        return diffs

       

    def __del__(self):
        self.box.close()
        del self.box

    def read_chunk(self, ignore_blank=True):
        self.start()

        start = time.perf_counter()
        counter = 0
        checks = 0
        prev_waiting = 0
        while counter <= 15000:
            if checks % 150000 == 0:
                print(self.box.in_waiting, 'in waiting')
            checks += 1
            if time.perf_counter() - start >= 10:
                print('Reading...')
                chunk = self.box.read(5000)

                for inchar in chunk:
                    if ignore_blank and inchar == b'':
                        continue
                    else:

                        counter += 1
                        self.read_items.append((counter, (counter*1/800), inchar))
                start = time.perf_counter()
        self.stop()
