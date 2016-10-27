#-*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from psychopy import locale_setup, gui, visual, core, data, event, logging, sound
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)

import numpy as np
from numpy.random import random, randint, normal, shuffle

import datetime
import os,sys

class Experiment():
    def __init__(self):
        self.clock = core.MonotonicClock()
        self.window = visual.Window(color=(1, 1, 1), fullscr=False)
        self.handler = data.ExperimentHandler(
            name='Orthophonology',
            version='1.0.0',
            extraInfo= {
                'subject': 1,
                'date': datetime.datetime.today().date(),
                'experiment_start': datetime.datetime.today().time().strftime("%H:%M:%S")
            }
        )
        other_clock = core.Clock()

        # self.maze = [
        #     (u'这种', u'ＸＸ'),
        #     (u'人', u'的'),
        #     (u'用', u'休'),
        #     (u'这种', u'重伤'),
        #     (u'方法', u'国际'),
        #     (u'治,', u'＃,'),
        #     (u'可谓', u'数组'),
        #     (u'是', u'扮'),
        #     (u'以毒攻毒.', u'男男女女.')
        # ]

        # self.maze = [
        #     (u'The', u'XXX'),
        #     (u'boy', u'for'),
        #     (u'ran', u'bed'),
        #     (u'for', u'car'),
        #     (u'three', u'jumps'),
        #     (u'miles', u'pounds'),
        #     (u'after', u'orange'),
        #     (u'school', u'shelf'),
        #     (u'because', u'clock'),
        #     (u'he', u'to'),
        #     (u'was', u'pen'),
        #     (u'full', u'door'),
        #     (u'of', u'at'),
        #     (u'energy.', u'couch.')
        # ]

        self.trials = [
            {
                'target_sentence': [
                    u'The', u'boy', u'ran', u'for', u'three', u'miles', u'after',
                    u'school', u'because', u'he', u'was', u'full', u'of', u'energy.'
                ],
                'alternative_sentence': [
                    u'XXX', u'for', u'bed', u'car', u'jumps', u'pounds', u'orange',
                    u'shelf', u'clock', u'to', u'pen', u'door', u'at', u'couch.'
                ]
            },
            {
                'target_sentence': [
                    u'The', u'quick', u'brown', u'fox',
                    u'jumps', u'over', u'the', u'lazy', u'dog.'
                ],
                'alternative_sentence': [
                    u'XXX', u'NOT', u'NOT', u'NOT', u'NOT', u'NOT', u'NOT', u'NOT',u'NOT.'
                ]
            }
        ]
        # self.trials = [{'test': 'something', 'other': 'something'}]
        # self.trials = [self.maze]
        # print(self.trials)

        trial_handler = data.TrialHandler(
            trialList=self.trials,
            nReps=1,
            method='random',
            dataTypes=[
                'target_sentence', 'alternative_sentence', 'trial_start'
            ]
        )
        trial_handler.setExp(self.handler)
        # self.handler.addLoop(self.trial_handler)
        # self.trial_handler.setExp(self.handler)

        self.t1 = visual.TextStim(self.window, text='', font='Songti SC', pos=(-0.5, 0), height=0.25, color=(-1, -1, -1))
        self.t2 = visual.TextStim(self.window, text='', font='Songti SC', pos=(0.5, 0), height=0.25, color=(-1, -1, -1))

        self.fixation = visual.TextStim(self.window, text='+', font='Courier New', pos=(0, 0), height=0.25, color=(-1, -1, -1))
        self.message = visual.TextStim(self.window, text='', font='Courier New', pos=(0, 0), height=0.25, color=(-1,-1,-1))
        self.t1.autoDraw = True
        self.t2.autoDraw = True
        # self.t1.draw()
        # self.t2.draw()

        # current_trial = self.trial_handler.next()
        # self.begin_trial()
        self.handler.addLoop(trial_handler)
        for trial in trial_handler:
            trial_handler.addData('trial_start', datetime.datetime.today().time())
            zipped_pairs = zip(trial['target_sentence'], trial['alternative_sentence'])
            trial_pairs = []
            for pair in zipped_pairs:
                trial_pairs.append({
                    'target': pair[0],
                    'distractor': pair[1],
                    'target_pos': random.randint(0,1)
                })

            sentence_handler = data.TrialHandler(
                trialList=trial_pairs,
                nReps=1,
                method='sequential',
                dataTypes= [
                    'target', 'distractor', 'target_pos','resp', 'resp.RT', 'resp.acc'
                ]
            )
            sentence_handler.setExp(self.handler)
            for i in range(90):
                self.window.flip()
            for i in range(120):
                self.fixation.draw()
                self.window.flip()
            # sentence_handler.setExp(self.handler)
            self.handler.addLoop(sentence_handler)
            sentence_correct = True
            for pair in sentence_handler:
                self.t1.text = ''
                self.t2.text = ''
                for i in range(12):
                    self.fixation.draw()
                    self.window.flip()

                # target_pos = self.display_pair(pair)
                # self.handler.addData('target', pair[0])
                # self.handler.addData('distractor', pair[1])
                # self.handler.addData('target_pos', target_pos)
                # sentence_handler.addData('target', pair['target'])
                # sentence_handler.addData('distractor', pair['distractor'])
                # sentence_handler.addData('target_pos', target_pos)
                self.display_pair((pair['target'], pair['distractor']), pair['target_pos'])

                self.window.flip()
                trial_display = core.MonotonicClock()
                response = event.waitKeys(keyList=['c', 'm'])[0]
                sentence_handler.addData('resp', response)
                sentence_handler.addData('resp.RT', '{:.1f}'.format(trial_display.getTime() * 1000))


                if not self.judge_response(response, pair['target_pos']):
                    self.incorrect_response()
                    sentence_handler.addData('resp.acc', 0)
                    self.handler.nextEntry()
                    sentence_correct = False
                    break
                sentence_handler.addData('resp.acc', 1)
                # self.handler.nextEntry()

                self.handler.nextEntry()

            if sentence_correct:
                self.completed_sentence()


            self.handler.loopEnded(sentence_handler)
            self.handler.nextEntry()

        # self.handler.nextEntry()
        self.handler.loopEnded(trial_handler)
        self.handler.saveAsWideText('test.txt', delim='\t')
        core.wait(3)

    # def begin_trial(self):
    #     self.fixation.draw()
    #     self.window.flip()
    #     core.wait(3)

    def judge_response(self, key, target_pos):
        if target_pos == 0 and key == 'c':
            return True
        elif target_pos == 1 and key =='m':
            return True

        return False

    def display_pair(self, pair, target_pos):
        # target_pos = random.randint(0,1)
        if target_pos == 0:
            self.t1.text = pair[0]
            # self.t1.color = (-1, 1, -1)
            self.t2.text = pair[1]
            # self.t2.color = (-1, -1, -1)
        else:
            self.t1.text = pair[1]
            # self.t1.color = (-1, -1, -1)
            self.t2.text = pair[0]
            # self.t2.color = (-1, 1, -1)

        # return target_pos

    def incorrect_response(self):
        self.message.text = 'INCORRECT'
        self.message.color = (1, -1, -1)
        self.t1.text = ''
        self.t2.text = ''
        for i in range(300):
            self.message.draw()
            self.window.flip()
        # core.wait(5)

    def completed_sentence(self):
        self.message.text = 'GOOD!'
        self.message.color = (-1, 0.75, -1)
        self.t1.text = ''
        self.t2.text = ''
        for i in range(180):
            self.message.draw()
            self.window.flip()
        # core.wait(3)
