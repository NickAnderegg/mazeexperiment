#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
from psychopy import locale_setup, gui, visual, core, data, event, logging, sound
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)

import numpy as np
from numpy.random import random, randint, normal, shuffle

from datetime import datetime
import os, sys

__version__ = "1.0.0"

class Experiment():
    def __init__(self, exp_name=None):
        self.pwd = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
        os.chdir(self.pwd)

        self.exp_name = u'untitled' if exp_name is None else exp_name
        self.exp_info = {
            u'session': u'001',
            u'participant': u'',
            u'version': u'{}'.format(__version__)
        }

        self.get_session_info()

        self.exp_info['exp_name'] = self.exp_name
        self.exp_info['date'] = datetime.today().strftime('%Y-%m-%d')
        self.exp_info['session_start'] = datetime.today().strftime('%H:%M:%S')

        # data file name stem
        self.data_file_stem = u'{}{}{}{}{}_{}_{}_{}'.format(
            self.pwd, os.sep,
            u'data', os.sep,
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
            savePickle = True,
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
            frameDur = 1.0 / round(self.exp_info['frameRate'])
        else:
            frameDur = 1.0 / 60.0  # could not measure, so guess

        self.globalClock    = core.Clock()
        self.instr_clock    = core.Clock()
        self.sentence_clock = core.Clock()
        self.pair_clock     = core.Clock()

        self.routine_timer  = core.CountdownTimer()

        self.text_left  = visual.TextStim(
            win=self.window,    name='text_left',   text='',
            font='Songti SC',   pos=(-0.5, 0),      height=0.25,
            wrapWidth=None,     color=(-1, -1, -1), colorSpace='rgb',
            opacity=1,          depth=0.0,          ori=0
        )

        self.right_left  = visual.TextStim(
            win=self.window,    name='text_right',   text='',
            font='Songti SC',   pos=(0.5, 0),      height=0.25,
            wrapWidth=None,     color=(-1, -1, -1), colorSpace='rgb',
            opacity=1,          depth=0.0,          ori=0
        )

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
