from __future__ import absolute_import, division, print_function

# NOTE: We can't use pytest for these tests because using pyautogui to send the
# input results in a "oserror: reading from stdin while output is captured" error.

import io
import sys
import threading
import time
import unittest

import pyinputplus as pyip
from pynput.keyboard import Controller

keyboard = Controller()
originalStdout = sys.stdout


# TODO - work in progress

def pauseThenType(text, pauseLen=0.05):
    def inner(text):
        time.sleep(pauseLen)
        keyboard.type(text)
    t = threading.Thread(target=inner, args=(text,))
    t.start()
    sys.stdout = io.StringIO()

def getOut(): # get captured output
    return sys.stdout.getvalue()

class test_inputStr(unittest.TestCase):
    def test_inputStr(self):
        # Test typical usage.
        pauseThenType('hello\n')
        self.assertEqual(pyip.inputStr(), 'hello')
        self.assertEqual(getOut(), '')

        # Test prompt keyword arg.
        pauseThenType('hello\n')
        self.assertEqual(pyip.inputStr('Prompt>'), 'hello')
        self.assertEqual(getOut(), 'Prompt>')

        # Test default keyword arg with retry limit keyword arg.
        pauseThenType('\n\n')
        self.assertEqual(pyip.inputStr(default='def', limit=2), 'def')
        self.assertEqual(getOut(), 'Blank values are not allowed.\nBlank values are not allowed.\n')

        # Test default keyword arg with timeout keyword arg.
        pauseThenType('hello\n')
        self.assertEqual(pyip.inputStr(default='def', timeout=0.01), 'def')
        self.assertEqual(getOut(), '')

        # Test retry limit with no default value.
        with self.assertRaises(pyip.RetryLimitException):
            pauseThenType('\n\n')
            pyip.inputStr(limit=2)
        self.assertEqual(getOut(), 'Blank values are not allowed.\nBlank values are not allowed.\n')

        # Test timeout limit with no default value, entering valid input.
        with self.assertRaises(pyip.TimeoutException):
            pauseThenType('hello\n')
            pyip.inputStr(timeout=0.01)
        self.assertEqual(getOut(), '')

        # Test timeout limit with no default value, entering invalid input.
        with self.assertRaises(pyip.TimeoutException):
            pauseThenType('\n')
            pyip.inputStr(timeout=0.01)
        self.assertEqual(getOut(), 'Blank values are not allowed.\n')

        # Test timeout limit but with valid input and default value.
        pauseThenType('hello\n')
        self.assertEqual(pyip.inputStr(default='def', timeout=9999), 'hello')
        self.assertEqual(getOut(), '')

        # Test retry limit but with valid input and default value.
        pauseThenType('\nhello\n')
        self.assertEqual(pyip.inputStr(default='def', limit=9999), 'hello')
        self.assertEqual(getOut(), 'Blank values are not allowed.\n')

        # Test blank=True with blank input.
        pauseThenType('\n')
        self.assertEqual(pyip.inputStr(blank=True), '')
        self.assertEqual(getOut(), '')

        # Test blank=True with normal valid input.
        pauseThenType('hello\n')
        self.assertEqual(pyip.inputStr(blank=True), 'hello')
        self.assertEqual(getOut(), '')

        # Test blank=True with normal valid input and a default value. (Make sure
        # the default value isn't used.)
        pauseThenType('hello\n')
        self.assertEqual(pyip.inputStr(blank=True, default='def'), 'hello')
        self.assertEqual(getOut(), '')

        # Test applyFunc keyword arg.
        pauseThenType('hello\n')
        self.assertEqual(pyip.inputStr(applyFunc=str.upper), 'HELLO')
        self.assertEqual(getOut(), '')

        # Test allowlistRegexes keyword arg.
        pauseThenType('hello\n')
        self.assertEqual(pyip.inputStr(allowlistRegexes=['.*']), 'hello')
        self.assertEqual(getOut(), '')
        pauseThenType('hello\n')
        self.assertEqual(pyip.inputStr(allowlistRegexes=['hello']), 'hello')
        self.assertEqual(getOut(), '')

        # Test blocklistRegexes keyword arg, with a single regex.
        pauseThenType('hello\nhowdy\n')
        self.assertEqual(pyip.inputStr(blocklistRegexes=['hello']), 'howdy')
        self.assertEqual(getOut(), 'This response is invalid.\n')

        # Test blocklistRegexes keyword arg, with multiple regexes.
        pauseThenType('hello\nhowdy\n!!!\n')
        self.assertEqual(pyip.inputStr(blocklistRegexes=['hello', r'\w+']), '!!!')
        self.assertEqual(getOut(), 'This response is invalid.\nThis response is invalid.\n')

        # Test postValidateApplyFunc keyword arg.
        # (The blocklist regex will block uppercase responses, but the
        # postValidateApplyFunc will convert it to uppercase.)
        pauseThenType('HOWDY\nhello\n')
        self.assertEqual(pyip.inputStr(blocklistRegexes=['[A-Z]+'], postValidateApplyFunc=str.upper), 'HELLO')
        self.assertEqual(getOut(), 'This response is invalid.\n')

        # Test strip keyword arg
        pauseThenType('   hello    \n')
        self.assertEqual(pyip.inputStr(), 'hello')
        self.assertEqual(getOut(), '')

        pauseThenType(' hello \n')
        self.assertEqual(pyip.inputStr(strip=None), ' hello ')
        self.assertEqual(getOut(), '')

        pauseThenType('xxxhello\n')
        self.assertEqual(pyip.inputStr(strip='x'), 'hello')
        self.assertEqual(getOut(), '')

        pauseThenType('cbacbahelloaaa\n')
        self.assertEqual(pyip.inputStr(strip='abc'), 'hello')
        self.assertEqual(getOut(), '')


    def test_inputNum(self):
        # Test typical usage.
        pauseThenType('42\n')
        self.assertEqual(pyip.inputNum(), 42)
        self.assertEqual(getOut(), '')

        pauseThenType('42.0\n')
        self.assertEqual(pyip.inputNum(), 42.0)
        self.assertEqual(getOut(), '')

        # Test invalid input.
        pauseThenType('one\ntwo\n42\n')
        self.assertEqual(pyip.inputNum(), 42)
        self.assertEqual(getOut(), "'one' is not a number.\n'two' is not a number.\n")

        # Test postValidateApplyFunc keyword argument.
        pauseThenType('42\n')
        self.assertEqual(pyip.inputNum(postValidateApplyFunc=str), '42')
        self.assertEqual(getOut(), '')

        # Test prompt keyword arg.
        pauseThenType('42\n')
        self.assertEqual(pyip.inputNum('Prompt>'), 42)
        self.assertEqual(getOut(), 'Prompt>')

        # Test default keyword arg with retry limit keyword arg.
        pauseThenType('\n\n')
        self.assertEqual(pyip.inputNum(default='def', limit=2), 'def')
        self.assertEqual(getOut(), 'Blank values are not allowed.\nBlank values are not allowed.\n')

        # Test default keyword arg with timeout keyword arg.
        pauseThenType('42\n')
        self.assertEqual(pyip.inputNum(default='def', timeout=0.01), 'def')
        self.assertEqual(getOut(), '')

        # Test retry limit with no default value.
        with self.assertRaises(pyip.RetryLimitException):
            pauseThenType('\n\n')
            pyip.inputNum(limit=2)
        self.assertEqual(getOut(), 'Blank values are not allowed.\nBlank values are not allowed.\n')

        # Test timeout limit with no default value, entering valid input.
        with self.assertRaises(pyip.TimeoutException):
            pauseThenType('42\n')
            pyip.inputNum(timeout=0.01)
        self.assertEqual(getOut(), '')

        # Test timeout limit with no default value, entering invalid input.
        with self.assertRaises(pyip.TimeoutException):
            pauseThenType('\n')
            pyip.inputNum(timeout=0.01)
        self.assertEqual(getOut(), 'Blank values are not allowed.\n')

        # Test timeout limit but with valid input and default value.
        pauseThenType('42\n')
        self.assertEqual(pyip.inputNum(default='def', timeout=9999), 42)
        self.assertEqual(getOut(), '')

        # Test retry limit but with valid input and default value.
        pauseThenType('\n42\n')
        self.assertEqual(pyip.inputNum(default='def', limit=9999), 42)
        self.assertEqual(getOut(), 'Blank values are not allowed.\n')

        # Test blank=True with blank input.
        pauseThenType('\n')
        self.assertEqual(pyip.inputNum(blank=True), '')
        self.assertEqual(getOut(), '')

        # Test blank=True with normal valid input.
        pauseThenType('42\n')
        self.assertEqual(pyip.inputNum(blank=True), 42)
        self.assertEqual(getOut(), '')

        # Test applyFunc keyword arg.
        pauseThenType('42\n')
        self.assertEqual(pyip.inputNum(applyFunc=lambda x: int(x)+1), 43)
        self.assertEqual(getOut(), '')

        # Test allowlistRegexes keyword arg.
        pauseThenType('42\n')
        self.assertEqual(pyip.inputNum(allowlistRegexes=['.*']), 42)
        self.assertEqual(getOut(), '')
        pauseThenType('42\n')
        self.assertEqual(pyip.inputNum(allowlistRegexes=['42']), 42)
        self.assertEqual(getOut(), '')

        # Test blocklistRegexes keyword arg, with a single regex.
        pauseThenType('42\n43\n')
        self.assertEqual(pyip.inputNum(blocklistRegexes=['42']), 43)
        self.assertEqual(getOut(), 'This response is invalid.\n')

        # Test blocklistRegexes keyword arg, with multiple regexes.
        pauseThenType('42\n44\n43\n')
        self.assertEqual(pyip.inputNum(blocklistRegexes=['42', r'[02468]$']), 43)
        self.assertEqual(getOut(), 'This response is invalid.\nThis response is invalid.\n')

        # Test postValidateApplyFunc keyword arg.
        # (The blocklist regex will block uppercase responses, but the
        # postValidateApplyFunc will convert it to uppercase.)
        pauseThenType('42\n41\n')
        self.assertEqual(pyip.inputNum(blocklistRegexes=['[02468]$'], postValidateApplyFunc=lambda x: x+1), 42)
        self.assertEqual(getOut(), 'This response is invalid.\n')

        # Test strip. (Note that strip=None has no effect and is the same
        # as strip=True, since int()/float() don't care about whitespace.)
        pauseThenType('  42  \n')
        self.assertEqual(pyip.inputNum(), 42)
        self.assertEqual(getOut(), '')

        pauseThenType('abc42cba\n')
        self.assertEqual(pyip.inputNum(strip='abc'), 42)
        self.assertEqual(getOut(), '')

        pauseThenType('abc 42 cba\n')
        self.assertEqual(pyip.inputNum(strip='abc'), 42)
        self.assertEqual(getOut(), '')


if __name__ == '__main__':
    unittest.main()
    sys.stdout = originalStdout # Restore stdout.
