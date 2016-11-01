from __future__ import absolute_import, division, print_function
from psychopy import core

import serial
import serial.tools.list_ports
import time
from decimal import Decimal
from threading import Thread, Event

class SRBox():
    def __init__(self, port=None, baudrate=19200, timeout=0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout

        if port is None:
            ports = []
            for p in serial.tools.list_ports.comports():
                ports.append(p.device)

            for dev in ports:
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

        self._record_thread = None
        self._recorded_pressed = None


    def _signal(self, byte):
        if type(byte) is int:
            byte = chr(int)
        return self._box.write(byte)

    def _read(self):
        byte = ''
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

    def waitKeys(self, keyList=None, maxWait=None, timeStamped=False):
        if not self._reading:
            self.start_input()

        if timeStamped:
            clock = timeStamped.getTime
            timeStamped = True
        else:
            clock = time.time

        if maxWait is None:
            run_infinite = True
        else:
            run_infinite = False

        start_time = clock()
        current_time = start_time
        while run_infinite or (current_time - start_time < maxWait):
            current_time = clock()
            keys = ord(self._read())
            if keys == 0:
                continue
            pressed = self._keys_pressed(keys)

            if keyList is not None:
                valid_keys = []
                for key in pressed:
                    if key in keyList:
                        valid_keys.append(key)
            else:
                valids_keys = pressed

            if len(valid_keys) > 0:
                self.stop_input()
                if timeStamped:
                    return valid_keys, current_time
                else:
                    return valid_keys

        return []

    def recordKeys(self, keyList=None, timeStamped=False, maxWait=30):
        if self._record_thread is not None:
            raise RuntimeError('Cannot call recordKeys() more than once without calling getKeys()')
        if self._reading:
            raise RuntimeError('Cannot record keys pressed before recordKeys() is called')

        self._record_thread = Thread(target=self._recorder, args=(keyList, timeStamped))
        self._record_thread.start()

    def _recorder(self, keyList=None, timeStamped=False, maxWait=30):
        self._continue_recording = True
        if timeStamped:
            clock = timeStamped.getTime
            timeStamped = True
        else:
            clock = time.time

        if maxWait is None or maxWait is False:
            run_infinite = True
        else:
            run_infinite = False

        self._recorded_presses = []

        start_time = clock()
        current_time = start_time
        last_keys = 0
        while self._continue_recording and (run_infinite or (current_time - start_time < maxWait)):
            current_time = clock()
            keys = ord(self._read())
            if keys == last_keys:
                continue
            else:
                last_keys = keys

            keys = self._keys_pressed(keys)

            if keyList is not None:
                valid_keys = []
                for key in keys:
                    if key in keyList:
                        valid_keys.append(key)
            else:
                valids_keys = keys

            if len(valid_keys) > 0:
                if timeStamped:
                    self._recorded_presses.append((valid_keys, current_time-start_time))
                else:
                    self._recorded_presses.extend(valid_keys)

        if last_keys != 0 and timeStamped:
            self._recorded_presses.append((current_time-start_time, self._keys_pressed(last_keys)))

        if not timeStamped:
            self._recorded_presses = list(set(self._recorded_presses))


    def get_keys(self, keyList=None, timeout=-1, timeStamp=False):
        if self._recorded_presses is None:
            raise RuntimeError('recordKeys() method must be called before keys are available')

        self._continue_recording = False
        self.stop_input()
        presses = self._recorded_presses
        self._recorded_presses = None
        return presses

        # pressed = []
        #
        # start_time = time.time()
        # current_time = start_time
        # last_keys= 0
        # while current_time - start_time < timeout:
        #     current_time = time.time()
        #     keys = ord(self._read())
        #     if keys == last_keys:
        #         continue
        #     elif len(pressed) > 0 and current_time-pressed[-1][0] < .002:
        #         continue
        #     else:
        #         pressed.append((current_time-start_time, self._keys_pressed(keys)))
        #         last_keys = keys
        #
        # if last_keys != 0 and abs(pressed[-1][0] - (current_time-start_time)) > 0.00125:
        #     pressed.append((current_time-start_time, self._keys_pressed(last_keys)))
        #
        # return pressed

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

        self._signal(chr(status))

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
                set_on = (not set_on)

        for light in lights:
            self.set_light(light, False)
        self.update_lights()
