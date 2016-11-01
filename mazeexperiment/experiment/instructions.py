#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from psychopy import locale_setup, visual, core, data, event, logging#, sound, gui
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)

import numpy as np
from numpy.random import random, randint, normal, shuffle

from math import cos, sin

from datetime import datetime
import time
import os, sys

class Instructions():
    def __init__(self, parent, exp_info):
        self.exp_info = exp_info
        self.parent = parent

        self.window = self.parent.window

        self.prepare_visuals()

    def begin_instructions(self):
        self.paragraph.text = u'In this experiment, you will be asked to read sentences in Mandarin. '
        self.paragraph.autoDraw = True
        self.paragraph.alignVert = 'center'
        self.flipper(5)

        self.paragraph.text = (
            u'The words in each sentence will be presented one at a time. Each word ' +
            u'in a sentence will appear beside an unrelated word that does ' +
            u'that does not fit into the sentence.'
        )
        self.flipper(10)

        self.paragraph.text = (
            u'Your task is to choose which word fits best into the sentence. '+
            u'You will do this by pressing the button which corresponds to the side ' +
            u'that the correct word is on.'
        )
        self.flipper(15)

        self.paragraph.text = (
            u'To choose the word that is on the left side of the screen, ' +
            u'press the button that is on the left side of the response box.'
        )
        self.flipper(3)
        draw = True
        for i in range(20):
            self.draw_left_arrow(draw)
            self.flipper(0.25)
            draw = not draw

        self.draw_left_arrow(False)
        self.paragraph.autoDraw = False
        self.flipper(1)

        self.paragraph.autoDraw = True
        self.paragraph.text = (
            u'To choose the word that is on the right side of the screen, ' +
            u'press the button that is on the right side of the response box.'
        )
        self.flipper(3)
        draw = True
        for i in range(20):
            self.draw_right_arrow(draw)
            self.flipper(0.25)
            draw = not draw

        self.draw_right_arrow(False)
        self.flipper(0.5)

        move, frames = self.animated_move([-0.8, 0.0], [-0.8, 0.75], 2)
        for i in range(frames):
            self.paragraph.pos += move
            self.window.flip()

        self.paragraph.autoDraw = False
        self.paragraph.alignVert = 'top'
        self.flipper(0.25)
        self.paragraph.text = (
            u'Before each block of sentences begins, ' +
            u'a message will appear on screen which states "GET READY"'
        )
        self.paragraph.pos= (-0.8, 0.9)
        self.paragraph.autoDraw = True
        self.flipper(3)

        self.message.text = u'GET READY'
        self.message.autoDraw = True
        self.flipper(7.5)

        self.paragraph.autoDraw = False
        self.flipper(0.25)
        self.paragraph.text = (
            u'This will be followed briefly by a blank screen. When a ' +
            u'fixation cross (+) appears on screen, the first sentence is about '+
            u'to begin. Here\'s an example:'
        )
        self.paragraph.autoDraw = True
        self.flipper(10)
        self.paragraph.autoDraw = False
        self.flipper(2)
        self.message.autoDraw = False
        self.flipper(1)
        self.fixation.autoDraw = True
        self.flipper(5)

        self.paragraph.text = (
            u'The first word in each sentence will be presented beside a series of X symbols.'
        )
        self.paragraph.autoDraw = True
        self.flipper(5)

        self.text_left.text = 'XXX'
        self.text_right.text = 'The'
        self.text_left.autoDraw = True
        self.text_right.autoDraw = True
        self.flipper(0.5)

        self.fixation.autoDraw = False
        self.flipper(3)

        self.paragraph.text = (
            u'You have to press the response button which corresponds to the correct word.'
        )

        self.paragraph.autoDraw = True
        self.flipper(3)

        self.paragraph.text = (
            u'Press the button on the right to choose that word.'
        )
        self.paragraph.pos = (-0.9, -0.6)

        draw = True
        for i in range(20):
            self.draw_right_arrow(draw)
            self.flipper(0.25)
            draw = not draw

        self.draw_right_arrow(False)
        self.flipper(0.5)

        self.paragraph.autoDraw = True
        self.paragraph.pos = (-0.8, 0.9)
        self.paragraph.text = (
            u'After you choose a word, both words will be replaced by a fixation cross. ' +
            u'Then, you will see two new words. Only one of these words can come after the ' +
            u'previous word that you chose. Here\'s an example:'
        )
        self.flipper(15)
        self.text_left.autoDraw = False
        self.text_right.autoDraw = False
        self.fixation.autoDraw = True
        self.paragraph.autoDraw = False
        self.flipper(0.5)

        self.fixation.autoDraw = False
        self.text_left.text = 'boy'
        self.text_right.text = 'jumped'
        self.text_left.autoDraw = True
        self.text_right.autoDraw = True

        self.flipper(3)

        self.paragraph.autoDraw = True
        self.paragraph.text = (
            u'Now you should choose the word that is on the left side by pressing ' +
            u'the button on the left. You would choose this because "The boy..." is ' +
            u'correct grammar, while "The jumped..." is not a legal sentence.'
        )
        self.flipper(15)

        self.paragraph.pos = (-0.5, -0.6)
        self.paragraph.text = (
            u'Press the button on the left to choose that word.'
        )

        draw = True
        for i in range(20):
            self.draw_left_arrow(draw)
            self.flipper(0.25)
            draw = not draw

        self.draw_left_arrow(False)
        self.text_left.autoDraw = False
        self.text_right.autoDraw = False
        self.paragraph.autoDraw = False
        self.flipper(1.5)

        self.paragraph.text = (
            u'Good! Now you will see an example of responses to an entire sentence. ' +
            u'Please watch the screen carefully, but do not make any responses.'
        )

        self.paragraph.autoDraw = True
        self.paragraph.pos = (-0.8, 0)
        self.flipper(10)

        example_sentence = [
            [u"这种", u"ＸＸ"],
            [u"人", u"峙"],
            [u"用", u"肩"],
            [u"这种", u"签订"],
            [u"方法", u"温馨"],
            [u"治", u"＃"],
            [u",", u"*"],
            [u"可谓", u"卑鄙"],
            [u"是", u"韦"],
            [u"以毒攻毒", u"无地自容"],
            [u".", u"*"]
        ]
        self.paragraph.autoDraw = False
        self.flipper(2)

        self.message.text = u'GET READY'
        self.message.autoDraw = True
        self.flipper(5)
        self.message.autoDraw = False
        self.flipper(1)
        self.fixation.autoDraw = True
        self.flipper(3)

        for pair in example_sentence:
            target_pos = randint(0,2)

            self.fixation.autoDraw = True
            self.flipper(0.2)
            self.fixation.autoDraw = False

            if target_pos == 0:
                self.text_left.text = pair[0]
                self.text_right.text = pair[1]
            else:
                self.text_left.text = pair[1]
                self.text_right.text = pair[0]

            self.text_left.autoDraw = True
            self.text_right.autoDraw = True
            self.flipper(randint(15,25)/20)

            if target_pos == 0:
                self.draw_left_arrow(True)
                self.flipper(0.3)
                self.draw_left_arrow(False)
            else:
                self.draw_right_arrow(True)
                self.flipper(0.3)
                self.draw_right_arrow(False)

            self.text_left.autoDraw = False
            self.text_right.autoDraw = False

        self.paragraph.autoDraw = True
        self.paragraph.pos = (-0.8, 0.9)
        self.paragraph.text = (
            u'After you reach the end of the sentence, a feedback message will be displayed.'
        )

        self.message.text = u'Correct!'
        self.message.color = (-1, 1, -1)
        self.message.autoDraw = True

        self.flipper(5)
        self.message.autoDraw = False

        self.paragraph.text = (
            u'If you choose the wrong word in the middle of a sentence, the trial will end:'
        )
        self.flipper(5)

        self.fixation.autoDraw = True
        self.flipper(0.5)
        self.fixation.autoDraw = False

        self.text_left.text = u'✔✔✔'
        self.text_right.text = u'✘✘✘'
        self.text_left.autoDraw = True
        self.text_right.autoDraw = True
        self.flipper(3)

        self.draw_right_arrow(True)
        self.flipper(1)
        self.draw_right_arrow(False)

        self.text_left.autoDraw = False
        self.text_right.autoDraw = False
        self.window.color = (1, -1, -1)
        self.flipper(0.2)
        self.window.color = (1, 1, 1)

        self.fixation.autoDraw = True
        self.flipper(0.5)
        self.fixation.autoDraw = False

        self.message.text = u'Incorrect'
        self.message.color = (1, -1, -1)
        self.message.autoDraw = True

        self.flipper(5)

        self.message.autoDraw = False

        self.paragraph.autoDraw = True
        self.paragraph.pos = (-0.8, 0)

        self.paragraph.text = (
            u'If you have any questions about this experiment, please ask the experimenter now. '
        )
        self.flipper(5)

        move, frames = self.animated_move([-0.8, 0.0], [-0.8, 0.75], 5)
        for i in range(frames):
            self.paragraph.pos += move
            self.window.flip()

        self.paragraph.text = (
            u'If you would like to see these instructions again, press the button on the left. ' +
            u'If you are ready to try a few practice trials, press the button on the right.'
        )

        self.text_left.text = u'↺ Replay'
        self.text_right.text = u'Continue ➡'
        self.fixation.text = u'|'
        self.text_left.autoDraw = True
        self.text_right.autoDraw = True
        self.fixation.autoDraw = True

        self.flipper(10)

    def prepare_visuals(self):
        self.paragraph = visual.TextStim(
            win=self.window,  name='paragraph_text',text='',
            font='Songti SC', pos=(-0.8, 0),         height=0.1,
            wrapWidth=1.6,    color=(-1,-1,-1),   colorSpace='rgb',
            opacity=1,        depth=0.0,          ori=0,
            alignHoriz='left', alignVert='top'
        )

        self.left_arrow = visual.ShapeStim(
            win=self.window, name='left_arrow',
            lineColor=None, fillColor=(-1,-1,-1),
            vertices=[(-0.4,0.05),(-0.4,-0.05),(-.2,-0.05),(-.2,-0.1),(-0.1,0),(-.2,0.1),(-.2,0.05)],
            pos=(-1,-1), interpolate=True, ori=135
        )

        self.right_arrow = visual.ShapeStim(
            win=self.window, name='right_arrow',
            lineColor=None, fillColor=(-1,-1,-1),
            vertices=[(-0.4,0.05),(-0.4,-0.05),(-.2,-0.05),(-.2,-0.1),(-0.1,0),(-.2,0.1),(-.2,0.05)],
            pos=(1,-1), interpolate=True, ori=45
        )

        self.press_button_left = visual.ImageStim(
            win=self.window, name='press_img_left',
            image=u'{}{}{}{}{}'.format(
                self.parent.pwd, os.sep,
                u'data', os.sep, 'press.png'
            ),
            size=(0.25/(self.window.size[0]/self.window.size[1]), 0.25),
            interpolate=True, pos=(-0.65, -0.55), flipHoriz=True
        )

        self.press_button_right = visual.ImageStim(
            win=self.window, name='press_img_right',
            image=u'{}{}{}{}{}'.format(
                self.parent.pwd, os.sep,
                u'data', os.sep, 'press.png'
            ),
            size=(0.25/(self.window.size[0]/self.window.size[1]), 0.25),
            interpolate=True, pos=(0.65, -0.55)
        )

        self.message = visual.TextStim(
            win=self.window,    name='message', text='',
            font='Courier New', pos=(0, 0),         height=0.25,
            wrapWidth=None,     color=(-1,-1,-1),   colorSpace='rgb',
            opacity=1,          depth=0.0,          ori=0
        )

        self.fixation = visual.TextStim(
            win=self.window,    name='fixation',    text='+',
            font='Courier New', pos=(0, 0),         height=0.25,
            wrapWidth=None,     color=(-1, -1, -1), colorSpace='rgb',
            opacity=1,          depth=0.0,          ori=0
        )

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

        # self.draw_left_arrow(True)
        # self.draw_right_arrow(True)

    def draw_left_arrow(self, draw=True):
        self.left_arrow.autoDraw = draw
        self.press_button_left.autoDraw = draw

    def draw_right_arrow(self, draw=True):
        self.right_arrow.autoDraw = draw
        self.press_button_right.autoDraw = draw

    def flipper(self, time):
        frames = int(round(time / self.parent.frame_dur))
        for i in range(frames):
            self.window.flip()

    def animated_move(self, start, end, duration):
        frames = int(round(duration / self.parent.frame_dur))
        move_x = (end[0] - start[0])/frames
        move_y = (end[1] - start[1])/frames

        return [move_x, move_y], frames

    # def _rotate(self, vertices, rotation):
    #     rotated = []
    #     window_size = self.window.size
    #
    #     def pix_width(dimension, width=window_size[0]):
    #         return (width/2) + (width/2*dimension)
    #
    #     def pix_height(dimension, height=window_size[1]):
    #         return (height/2) + (height/2*dimension)
    #
    #     def rel_width(dimension, width=window_size[0]):
    #         return -1 * ((width/2) - dimension)/(width/2)
    #
    #     def rel_height(dimension, height=window_size[1]):
    #         return -1 * ((height/2) - dimension)/(height/2)
    #
    #     for vertex in vertices:
    #         new_vertex = [0,0]
    #         new_vertex[0] = pix_width(vertex[0])*cos(rotation) - pix_height(vertex[1])*sin(rotation)
    #         new_vertex[1] = pix_width(vertex[0])*sin(rotation) + pix_height(vertex[1])*cos(rotation)
    #         rotated.append(new_vertex)
    #
    #     return rotated
