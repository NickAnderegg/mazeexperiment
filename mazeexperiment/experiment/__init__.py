#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
from psychopy import locale_setup, visual, core, data, event, logging, info, sound, gui
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
from .practicetrials import PracticeBlock

__version__ = "1.0.0"

class Experiment():
    def __init__(self, exp_name=None, pwd=None, use_srbox=False):

        if pwd is None:
            self.pwd = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
        else:
            self.pwd = pwd
        os.chdir(self.pwd)
        self.exp_name = u'untitled' if exp_name is None else exp_name

        data_dir = u'{}{}{}{}'.format(
            self.pwd, os.sep,
            u'participant_data',
            os.sep
        )

        data_file_base = u'{}_'.format(self.exp_name)
        existing = []
        for dirname, dirnames, filenames in os.walk(data_dir):
            for filename in filenames:
                if data_file_base in filename and filename.endswith('.csv'):
                    filename = filename.split('_')
                    participant = int(filename[1])

                    existing.append(participant)

        existing_low = sorted([x for x in existing if x < 500])
        if not existing:
            participant_suggestion = 101
        else:
            participant_suggestion = existing_low[-1] + 1


        exp_suggestions = {
            u'participant': u''+str(participant_suggestion),
            u'version': u'{}'.format(__version__)
        }

        continue_dlg = True
        dlg_title = self.exp_name
        last_attempt = int(exp_suggestions['participant'])
        while continue_dlg:
            dlg = gui.DlgFromDict(
                dictionary=exp_suggestions,
                title=dlg_title,
                fixed=[u'version']
            )

            if dlg.OK == False:
                core.quit()
            else:
                part = int(exp_suggestions['participant'])
                if part in existing and part != last_attempt:
                    last_attempt = part
                    while part in existing:
                        part += 1
                    exp_suggestions['participant'] = part
                    dlg_title = u'Participant {:0>3} Already Exists! ({})'.format(last_attempt, self.exp_name)
                else:
                    continue_dlg = False

        self.exp_info = exp_suggestions


        # self.get_session_info()

        self.window = visual.Window(
            size=(1440/2, 900/2), fullscr=False, screen=0,
            allowGUI=True, allowStencil=False,
            monitor=u'testMonitor', color=[1,1,1], colorSpace='rgb',
            blendMode='avg', useFBO=True, winType='pyglet')

        runtime = info.RunTimeInfo(version=self.exp_info['version'], win=self.window)

        self.exp_info['exp_name'] = self.exp_name
        self.exp_info['date'] = datetime.today().strftime('%Y-%m-%d')
        self.exp_info['session_start'] = datetime.today().strftime('%H:%M:%S')

        self.exp_info['psychopy_version'] = runtime['psychopyVersion']
        self.exp_info['hostname'] = runtime['systemHostName']
        self.exp_info['platform'] = runtime['systemPlatform']
        self.exp_info['proc_count'] = runtime['systemUserProcCount']
        self.exp_info['window_type'] = runtime['windowWinType']
        self.exp_info['window_size'] = runtime['windowSize_pix']

        self.exp_info['all_runtime'] = dict(runtime)

        self.participant_id = int(self.exp_info['participant'])

        if 'darwin' in self.exp_info['platform'] or 'linux' in self.exp_info['platform']:
            self.use_srbox = False
            print('Not using SRBOX')
        else:
            self.use_srbox = use_srbox
            if self.use_srbox:
                self.srbox = SRBox('COM4', 19200, 0)
                self.srbox.set_lights([1,1,1,1,1], update=True)
                core.wait(0.5)
                self.srbox.set_lights([0,0,0,0,0], update=True)

        data_file_stem = u'{}_{}_{}'.format(
            self.exp_name,
            self.exp_info['participant'],
            datetime.today().strftime('%Y-%m-%d')
        )
        # data file name stem
        if int(self.exp_info['participant']) > 500:
            data_file_stem = u'TESTFILE' + data_file_stem

        self.data_file_stem = u'{}{}{}{}{}'.format(
            self.pwd, os.sep,
            u'participant_data', os.sep,
            data_file_stem
        )
        # print(self.data_file_stem)


        self.experiment = data.ExperimentHandler(
            name = self.exp_name,
            version = self.exp_info['version'],
            extraInfo = self.exp_info,
            originPath = None,
            savePickle = True,
            saveWideText = True,
            dataFileName = self.data_file_stem
        )

        self.log_file = logging.LogFile('{}.log'.format(self.data_file_stem), level=logging.DEBUG, encoding='utf-8')
        logging.console.setLevel(logging.CRITICAL)

        self.end_exp_now = False

        self.frame_rate = self.window.getActualFrameRate()

        if self.frame_rate != None:
            self.frame_dur = 1.0 / round(self.frame_rate)
        else:
            self.frame_dur = 1.0 / 60.0  # could not measure, so guess

        self.global_clock    = core.Clock()
        # self.instr_clock    = core.Clock()
        self.sentence_clock = core.Clock()
        self.pair_clock     = core.Clock()

        self.routine_timer  = core.CountdownTimer()
        logging.flush()

        instructions = Instructions(self, self.exp_info)
        instructions.begin_instructions()

        self.prepare_visuals()
        self.load_latin_square()
        self.load_trials()
        self.load_practice_trials()

        practice_block = PracticeBlock(self, self.experiment, self.exp_info, self.practice_trials)

        sentence_block = SentenceBlock(self, self.experiment, self.exp_info, self.trials)

        logging.flush()

    def abort(self):
        self.experiment.saveAsWideText('{}.csv'.format(self.data_file_stem))
        logging.flush()
        # make sure everything is closed down
        try:
            self.experiment.abort()  # or data files will save again on exit
        except: pass
        try:
            self.window.close()
        except: pass
        try:
            core.quit()
        except: pass

    def check_abort(self):
        keys = event.getKeys(keyList=['escape'], modifiers=True)
        if keys and (keys[0][0] == 'escape' and keys[0][1]['ctrl'] and keys[0][1]['alt']):
            try:
                self.abort()
            except:
                pass

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

        if 'darwin' in self.exp_info['platform']:
            CHINESE_FONT = 'STFangSong'
        elif 'win' in self.exp_info['platform']:
            CHINESE_FONT = 'FangSong'

        self.text_left = visual.TextStim(
            win=self.window,    name='text_left',   text='',
            font=CHINESE_FONT,   pos=(-0.1, 0),      height=0.25,
            wrapWidth=None,     color=(-1, -1, -1), colorSpace='rgb',
            opacity=1,          depth=0.0,          ori=0,
            alignHoriz='right', autoLog=False
        )

        self.text_right = visual.TextStim(
            win=self.window,    name='text_right',  text='',
            font=CHINESE_FONT,   pos=(0.1, 0),       height=0.25,
            wrapWidth=None,     color=(-1, -1, -1), colorSpace='rgb',
            opacity=1,          depth=0.0,          ori=0,
            alignHoriz='left', autoLog=False
        )

        self.fixation = visual.TextStim(
            win=self.window,    name='fixation',    text='+',
            font='Courier New', pos=(0, 0),         height=0.25,
            wrapWidth=None,     color=(-1, -1, -1), colorSpace='rgb',
            opacity=1,          depth=0.0,          ori=0,
            autoLog=False
        )

        self.acc_feedback = visual.TextStim(
            win=self.window,    name='acc_feedback',text='',
            font=CHINESE_FONT, pos=(0, 0),         height=0.25,
            wrapWidth=None,     color=(-1,-1,-1),   colorSpace='rgb',
            opacity=1,          depth=0.0,          ori=0,
            autoLog=False
        )

        self.message = visual.TextStim(
            win=self.window,    name='message',text='',
            font=CHINESE_FONT, pos=(0, 0),         height=0.25,
            wrapWidth=None,     color=(-1,-1,-1),   colorSpace='rgb',
            opacity=1,          depth=0.0,          ori=0,
            autoLog=False
        )

        # self.text_left.autoDraw  = True
        # self.text_right.autoDraw = True

    def load_practice_trials(self):
        practice_file = u'{}{}data{}practice_trials.json'.format(
            self.pwd, os.sep, os.sep
        )

        practice_file = open(practice_file, 'r')
        self.practice_trials = json.load(practice_file, encoding='utf-8')['sentences']
        practice_file.close()

        logging.info(u'Practice trials loaded')
        logging.flush()

    def load_trials(self):
        trials_file = u'{}{}data{}trials.json'.format(
            self.pwd, os.sep, os.sep
        )

        trials_file = open(trials_file, 'r')
        self.trials = json.load(trials_file, encoding='utf-8')['sentences']
        trials_file.close()

        # print('Participant ID # {}'.format(self.participant_id))
        # print('Participant ID % 23 {}'.format((self.participant_id%46)))
        # print('Participant ID % 100 {}'.format((self.participant_id%100)))

        participant_mod = self.participant_id# % 100

        # print('Participant MOD % 23 {}'.format((participant_mod%23)))

        first_row = self.participant_id % 23
        last_row = (first_row + 5) % 23
        # last_row = (first_row + 4) % 20

        # logging.info(u'Latin square first row: {}, last row: {}'.format(first_row, last_row-1))

        square = []
        # if first_row <= 16:
        #     square = self.latin_square[first_row:first_row+5]
        # else:
        #     square = self.latin_square[first_row:] + self.latin_square[:last_row]

        for i in range(5):
            row_id = ((participant_mod % 46) + (i * (int((participant_mod - 1) / 46) + 1))) % 46
            square.append(self.latin_square[row_id])
            logging.info(u'       {}'.format(''.join(['{:>4}'.format((x+(i*23))) for x in range(1,24)])))
            logging.info(u'Row {:>2}:{}'.format(row_id, ''.join(['{:>4}'.format(x) for x in self.latin_square[row_id]])))

        square = [int(x) for x in chain.from_iterable(square)]
        # print('Square:', square)

        logging.info(u'Participant latin square: {}'.format(square))

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

            # print(trial['sentence_number'], ':', trial['condition'], end=' | ')

        logging.flush()

    def load_latin_square(self):
        square_file = u'{}{}data{}latinsquare_23.txt'.format(
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
        logging.info(u'{}: Set message to "{}"'.format(self.message.name, message))
        self.message.color = (-1, -1, -1) if color is None else color
        self.message.draw()
        self.window.logOnFlip(u'{}: Display message "{}"'.format(self.message.name, message), logging.EXP, self.message)
        self.window.flip()

        if time is not None:
            frames = int(round(time / self.frame_dur))-1
            self.window.logOnFlip(
                'Begin show blank screen for {:.2f} ({} frames/{} actual est.)'.format(time, frames, (frames*self.frame_dur)),
                logging.EXP
            )
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

        self.window.logOnFlip(u'{}: Hide message "{}"'.format(self.message.name, message), logging.EXP, self.message)
