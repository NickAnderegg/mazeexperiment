#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
from psychopy import locale_setup, visual, core, data, event, logging#, sound, gui
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)

import numpy as np
from numpy.random import random, randint, normal, shuffle

from datetime import datetime
from itertools import chain
import json
import os, sys

from .srbox import SRBox
from .trials import SentenceBlock
from .instructions import Instructions

__version__ = "1.0.0"

class Experiment():
    def __init__(self, exp_name=None, pwd=None):

        if pwd is None:
            self.pwd = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
        else:
            self.pwd = pwd
        os.chdir(self.pwd)

        self.exp_name = u'untitled' if exp_name is None else exp_name
        self.exp_info = {
            u'session': u'001',
            u'participant': u'917',
            u'version': u'{}'.format(__version__)
        }

        # self.get_session_info()

        self.exp_info['exp_name'] = self.exp_name
        self.exp_info['date'] = datetime.today().strftime('%Y-%m-%d')
        self.exp_info['session_start'] = datetime.today().strftime('%H:%M:%S')

        self.participant_id = int(self.exp_info['participant'])

        self.use_srbox = False
        if self.use_srbox:
            self.srbox = SRBox('COM1', 19200, 0)

        # data file name stem
        self.data_file_stem = u'{}{}{}{}{}_{}_{}_{}'.format(
            self.pwd, os.sep,
            u'participant_data', os.sep,
            self.exp_name,
            self.exp_info['participant'],
            self.exp_info['session'],
            datetime.today().strftime('%Y-%m-%d')
        )

        self.experiment = data.ExperimentHandler(
            name = self.exp_name,
            version = self.exp_info['version'],
            extraInfo = self.exp_info,
            runtimeInfo = None,
            originPath = None,
            savePickle = False,
            saveWideText = True,
            dataFileName = self.data_file_stem
        )

        self.log_file = logging.LogFile('{}.log'.format(self.data_file_stem), level=logging.DEBUG)
        logging.console.setLevel(logging.DEBUG)

        self.end_exp_now = False

        self.window = visual.Window(
            size=(1440, 900), fullscr=True, screen=0,
            allowGUI=True, allowStencil=False,
            monitor=u'testMonitor', color=[1,1,1], colorSpace='rgb',
            blendMode='avg', useFBO=True)

        self.exp_info['frameRate'] = self.window.getActualFrameRate()

        if self.exp_info['frameRate'] != None:
            self.frame_dur = 1.0 / round(self.exp_info['frameRate'])
        else:
            self.frame_dur = 1.0 / 60.0  # could not measure, so guess

        self.global_clock    = core.Clock()
        # self.instr_clock    = core.Clock()
        self.sentence_clock = core.Clock()
        self.pair_clock     = core.Clock()

        self.routine_timer  = core.CountdownTimer()

        # instructions = Instructions(self, self.exp_info)
        # instructions.begin_instructions()
        # return
        self.prepare_visuals()
        self.load_latin_square()
        self.load_trials()

        sentence_block = SentenceBlock(self, self.experiment, self.exp_info, self.trials)

    def abort(self):
        self.experiment.saveAsWideText('{}.csv'.format(self.data_file_stem))
        logging.flush()
        # make sure everything is closed down
        self.experiment.abort()  # or data files will save again on exit
        self.window.close()
        core.quit()

    def get_session_info(self):
        dlg = gui.DlgFromDict(
            dictionary=self.exp_info,
            title=self.exp_name,
            fixed=[u'version']
        )

        if dlg.OK == False:
            core.quit()
        else:
            return True

    def prepare_visuals(self):

        self.text_left = visual.TextStim(
            win=self.window,    name='text_left',   text='',
            font='Songti SC',   pos=(-0.1, 0),      height=0.25,
            wrapWidth=None,     color=(-1, -1, -1), colorSpace='rgb',
            opacity=1,          depth=0.0,          ori=0,
            alignHoriz='right'
        )

        self.text_right = visual.TextStim(
            win=self.window,    name='text_right',  text='',
            font='Songti SC',   pos=(0.1, 0),       height=0.25,
            wrapWidth=None,     color=(-1, -1, -1), colorSpace='rgb',
            opacity=1,          depth=0.0,          ori=0,
            alignHoriz='left'
        )

        self.fixation = visual.TextStim(
            win=self.window,    name='fixation',    text='+',
            font='Courier New', pos=(0, 0),         height=0.25,
            wrapWidth=None,     color=(-1, -1, -1), colorSpace='rgb',
            opacity=1,          depth=0.0,          ori=0
        )

        self.acc_feedback = visual.TextStim(
            win=self.window,    name='acc_feedback',text='',
            font='Courier New', pos=(0, 0),         height=0.25,
            wrapWidth=None,     color=(-1,-1,-1),   colorSpace='rgb',
            opacity=1,          depth=0.0,          ori=0
        )

        self.message = visual.TextStim(
            win=self.window,    name='message',text='',
            font='Courier New', pos=(0, 0),         height=0.25,
            wrapWidth=None,     color=(-1,-1,-1),   colorSpace='rgb',
            opacity=1,          depth=0.0,          ori=0
        )

        # self.text_left.autoDraw  = True
        # self.text_right.autoDraw = True

    def load_trials(self):
        trials_file = u'{}{}data{}trials.json'.format(
            self.pwd, os.sep, os.sep
        )

        trials_file = open(trials_file, 'r')
        self.trials = json.load(trials_file, encoding='utf-8')['sentences']
        trials_file.close()

        first_row = self.participant_id % 20
        last_row = (first_row + 5) % 20
        if first_row <= 15:
            square = self.latin_square[first_row:first_row+5]
        else:
            square = self.latin_square[first_row:] + self.latin_square[:last_row]

        square = [int(x) for x in chain.from_iterable(square)]

        for trial in self.trials:
            trial_num = int(trial['sentence_number']) - 1
            if square[trial_num] % 4 == 0:
                trial['condition'] = 1
            elif (square[trial_num] - 1) % 4 == 0:
                trial['condition'] = 2
            elif (square[trial_num] - 2) % 4 == 0:
                trial['condition'] = 3
            else:
                trial['condition'] = 4

    def load_latin_square(self):
        square_file = u'{}{}data{}latinsquare.txt'.format(
            self.pwd, os.sep, os.sep
        )

        square_file = open(square_file, 'r')

        self.latin_square = []
        for line in square_file:
            line = line.strip()
            self.latin_square.append(line.split('\t'))
            # print(self.latin_square[-1])

        square_file.close()

    def display_message(self, message, time=None, keypress=None, color=None):
        self.message.text = message
        self.message.color = (-1, -1, -1) if color is None else color
        self.message.draw()
        self.window.flip()

        if time is not None:
            frames = int(round(time / self.frame_dur))-1
            for i in range(frames):
                self.message.draw()
                self.window.flip()
                if keypress is not None:
                    keys = event.getKeys(keyList=keypress)
                    if len(keys) > 0:
                        return keys
        else:
            if keypress is not None:
                return event.waitKeys(keyList=keypress)

    def prepare_block(self):
        pass
