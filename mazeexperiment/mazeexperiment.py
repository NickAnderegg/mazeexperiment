#!/usr/bin/env python2
# -*- coding: utf-8 -*-


# The MIT License (MIT)
#
# Copyright (c) 2016 Your Name
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#add correct version number here
__version__ = "1.0.0"
__author__ = "Nick Anderegg"


#PROGRAMNAME="mazeexperiment"
#VERSION=__version__
#COPYRIGHT="(C) 2016 Your Name"

import experiment
import os, sys

def main():
    exp_pwd = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
    experiment.Experiment(pwd=exp_pwd, autorun=True)

if __name__ == "__main__":
    main()
