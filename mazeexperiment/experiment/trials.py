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

from .srbox import SRBox

TEXT_GET_READY = u'请准备'
TEXT_FEEDBACK_CORRECT = u'正确！'
TEXT_FEEDBACK_INCORRECT = u'错误！'

SPEED_MULTIPLIER = 1.0

class SentenceBlock():
    def __init__(self, parent, experiment, exp_info, sentence_list, autorun=False):
        logging.debug(u'Entered SentenceBlock()')

        self.exp_info = exp_info
        self.sentence_list = sentence_list
        self.experiment = experiment
        self.parent = parent
        self.autorun = autorun

        if self.autorun:
            logging.warning(u'EXPERIMENT IN AUTORUN MODE DO NOT USE DATA')
            logging.data(u'EXPERIMENT IN AUTORUN MODE DO NOT USE DATA')
            logging.exp(u'EXPERIMENT IN AUTORUN MODE DO NOT USE DATA')

        self.window = self.parent.window
        self.use_srbox = self.parent.use_srbox
        if self.use_srbox:
            self.srbox = self.parent.srbox

        self.block_clock = core.Clock()

        self.sentences = data.TrialHandler(
            nReps=1, method='random', extraInfo=self.exp_info,
            originPath=-1, trialList=sentence_list,
            seed=None, name='sentence_block',
            dataTypes=['block.acc', 'block.RT', 'frame_rate', 'pretrial_fixation']
        )

        self.experiment.addLoop(self.sentences)

        self.conditions = {
            1: 'both_sim',
            2: 'orth_sim',
            3: 'phon_sim',
            4: 'both_dif'
        }
        self.begin_block()
        logging.flush()

    def begin_block(self):
        logging.debug(u'Entered SentenceBlock().begin_block()')

        self.parent.display_message(TEXT_GET_READY, time=3*SPEED_MULTIPLIER)
        for sentence in self.sentences:
            sentence = self.prepare_trial(sentence)
            block_frame_rate = self.window.getActualFrameRate()
            sentence_trial = SentenceTrial(
                self.parent, self.experiment, self.exp_info,
                sentence['target_sentence'], sentence['alt_sentence'],
                self.autorun
            )
            sentence_acc, sentence_time, fixation_length = sentence_trial.begin_trial()
            logging.flush()

            self.sentences.addData('frame_rate', block_frame_rate)
            self.sentences.addData('block.acc', sentence_acc)
            self.sentences.addData('block.RT', '{:.2f}'.format(sentence_time * 1000))
            self.sentences.addData('pretrial_fixation', '{:.2f}'.format(fixation_length * 1000))
            self.parent.experiment.nextEntry()

        self.experiment.loopEnded(self.sentences)


    def prepare_trial(self, trial):
        logging.debug(u'Preparing trial for sentence {}, critical target {}'.format(
            trial['sentence_number'], trial['critical_target']
        ))

        trial['critical_distractor'] = trial['distractors'][self.conditions[trial['condition']]]

        logging.exp(u'Set critical distractor to: {}'.format(trial['critical_distractor']))
        trial['target_sentence'], trial['alt_sentence'], trial['critical_index'] = self.process_sentence(trial['sentence'], trial['critical_distractor'])

        del trial['sentence']
        del trial['distractors']
        if 'original_distractors' in trial:
            del trial['original_distractors']

        if self.autorun:
            trial['AUTORUN_DATA'] = u'EXPERIMENT IN AUTORUN MODE DO NOT USE DATA'

        return trial

    def process_sentence(self, sentence_pairs, distractor):
        target = []
        alternative = []
        critical_index = 0
        count = 0
        for pair in sentence_pairs:
            if u'＃' in pair[1]:
                target.append(pair[0])
                alternative.append(distractor)
                critical_index = count
            elif pair[1] == u'*':
                    target[-1] = u'{}{}'.format(target[-1], pair[0])
                    alternative[-1] = u'{}{}'.format(alternative[-1], pair[0])
            else:
                target.append(pair[0])
                alternative.append(pair[1])

            count += 1

        return u' | '.join(target), u' | '.join(alternative), critical_index

class SentenceTrial():
    def __init__(self, parent, experiment, exp_info, target_sentence, alternative_sentence, autorun=False):
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
        self.autorun = autorun

        if self.autorun:
            logging.warning(u'EXPERIMENT IN AUTORUN MODE DO NOT USE DATA')
            logging.data(u'EXPERIMENT IN AUTORUN MODE DO NOT USE DATA')
            logging.exp(u'EXPERIMENT IN AUTORUN MODE DO NOT USE DATA')

        self.window = self.parent.window
        self.text_left = self.parent.text_left
        self.text_right = self.parent.text_right
        self.acc_feedback = self.parent.acc_feedback

        self.use_srbox = self.parent.use_srbox
        if self.use_srbox:
            self.srbox = self.parent.srbox

        self.trial_clock = core.Clock()
        self.pair_clock = core.Clock()

        self.trial = data.TrialHandler(
            nReps=1, method='sequential', extraInfo=self.exp_info,
            trialList=self.sentence, name='sentence_trial',
            dataTypes=[
                'pair_correct', 'pair_distractor',
                'target_pos', 'target_pos.verbose',
                'resp', 'resp.acc', 'resp.RT', 'resp.verbose',
                'prev_pos', 'prev_resp'
            ]
        )

        self.experiment.addLoop(self.trial)

        # self.begin_trial()

    def begin_trial(self):
        logging.debug(u'Entered SentenceTrial().begin_trial()')

        self.text_left.text = ''
        self.text_right.text = ''

        logging.info(u'{}: Reset text'.format(self.text_left.name))
        logging.info(u'{}: Reset text'.format(self.text_right.name))

        self.show_blank(.5*SPEED_MULTIPLIER)
        fixation_length = (1 + 2*random()) * SPEED_MULTIPLIER
        self.show_fixation(fixation_length)

        sentence_correct = True

        prev_pos = ''
        prev_resp = ''
        logging.exp(u'trial_clock: Reset time')
        self.trial_clock.reset()
        for pair in self.trial:
            self.show_fixation(0.2*SPEED_MULTIPLIER)

            target_pos = self.show_pair(pair)

            logging.exp(u'pair_clock: Reset time')
            self.pair_clock.reset()

            acc, response_time, response = self.get_response(target_pos)
            self.clear_pair()

            self.trial.addData('target_pos', target_pos)
            if target_pos == 0:
                self.trial.addData('target_pos.verbose', 'L')
            else:
                self.trial.addData('target_pos.verbose', 'R')

            self.trial.addData('resp', response)
            if response == 0:
                self.trial.addData('resp.verbose', 'L')
            else:
                self.trial.addData('resp.verbose', 'R')

            self.trial.addData('resp.RT', '{:.2f}'.format(response_time * 1000))
            self.trial.addData('resp.acc', acc)

            self.trial.addData('prev.pos', prev_pos)
            self.trial.addData('prev.resp', prev_resp)

            if self.autorun:
                self.trial.addData('TRIAL_AUTORUN', u'EXPERIMENT IN AUTORUN MODE DO NOT USE DATA')

            prev_pos = target_pos
            prev_resp = response

            self.parent.experiment.nextEntry()

            if acc == 0:
                logging.exp(u'Incorrect sentence path chosen')
                sentence_correct = False
                break
        block_time = self.trial_clock.getTime()

        self.show_feedback(sentence_correct)
        self.experiment.loopEnded(self.trial)

        if sentence_correct:
            logging.info(u'Sentence completed accurately.')
            logging.data(u'Block completion time: {}'.format(block_time))
            logging.data(u'Block accuracy: {}'.format(1))
            return 1, block_time, fixation_length
        else:
            logging.info(u'Sentence was not completed accurately.')
            logging.data(u'Block completion time: {}'.format(block_time))
            logging.data(u'Block accuracy: {}'.format(0))
            return 0, block_time, fixation_length

    def show_pair(self, pair):
        target_pos = randint(0,2)
        logging.exp(u'Pair target position: {}'.format(target_pos))
        if target_pos == 0:
            self.text_left.text = u'' + pair['pair_correct']
            # self.text_left.color = (-1, -0.50, -1)
            self.text_right.text = u'' + pair['pair_distractor']
            # self.text_right.color = (-1, -1, -1)
        else:
            self.text_left.text = u'' + pair['pair_distractor']
            # self.text_left.color = (-1, -1, -1)
            self.text_right.text = u'' + pair['pair_correct']
            # self.text_right.color = (-1, -0.50, -1)

        logging.info(u'{}: Set text to "{}"'.format(self.text_left.name, self.text_left.text))
        logging.info(u'{}: Set text to "{}"'.format(self.text_right.name, self.text_right.text))

        self.text_left.draw()
        self.text_right.draw()

        self.window.logOnFlip(u'{}: Display text "{}"'.format(self.text_left.name, self.text_left.text), logging.EXP)
        self.window.logOnFlip(u'{}: Display text "{}"'.format(self.text_right.name, self.text_right.text), logging.EXP)
        self.flip()

        return target_pos

    def show_feedback(self, accuracy):
        if not accuracy:
            self.acc_feedback.text = TEXT_FEEDBACK_INCORRECT
            self.acc_feedback.color = (-0.25, -0.25, -0.25)
        else:
            self.acc_feedback.text = TEXT_FEEDBACK_CORRECT
            self.acc_feedback.color = (-1, 1, -1)

        logging.info(u'{}: Set feedback to "{}"'.format(self.acc_feedback.name, self.acc_feedback.text))
        self.window.logOnFlip(u'{}: Display feedback "{}"'.format(self.acc_feedback.name, self.acc_feedback.text), logging.EXP)

        for i in range(1+int(89*SPEED_MULTIPLIER)):
            self.acc_feedback.draw()
            self.flip()

        self.window.logOnFlip(u'{}: Hide feedback "{}"'.format(self.acc_feedback.name, self.acc_feedback.text), logging.EXP)

    def clear_pair(self):
        self.text_left.text = ''
        self.text_right.text = ''

        logging.info(u'{}: Reset text'.format(self.text_left.name))
        logging.info(u'{}: Reset text'.format(self.text_right.name))

        self.text_left.color = (-1, -1, -1)
        self.text_right.color = (-1, -1, -1)

        self.text_left.draw()
        self.text_right.draw()

        self.window.logOnFlip(u'{}: Display text "{}"'.format(self.text_left.name, self.text_left.text), logging.EXP)
        self.window.logOnFlip(u'{}: Display text "{}"'.format(self.text_right.name, self.text_right.text), logging.EXP)
        self.flip()

    def get_response(self, target_pos):
        logging.exp(u'Waiting for response...')

        if self.autorun:
            logging.exp(u'Autorun active. Sending automatic response...')
            auto_response_time = 0.5 + random()
            if randint(0,100) < 98:
                return 1, auto_response_time, target_pos
            else:
                return 0, auto_response_time, int(not target_pos)

        if self.use_srbox:
            response, response_time = self.srbox.waitKeys(keyList=[1, 5], timeStamped=self.pair_clock)
            response = response[0]
        else:
            response, response_time = event.waitKeys(keyList=['c', 'm'], timeStamped=self.pair_clock)[0]
        logging.exp(u'Key presses received')
        # response_time = self.pair_clock.getTime()

        if response in ('c', 1):
            response = 0
        elif response in ('m', 5):
            response = 1

        logging.exp(u'Kepress position: {}'.format(response))

        if response == target_pos:
            logging.info(u'Kepress does match target position.')
            logging.data(u'Response: {}'.format(response))
            logging.data(u'Acc: {}'.format(1))
            logging.data(u'Response time: {}'.format(response_time))
            return 1, response_time, response
        else:
            logging.info(u'Kepress does match target position.')
            logging.data(u'Response: {}'.format(response))
            logging.data(u'Acc: {}'.format(0))
            logging.data(u'Response time: {}'.format(response_time))
            return 0, response_time, response

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

    def flip(self):
        self.check_abort()
        self.window.flip()

    def check_abort(self):
        keys = event.getKeys(keyList=['escape'], modifiers=True)
        if keys and (keys[0][0] == 'escape' and keys[0][1]['ctrl'] and keys[0][1]['alt']):
            self.experiment.saveAsWideText('{}.csv'.format(self.parent.data_file_stem))
            logging.flush()
            # make sure everything is closed down
            self.experiment.abort()
            self.window.close()
            core.quit()
