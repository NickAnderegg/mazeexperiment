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

class SentenceBlock():
    def __init__(self, parent, experiment, exp_info, sentence_list):
        self.exp_info = exp_info
        self.sentence_list = sentence_list
        self.experiment = experiment
        self.parent = parent

        self.block_clock = core.Clock()

        self.sentences = data.TrialHandler(
            nReps=1, method='random', extraInfo=self.exp_info,
            originPath=-1, trialList=sentence_list,
            seed=None, name='sentence_block',
            dataTypes=['block.acc', 'block.RT']
        )

        self.experiment.addLoop(self.sentences)

        self.conditions = {
            1: 'both_sim',
            2: 'orth_sim',
            3: 'phon_sim',
            4: 'both_dif'
        }
        self.begin_block()

    def begin_block(self):
        self.parent.display_message('GET READY', time=3)
        for sentence in self.sentences:
            sentence = self.prepare_trial(sentence)
            sentence_trial = SentenceTrial(
                self.parent, self.experiment, self.exp_info,
                sentence['target_sentence'], sentence['alt_sentence']
            )
            sentence_acc, sentence_time = sentence_trial.begin_trial()

            self.sentences.addData('block.acc', sentence_acc)
            self.sentences.addData('block.RT', '{:.1f}'.format(sentence_time * 1000))
            self.parent.experiment.nextEntry()

        self.experiment.loopEnded(self.sentences)


    def prepare_trial(self, trial):
        trial['critical_distractor'] = trial['distractors'][self.conditions[trial['condition']]]
        trial['target_sentence'], trial['alt_sentence'] = self.process_sentence(trial['sentence'], trial['critical_distractor'])

        del trial['sentence']
        del trial['distractors']

        return trial

    def process_sentence(self, sentence_pairs, distractor):
        target = []
        alternative = []
        for pair in sentence_pairs:
            if pair[1] == u'＃':
                target.append(pair[0])
                alternative.append(distractor)
            elif pair[1] == u'*':
                    target[-1] = u'{}{}'.format(target[-1], pair[0])
                    alternative[-1] = u'{}{}'.format(alternative[-1], pair[0])
            else:
                target.append(pair[0])
                alternative.append(pair[1])

        return u' | '.join(target), u' | '.join(alternative)

class SentenceTrial():
    def __init__(self, parent, experiment, exp_info, target_sentence, alternative_sentence):
        self.exp_info = exp_info
        zipped_sentence = zip(target_sentence.split(' | '), alternative_sentence.split(' | '))
        self.sentence = []
        for pair in zipped_sentence:
            self.sentence.append({
                'pair_correct': pair[0],
                'pair_distractor': pair[1]
            })

        self.experiment = experiment
        self.parent = parent

        self.trial_clock = core.Clock()
        self.pair_clock = core.Clock()

        self.trial = data.TrialHandler(
            nReps=1, method='sequential', extraInfo=self.exp_info,
            trialList=self.sentence, name='sentence_trial',
            dataTypes=[
                'pair_correct', 'pair_distractor', 'resp', 'resp.acc', 'resp.RT'
            ]
        )

        self.experiment.addLoop(self.trial)

        # self.begin_trial()

    def begin_trial(self):
        self.parent.text_left.text = ''
        self.parent.text_right.text = ''

        self.show_blank(.5)
        fixation_length = 2 + 3*random()
        self.show_fixation(fixation_length)

        sentence_correct = True

        self.trial_clock.reset()
        for pair in self.trial:
            self.show_fixation(0.2)

            target_pos = self.show_pair(pair)
            self.pair_clock.reset()

            acc, response_time, response = self.get_response(target_pos)
            self.clear_pair()

            self.trial.addData('resp', response)
            self.trial.addData('resp.RT', '{:.1f}'.format(response_time * 1000))
            self.trial.addData('resp.acc', acc)
            self.parent.experiment.nextEntry()

            if acc == 0:
                sentence_correct = False
                break
        block_time = self.trial_clock.getTime()

        self.show_feedback(sentence_correct)
        self.experiment.loopEnded(self.trial)

        if sentence_correct:
            return 1, block_time
        else:
            return 0, block_time

    def show_pair(self, pair):
        target_pos = randint(0,2)
        if target_pos == 0:
            self.parent.text_left.text = pair['pair_correct']
            self.parent.text_left.color = (-1, -0.50, -1)
            self.parent.text_right.text = pair['pair_distractor']
            self.parent.text_right.color = (-1, -1, -1)
        else:
            self.parent.text_left.text = pair['pair_distractor']
            self.parent.text_left.color = (-1, -1, -1)
            self.parent.text_right.text = pair['pair_correct']
            self.parent.text_right.color = (-1, -0.50, -1)

        self.parent.text_left.draw()
        self.parent.text_right.draw()
        self.flip()

        return target_pos

    def show_feedback(self, accuracy):
        if not accuracy:
            self.parent.acc_feedback.text = 'INCORRECT'
            self.parent.acc_feedback.color = (-0.25, -0.25, -0.25)
        else:
            self.parent.acc_feedback.text = 'CORRECT'
            self.parent.acc_feedback.color = (-1, 1, -1)

        for i in range(160):
            self.parent.acc_feedback.draw()
            self.flip()

    def clear_pair(self):
        self.parent.text_left.text = ''
        self.parent.text_right.text = ''

        self.parent.text_left.color = (-1, -1, -1)
        self.parent.text_right.color = (-1, -1, -1)

        self.parent.text_left.draw()
        self.parent.text_right.draw()
        self.flip()

    def get_response(self, target_pos):
        response, response_time = event.waitKeys(keyList=['c', 'm'], timeStamped=self.pair_clock)[0]
        # response_time = self.pair_clock.getTime()

        if response == 'c':
            response = 0
        elif response == 'm':
            response = 1

        if response == target_pos:
            return 1, response_time, response
        else:
            return 0, response_time, response

    def show_fixation(self, time):
        frames = int(round(time / self.parent.frame_dur))
        for i in range(frames):
            self.parent.fixation.draw()
            self.flip()

    def show_blank(self, time):
        frames = int(round(time / self.parent.frame_dur))
        for i in range(frames):
            self.flip()

    def flip(self):
        self.parent.window.flip()
