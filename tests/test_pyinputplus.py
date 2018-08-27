from __future__ import absolute_import, division, print_function

# NOTE: We can't use pytest for these tests because using pyautogui to send the
# input results in a "oserror: reading from stdin while output is captured" error.

import os
import sys

input = lambda: 'hello'

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pyinputplus as pyip





def test_inputStr():
    # Test typical usage.
    assert pyip.inputStr() == 'hello'




if __name__ == '__main__':
    test_inputStr()


