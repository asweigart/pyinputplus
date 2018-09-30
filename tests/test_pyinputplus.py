from __future__ import absolute_import, division, print_function

# NOTE: We can't use pytest for these tests because using pyautogui to send the
# input results in a "oserror: reading from stdin while output is captured" error.

import threading
import time
import pyinputplus as pyip
from pynput.keyboard import Controller
keyboard = Controller()


# TODO - work in progress

def pauseThenType(text):
    def inner(text):
        time.sleep(0.1)
        keyboard.type(text)
    t = threading.Thread(target=inner, args=(text,))
    t.start()

def test_inputStr():
    # Test typical usage.
    pauseThenType('hello\n')
    assert pyip.inputStr() == 'hello'


if __name__ == '__main__':
    test_inputStr()
