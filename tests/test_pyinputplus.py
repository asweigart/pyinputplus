from __future__ import absolute_import, division, print_function

# NOTE: We can't use pytest for these tests because using pyautogui to send the
# input results in a "oserror: reading from stdin while output is captured" error.

import os
import sys
import time
import threading

import pyautogui

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pyinputplus


class TypewriteThread(threading.Thread):
    def __init__(self, msg, interval=0.0):
        super(TypewriteThread, self).__init__()
        self.msg = msg
        self.interval = interval
        self.start()


    def run(self):
        time.sleep(0.1)
        pyautogui.typewrite(self.msg, self.interval)


# Start the tests.
TypewriteThread('hello\n')
assert pyinputplus.inputStr() == 'hello'

TypewriteThread('\nhello\n')
assert pyinputplus.inputStr() == 'hello'

