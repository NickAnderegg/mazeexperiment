#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from psychopy import locale_setup, visual, core, data, event, logging#, sound, gui
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)

import numpy as np
from numpy.random import random, randint, normal, shuffle

from datetime import datetime
import time
import os, sys

class PracticeBlock():
    def __init__(self, parent, experiment, exp_info, practice_list):
        logging.debug(u'Entered PracticeBlock()')

        self.exp_info = exp_info
        self.practice_list = practice_list
        self.experiment = experiment
        self.parent = parent

        self.window = self.parent.window

        self.block_clock = core.Clock()

        self.trials = data.TrialHandler(
            nReps=1, method='sequential', extraInfo=self.exp_info,
            originPath=-1, trialList=self.practice_list, name='practice_block'
        )

        self.experiment.addLoop(self.trials)

        self.begin_practice()

    def begin_practice(self):
        logging.debug(u'Entered PracticeBlock().begin_practice()')

        self.parent.display_message('GET READY', time=0.5)#3)

        for trial in self.trials:
            practice_trial = PracticeTrial(
                self.parent, self.experiment, self.exp_info, trial
            )
            trial_pairs = dict(trial)

            failed_trial = practice_trial.begin_trial()

            while not failed_trial:
                trial = dict(trial_pairs)

                self.parent.display_message('GET READY', time=0.5)#3)

                practice_trial = PracticeTrial(
                    self.parent, self.experiment, self.exp_info, trial
                )
                failed_trial = practice_trial.begin_trial()

class PracticeTrial():
    def __init__(self, parent, experiment, exp_info, trial):
        self.exp_info = exp_info
        self.trial_num = trial['sentence_number']
        self.sentence = []
        for pair in trial['sentence']:
            self.sentence.append({
                'pair_correct': pair[0],
                'pair_distractor': pair[1]
            })

        self.experiment = experiment
        self.parent = parent

        self.window = self.parent.window
        self.text_left = self.parent.text_left
        self.text_right = self.parent.text_right
        self.acc_feedback = self.parent.acc_feedback

        self.sentence_progress = visual.TextStim(
            win=self.window,    name='message', text='',
            font='Songti SC', pos=(-0.9, 0.75),         height=0.10,
            wrapWidth=1.8,     color=(-1,-1,-1),   colorSpace='rgb',
            opacity=1,          depth=0.0,          ori=0,
            autoLog=False, alignHoriz='left'
        )
        self.progress_list = []

        self.trial_clock = core.Clock()
        self.pair_clock = core.Clock()

        self.trial = data.TrialHandler(
            nReps=1, method='sequential', extraInfo=self.exp_info,
            trialList=self.sentence, name='sentence_trial'
        )
        self.experiment.addLoop(self.trial)

    def begin_trial(self):
        logging.debug(u'Entered PracticeTrial().begin_trial()')

        # self.text_left.text = ''
        # self.text_right.text = ''

        self.clear_pair()
        self.reset_displays()

        # self.show_blank(.5)
        fixation_length = 2 + 3*random()
        self.show_fixation(0.5)

        sentence_correct = True

        prev_pos = ''
        prev_resp = ''
        self.trial_clock.reset()
        for pair in self.trial:

            target_pos = randint(0,2)

            acc = 0
            while acc == 0:
                self.show_fixation(0.2)
                self.show_pair(pair, target_pos)
                self.pair_clock.reset()
                acc, response_time, response = self.get_response(target_pos)

                self.show_trial_feedback(acc, target_pos)

                if not acc and self.trial_num >= 7:
                    self.clear_pair()
                    self.reset_displays()

                    self.window.color = (1, -1, -1)
                    self.parent.display_message('INCORRECT!', time=2)
                    self.window.color = (1, 1, 1)

                    return False

            self.clear_pair()
            self.update_progress(pair['pair_correct'])

            self.parent.experiment.nextEntry()

        self.window.color = (-1, 1, -1)
        self.parent.display_message('CORRECT!', time=2)
        self.window.color = (1, 1, 1)

        self.reset_displays()

        return True

    def show_trial_feedback(self, accuracy, target_pos):
        if not accuracy:
            self.window.color = (0.25, -1, -1)
            if target_pos == 0:
                correct_text = self.text_left
                distractor_text = self.text_right
            else:
                correct_text = self.text_right
                distractor_text = self.text_left

            if self.trial_num <= 5:
                correct_text.color = (-1, -1, -1)
                distractor_text.color = (-0.5, -1, -1)

            distractor_text.autoDraw = True
            correct_text.autoDraw = True

            self.sentence_progress.height = 0.2
            self.sentence_progress.pos = (0, 0.5)
            self.sentence_progress.alignHoriz = 'center'

            for i in range(5):
                if self.trial_num <= 5:
                    # correct_text.height = 0.35
                    correct_text.bold = True
                    self.flip(15)
                    # correct_text.height = 0.25
                    correct_text.bold = False
                self.flip(15)

            # distractor_text.opacity = 1.0

            correct_text.autoDraw = False
            distractor_text.autoDraw = False
            self.window.color = (1, 1, 1)
            correct_text.draw()
            distractor_text.draw()
            self.flip()

    def reset_displays(self):
        self.text_left.color = (-1, -1, -1)
        self.text_right.color = (-1, -1, -1)

        self.text_left.opacity = 1.0
        self.text_right.opacity = 1.0

        self.text_left.draw()
        self.text_right.draw()

        self.sentence_progress.autoDraw = False
        self.sentence_progress.draw()

        self.flip()

    def show_pair(self, pair, target_pos):
        if target_pos == 0:
            correct_text = self.text_left
            distractor_text = self.text_right
        else:
            correct_text = self.text_right
            distractor_text = self.text_left

        # if target_pos == 0:
        correct_text.text = u'' + pair['pair_correct']
        distractor_text.text = u'' + pair['pair_distractor']

        if self.trial_num <= 2:
            correct_text.color = (-1, 0.5, -1)
            distractor_text.color = (-1, -1, -1)

        if self.trial_num <= 4:
            correct_text.height = 0.25
            distractor_text.height = 0.2

            correct_text.opacity = 1.0
            distractor_text.opacity = 0.7

        if self.trial_num <= 6:
            correct_text.opacity = 1.0
            distractor_text.opacity = 0.9

        self.text_left.draw()
        self.text_right.draw()
        self.flip()

    def clear_pair(self):
        self.text_left.text = ''
        self.text_right.text = ''

        self.text_left.color = (-1, -1, -1)
        self.text_right.color = (-1, -1, -1)

        self.text_left.opacity = 1.0
        self.text_right.opacity = 1.0

        self.text_left.height = 0.25
        self.text_right.height = 0.25

        self.text_left.draw()
        self.text_right.draw()

        self.sentence_progress.text = ''
        self.sentence_progress.size = 0.1
        self.sentence_progress.pos = (-0.9, 0.75)
        self.sentence_progress.height = 0.10
        self.sentence_progress.alignHoriz = 'left'
        self.sentence_progress.draw()

        self.flip()

    def update_progress(self, word):
        if self.trial_num >= 8:
            return

        self.progress_list.append(word)

        if self.trial_num >= 5:
            if len(self.progress_list) > 3:
                self.progress_list[-4] = u'\u3000' * len(self.progress_list[-4])
        self.sentence_progress.text = u' '.join(self.progress_list)
        # self.sentence_progress.text = u'{}{}'.format(
        #     self.sentence_progress.text, word
        # )
        self.sentence_progress.height = 0.1
        self.sentence_progress.draw()
        self.sentence_progress.autoDraw = True
        self.flip()

    def get_response(self, target_pos):
        response, response_time = event.waitKeys(keyList=['c', 'm'], timeStamped=self.pair_clock)[0]

        if response == 'c':
            response = 0
        elif response == 'm':
            response = 1

        if response == target_pos:
            return 1, response_time, response
        else:
            return 0, response_time, response

    def flip(self, count=1):
        # self.sentence_progress.draw()
        for i in range(count):
            self.window.flip()

    def show_fixation(self, time):
        frames = int(round(time / self.parent.frame_dur))
        self.window.logOnFlip(
            'Begin show fixation for {:.2f} ({} frames/{} actual est.)'.format(time, frames, (frames*self.parent.frame_dur)),
            logging.EXP
        )
        for i in range(frames):
            self.parent.fixation.draw()
            self.flip()

        self.window.logOnFlip(u'End show fixation', logging.EXP)

    def show_blank(self, time):
        frames = int(round(time / self.parent.frame_dur))
        self.window.logOnFlip(
            'Begin show blank screen for {:.2f} ({} frames/{} actual est.)'.format(time, frames, (frames*self.parent.frame_dur)),
            logging.EXP
        )
        for i in range(frames):
            self.flip()

        self.window.logOnFlip(u'End show blank screen', logging.EXP)
