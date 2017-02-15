#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from psychopy import locale_setup, visual, core, data, event, logging, sound#, gui
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)

import numpy as np
from numpy.random import random, randint, normal, shuffle

from math import cos, sin

from datetime import datetime
import time
import os, sys

# Text constants
TEXT_GET_READY = u'请准备'
TEXT_FEEDBACK_CORRECT = u'正确！'
TEXT_FEEDBACK_INCORRECT = u'错误！'

# Speed constants
SPEED_MULTIPLIER = 1

class Instructions():
    def __init__(self, parent, exp_info):
        self.exp_info = exp_info
        self.parent = parent

        self.window = self.parent.window

        self.prepare_visuals()
        self.prepare_audio()

    def begin_instructions(self):
        # self.paragraph.text = u'In this experiment, you will be asked to read sentences in Mandarin. '
        self.play_instructions(1)
        self.paragraph.text = (
            u'在这个实验中，你将阅读一些中文句子。'
        )
        self.paragraph.autoDraw = True
        self.paragraph.alignVert = 'center'
        self.flipper(5 * SPEED_MULTIPLIER)

        # self.paragraph.text = (
        #     u'The words in each sentence will be presented one at a time. Each word ' +
        #     u'in a sentence will appear beside an unrelated word that does ' +
        #     u'that does not fit into the sentence.'
        # )
        self.play_instructions(2)
        self.paragraph.text = (
            u'句子中的词将会一个一个呈现。每一个适合语\u2028' +
            u'境的词将会和一个不适合语境的词同时出现。'
        )
        self.flipper(10 * SPEED_MULTIPLIER)

        # self.paragraph.text = (
        #     u'Your task is to choose which word fits best into the sentence. '+
        #     u'You will do this by pressing the button which corresponds to the side ' +
        #     u'that the correct word is on.'
        # )
        self.play_instructions(3)
        self.paragraph.text = (
            u'你需要做的就是选出适合语境那个词。你将按相应的键\u2028' +
            u'来选择正确的词。'
        )
        self.flipper(10 * SPEED_MULTIPLIER)

        # self.paragraph.text = (
        #     u'To choose the word that is on the left side of the screen, ' +
        #     u'press the button that is on the left side of the response box.'
        # )
        self.play_instructions(4)
        self.paragraph.text = u'如果要选择左边的词，按左键。'
        self.flipper(3 * SPEED_MULTIPLIER)
        draw = True
        for i in range(20):
            self.draw_left_arrow(draw)
            self.flipper(0.25)
            draw = not draw

        self.draw_left_arrow(False)
        self.paragraph.autoDraw = False
        self.flipper(1)

        self.paragraph.autoDraw = True
        # self.paragraph.text = (
        #     u'To choose the word that is on the right side of the screen, ' +
        #     u'press the button that is on the right side of the response box.'
        # )
        self.play_instructions(5)
        self.paragraph.text = u'如果要选择右边的词，按右键。'
        self.flipper(3 * SPEED_MULTIPLIER)
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
        # self.paragraph.text = (
        #     u'Before each block of sentences begins, ' +
        #     u'a message will appear on screen which states "GET READY"'
        # )
        self.play_instructions(6)
        self.paragraph.text = u'每个句子开始之前，你会看到“请准备”的提示。'
        self.paragraph.pos= (-0.8, 0.9)
        self.paragraph.autoDraw = True
        self.flipper(3 * SPEED_MULTIPLIER)

        # self.message.text = u'GET READY'
        self.message.text = TEXT_GET_READY
        self.message.autoDraw = True
        self.flipper(7.5 * SPEED_MULTIPLIER)

        self.paragraph.autoDraw = False
        self.flipper(0.25)
        # self.paragraph.text = (
        #     u'This will be followed briefly by a blank screen. When a ' +
        #     u'fixation cross (+) appears on screen, the first sentence is about '+
        #     u'to begin. Here\'s an example:'
        # )
        self.play_instructions(7)
        self.paragraph.text = (
            u'紧跟着你会看到空白屏幕。然后“+” 会出现在屏幕上，\u2028' +
            u'第一个句子即将开始。我们来看一个例子：'
        )
        self.paragraph.autoDraw = True
        self.flipper(10 * SPEED_MULTIPLIER)
        self.paragraph.autoDraw = False
        self.flipper(2 * SPEED_MULTIPLIER)
        self.message.autoDraw = False
        self.flipper(1)
        self.fixation.autoDraw = True
        self.flipper(3 * SPEED_MULTIPLIER)

        # self.paragraph.text = (
        #     u'The first word in each sentence will be presented beside a series of X symbols.'
        # )
        self.play_instructions(8)
        self.paragraph.text = (
            u'你需要按相应的键选择正确的词。\u2028' +
            u'每个句子的第一个词的选项里\u2028' +
            u'只有一是词，你只需要选择这个词。'
        )
        self.paragraph.autoDraw = True
        self.flipper(9 * SPEED_MULTIPLIER)

        self.text_left.text = 'XXX'
        # self.text_right.text = 'The'
        self.text_right.text = u'一个'
        self.text_left.autoDraw = True
        self.text_right.autoDraw = True
        self.flipper(0.5)

        self.fixation.autoDraw = False
        self.flipper(3 * SPEED_MULTIPLIER)

        # self.paragraph.text = (
        #     u'You have to press the response button which corresponds to the correct word.'
        # )
        # This sentence has been combined with the above translation

        self.paragraph.autoDraw = True
        self.flipper(3 * SPEED_MULTIPLIER)

        # self.paragraph.text = (
        #     u'Press the button on the right to choose that word.'
        # )
        self.play_instructions(9)
        self.paragraph.text = u'按左键选择左边的词。'
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
        # self.paragraph.text = (
        #     u'After you choose a word, both words will be replaced by a fixation cross. ' +
        #     u'Then, you will see two new words. Only one of these words can come after the ' +
        #     u'previous word that you chose. Here\'s an example:'
        # )
        self.play_instructions(10)
        self.paragraph.text = (
            u'你做好选择之后，两个词会消失，“+”会出现。\u2028' +
            u'然后你会看到两个新词，其中一个更接应\u2028' +
            u'前一个被选择的词的语境。\u2028' +
            u'我们来看一个例子：'
        )
        self.flipper(15 * SPEED_MULTIPLIER)
        self.text_left.autoDraw = False
        self.text_right.autoDraw = False
        self.fixation.autoDraw = True
        self.paragraph.autoDraw = False
        self.flipper(0.5)

        self.fixation.autoDraw = False
        # self.text_left.text = 'boy'
        self.text_left.text = u'男孩'
        # self.text_right.text = 'jumped'
        self.text_right.text = u'跳'
        self.text_left.autoDraw = True
        self.text_right.autoDraw = True

        self.flipper(3 * SPEED_MULTIPLIER)

        self.paragraph.autoDraw = True
        # self.paragraph.text = (
        #     u'Now you should choose the word that is on the left side by pressing ' +
        #     u'the button on the left. You would choose this because "The boy..." is ' +
        #     u'correct grammar, while "The jumped..." is not a legal sentence.'
        # )
        self.play_instructions(11)
        self.paragraph.text = u'按左键选择左边的词。\u2028因为“一个男孩” 是正确语法而“一个跳”不是。'
        self.flipper(11 * SPEED_MULTIPLIER)

        self.paragraph.pos = (-0.5, -0.6)
        # self.paragraph.text = (
        #     u'Press the button on the left to choose that word.'
        # )
        self.play_instructions(12)
        self.paragraph.text = u'按左键选择左边的词。'

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

        # self.paragraph.text = (
        #     u'Good! Now you will see an example of responses to an entire sentence. ' +
        #     u'Please watch the screen carefully, but do not make any responses.'
        # )
        self.play_instructions(13)
        self.paragraph.text = (
            u'很好！\u2028现在我们来看一个完整' +
            u'句子词汇选择的例子。\u2028' +
            u'请认真观看，不需要做任何选择。'
        )

        self.paragraph.autoDraw = True
        self.paragraph.pos = (-0.8, 0)
        self.flipper(10 * SPEED_MULTIPLIER)

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
        self.flipper(2 * SPEED_MULTIPLIER)

        # self.message.text = u'GET READY'
        self.message.text = TEXT_GET_READY
        self.message.autoDraw = True
        self.flipper(5 * SPEED_MULTIPLIER)
        self.message.autoDraw = False
        self.flipper(1)
        self.fixation.autoDraw = True
        self.flipper(3 * SPEED_MULTIPLIER)

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
        # self.paragraph.text = (
        #     u'After you reach the end of the sentence, a feedback message will be displayed.'
        # )
        self.play_instructions(14)
        self.paragraph.text = u'当你选好每个句子的最后一个词，\u2028你会看到一个反馈消息。'

        # self.message.text = u'Correct!'
        self.message.text = TEXT_FEEDBACK_CORRECT
        self.message.color = (-1, 1, -1)
        self.message.autoDraw = True

        self.flipper(5 * SPEED_MULTIPLIER)
        self.message.autoDraw = False

        # self.paragraph.text = (
        #     u'If you choose the wrong word in the middle of a sentence, the trial will end:'
        # )
        self.play_instructions(15)
        self.paragraph.text = (
            u'如果你在句中选择了错误的词，\u2028' +
            u'这个句子会半途而废：\u2028' +
            u'然后你会看到 “错误！” 的提示。'
        )
        self.flipper(7 * SPEED_MULTIPLIER)

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

        # self.message.text = u'Incorrect'
        self.message.text = TEXT_FEEDBACK_INCORRECT
        self.message.color = (1, -1, -1)
        self.message.autoDraw = True

        self.flipper(5 * SPEED_MULTIPLIER)

        self.message.autoDraw = False

        self.paragraph.autoDraw = True
        self.paragraph.pos = (-0.8, 0)

        # self.paragraph.text = (
        #     u'If you have any questions about this experiment, please ask the experimenter now. '
        # )
        self.play_instructions(16)
        self.paragraph.text = u'如果你有任何问题，请现在提问。'
        self.flipper(5 * SPEED_MULTIPLIER)

        move, frames = self.animated_move([-0.8, 0.0], [-0.8, 0.75], 5)
        for i in range(frames):
            self.paragraph.pos += move
            self.window.flip()

        # self.paragraph.text = (
        #     u'If you would like to see these instructions again, press the button on the left. ' +
        #     u'If you are ready to try a few practice trials, press the button on the right.'
        # )
        self.play_instructions(17)
        self.paragraph.text = (
            u'如果你还需要看一遍实验介绍，按左键。\u2028' +
            u'如果你没有问题已经准备好，按右键。'
        )


        self.text_left.height = 0.12
        self.text_right.height = 0.12

        # self.text_left.text = u'↺ Replay'
        self.text_left.text = u'↺ 重放实验介绍'
        # self.text_right.text = u'Continue ➡'
        self.text_right.text = u'继续到实验 ➡'
        self.fixation.text = u'|'
        self.text_left.autoDraw = True
        self.text_right.autoDraw = True
        self.fixation.autoDraw = True

        self.flipper(12 * SPEED_MULTIPLIER)

    def prepare_audio(self):
        self.instructions_audio = {}

        for i in range(1, 18):
            self.instructions_audio[i] = sound.Sound(u'{}{}{}{}{}{}{}{}{}'.format(
                self.parent.pwd, os.sep,
                u'data', os.sep, u'instructions_audio',
                os.sep, u'edited', os.sep, u'instr_{:0>2}.wav'.format(i)
            ))

    def play_instructions(self, i):
        self.instructions_audio[i].play()

    def prepare_visuals(self):
        self.paragraph = visual.TextStim(
            win=self.window,  name='paragraph_text',text='',
            font='SimSun', pos=(-0.8, 0),         height=0.1,
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
            font='SimSun', pos=(0, 0),         height=0.25,
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
            font='SimSun',   pos=(-0.1, 0),      height=0.25,
            wrapWidth=None,     color=(-1, -1, -1), colorSpace='rgb',
            opacity=1,          depth=0.0,          ori=0,
            alignHoriz='right'
        )

        self.text_right = visual.TextStim(
            win=self.window,    name='text_right',  text='',
            font='SimSun',   pos=(0.1, 0),       height=0.25,
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
