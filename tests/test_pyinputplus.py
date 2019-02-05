from __future__ import absolute_import, division, print_function

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# NOTE: We can't use pytest for these tests because using pyautogui to send
# the input results in a "oserror: reading from stdin while output is captured"
# error.
# These tests don't fail so much as hang the system. If you see the test hang,
# that means there's a failure somewhere.
# CURRENTLY TOX DOESN'T SEEM TO WORK WITH THIS TEST.
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

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

class test_main(unittest.TestCase):
    def test_inputStr(self):
        # Test typical usage.
        pauseThenType('hello\n')
        self.assertEqual(pyip.inputStr(), 'hello')
        self.assertEqual(getOut(), '')

        # Test prompt keyword arg.
        pauseThenType('hello\n')
        self.assertEqual(pyip.inputStr('Prompt>'), 'hello')
        self.assertEqual(getOut(), 'Prompt>')

        # Test that prompt reappears.
        pauseThenType('\nhello\n')
        self.assertEqual(pyip.inputStr('Prompt>'), 'hello')
        self.assertEqual(getOut(), 'Prompt>Blank values are not allowed.\nPrompt>')

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
        self.assertEqual(pyip.inputStr(strip=False), ' hello ')
        self.assertEqual(getOut(), '')

        pauseThenType('xxxhello\n')
        self.assertEqual(pyip.inputStr(strip='x'), 'hello')
        self.assertEqual(getOut(), '')

        pauseThenType('cbacbahelloaaa\n')
        self.assertEqual(pyip.inputStr(strip='abc'), 'hello')
        self.assertEqual(getOut(), '')


    def test_inputCustom(self):
        # Test validation function arg:
        def isEven(value):
            if float(value) % 2 != 0:
                raise Exception('This is not an even value.')

        pauseThenType('4.1\n2\n')
        self.assertEqual(pyip.inputCustom(isEven), '2')
        pauseThenType('hello\n2\n')
        self.assertEqual(pyip.inputCustom(isEven), '2')
        pauseThenType('4\n')
        self.assertEqual(pyip.inputCustom(isEven), '4')
        pauseThenType('4.0\n')
        self.assertEqual(pyip.inputCustom(isEven), '4.0')


    def _test_inputNumTemplate(self, inputFunc, numValue, numType):
        numValue += '\n'
        # Test typical usage.
        pauseThenType(numValue)
        self.assertEqual(inputFunc(), numType(numValue))
        self.assertEqual(getOut(), '')

        # Test invalid input.
        pauseThenType('one\ntwo\n' + numValue)
        self.assertEqual(inputFunc(), numType(numValue))
        #self.assertEqual(getOut(), "'one' is not a number.\n'two' is not a number.\n")

        # Test negative numbers.
        pauseThenType('-' + numValue)
        self.assertEqual(inputFunc(), numType('-' + numValue))
        self.assertEqual(getOut(), '')

        # Test greater than min.
        pauseThenType(numValue)
        self.assertEqual(inputFunc(min=numType(numValue) - 1), numType(numValue))
        self.assertEqual(getOut(), '')

        # Test equal to min.
        pauseThenType(numValue)
        self.assertEqual(inputFunc(min=numType(numValue)), numType(numValue))
        self.assertEqual(getOut(), '')

        # Test less than min.
        pauseThenType(str(numType(numValue) - 1) + '\n' + numValue)
        self.assertEqual(inputFunc(min=numType(numValue)), numType(numValue))
        self.assertEqual(getOut(), 'Number must be at minimum %s.\n' % (numType(numValue)))

        # Test greater than max.
        pauseThenType(str(numType(numValue) + 1) + '\n' + numValue)
        self.assertEqual(inputFunc(max=numType(numValue)), numType(numValue))
        self.assertEqual(getOut(), 'Number must be at maximum %s.\n' % (numType(numValue)))

        # Test equal to max.
        pauseThenType(numValue)
        self.assertEqual(inputFunc(max=numType(numValue)), numType(numValue))
        self.assertEqual(getOut(), '')

        # Test less than max.
        pauseThenType(str(numType(numValue) - 1) + '\n')
        self.assertEqual(inputFunc(max=numType(numValue)), numType(numValue) - 1)
        self.assertEqual(getOut(), '')

        # Test greater than greaterThan.
        pauseThenType(numValue)
        self.assertEqual(inputFunc(greaterThan=numType(numValue) - 1), numType(numValue))
        self.assertEqual(getOut(), '')

        # Test equal to greaterThan.
        pauseThenType(numValue + str(numType(numValue) + 1) + '\n')
        self.assertEqual(inputFunc(greaterThan=numType(numValue)), numType(numValue) + 1)
        self.assertEqual(getOut(), 'Number must be greater than %s.\n' % (numType(numValue)))

        # Test less than greaterThan.
        pauseThenType(str(numType(numValue) - 1) + '\n' + str(numType(numValue) + 1) + '\n')
        self.assertEqual(inputFunc(greaterThan=numType(numValue)), numType(numValue) + 1)
        self.assertEqual(getOut(), 'Number must be greater than %s.\n' % (numType(numValue)))

        # Test greater than lessThan.
        pauseThenType(str(numType(numValue) + 1) + '\n' + str(numType(numValue) - 1) + '\n')
        self.assertEqual(inputFunc(lessThan=numType(numValue)), numType(numValue) - 1)
        self.assertEqual(getOut(), 'Number must be less than %s.\n' % (numType(numValue)))

        # Test equal to lessThan.
        pauseThenType(numValue + str(numType(numValue) - 1) + '\n')
        self.assertEqual(inputFunc(lessThan=numType(numValue)), numType(numValue) - 1)
        self.assertEqual(getOut(), 'Number must be less than %s.\n' % (numType(numValue)))

        # Test less than lessThan.
        pauseThenType(str(numType(numValue) - 1) + '\n')
        self.assertEqual(inputFunc(lessThan=numType(numValue)), numType(numValue) - 1)
        self.assertEqual(getOut(), '')






        # Test postValidateApplyFunc keyword argument.
        pauseThenType(numValue)
        self.assertEqual(inputFunc(postValidateApplyFunc=str), str(numType(numValue)))
        self.assertEqual(getOut(), '')

        # Test prompt keyword arg.
        pauseThenType(numValue)
        self.assertEqual(inputFunc('Prompt>'), numType(numValue))
        self.assertEqual(getOut(), 'Prompt>')

        # Test that prompt reappears.
        pauseThenType('\n' + numValue)
        self.assertEqual(inputFunc('Prompt>'), numType(numValue))
        self.assertEqual(getOut(), 'Prompt>Blank values are not allowed.\nPrompt>')

        # Test default keyword arg with retry limit keyword arg.
        pauseThenType('\n\n')
        self.assertEqual(inputFunc(default='def', limit=2), 'def')
        self.assertEqual(getOut(), 'Blank values are not allowed.\nBlank values are not allowed.\n')

        # Test default keyword arg with timeout keyword arg.
        pauseThenType(numValue)
        self.assertEqual(inputFunc(default='def', timeout=0.01), 'def')
        self.assertEqual(getOut(), '')

        # Test retry limit with no default value.
        with self.assertRaises(pyip.RetryLimitException):
            pauseThenType('\n\n')
            inputFunc(limit=2)
        self.assertEqual(getOut(), 'Blank values are not allowed.\nBlank values are not allowed.\n')

        # Test timeout limit with no default value, entering valid input.
        with self.assertRaises(pyip.TimeoutException):
            pauseThenType(numValue)
            inputFunc(timeout=0.01)
        self.assertEqual(getOut(), '')

        # Test timeout limit with no default value, entering invalid input.
        with self.assertRaises(pyip.TimeoutException):
            pauseThenType('\n')
            inputFunc(timeout=0.01)
        self.assertEqual(getOut(), 'Blank values are not allowed.\n')

        # Test timeout limit but with valid input and default value.
        pauseThenType(numValue)
        self.assertEqual(inputFunc(default='def', timeout=9999), numType(numValue))
        self.assertEqual(getOut(), '')

        # Test retry limit but with valid input and default value.
        pauseThenType('\n' + numValue)
        self.assertEqual(inputFunc(default='def', limit=9999), numType(numValue))
        self.assertEqual(getOut(), 'Blank values are not allowed.\n')

        # Test blank=True with blank input.
        pauseThenType('\n')
        self.assertEqual(inputFunc(blank=True), '')
        self.assertEqual(getOut(), '')

        # Test blank=True with normal valid input.
        pauseThenType(numValue)
        self.assertEqual(inputFunc(blank=True), numType(numValue))
        self.assertEqual(getOut(), '')

        # Test applyFunc keyword arg.
        pauseThenType(numValue)
        self.assertEqual(inputFunc(applyFunc=lambda x: numType(x)+1), numType(numValue) + 1)
        self.assertEqual(getOut(), '')

        # Test allowlistRegexes keyword arg.
        pauseThenType(numValue)
        self.assertEqual(inputFunc(allowlistRegexes=['.*']), numType(numValue))
        self.assertEqual(getOut(), '')
        pauseThenType(numValue)
        self.assertEqual(inputFunc(allowlistRegexes=[numValue]), numType(numValue))
        self.assertEqual(getOut(), '')

        # Test strip. (Note that strip=None has no effect and is the same
        # as strip=True, since int()/float() don't care about whitespace.)
        pauseThenType('  ' + numValue.strip() + '  \n')
        self.assertEqual(inputFunc(), numType(numValue))
        self.assertEqual(getOut(), '')

        pauseThenType('abc' + numValue.strip() + 'cba\n')
        self.assertEqual(inputFunc(strip='abc'), numType(numValue))
        self.assertEqual(getOut(), '')

        pauseThenType('abc ' + numValue.strip() + ' cba\n')
        self.assertEqual(inputFunc(strip='abc'), numType(numValue))
        self.assertEqual(getOut(), '')

    def test_inputNum(self):
        self._test_inputNumTemplate(pyip.inputNum, '42', int)
        self._test_inputNumTemplate(pyip.inputNum, '42.0', float)

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

    def test_inputInt(self):
        self._test_inputNumTemplate(pyip.inputInt, '42', int)

        # Test blocklistRegexes keyword arg, with a single regex.
        pauseThenType('42\n43\n')
        self.assertEqual(pyip.inputInt(blocklistRegexes=['42']), 43)
        self.assertEqual(getOut(), 'This response is invalid.\n')

        # Test blocklistRegexes keyword arg, with multiple regexes.
        pauseThenType('42\n44\n43\n')
        self.assertEqual(pyip.inputInt(blocklistRegexes=['42', r'[02468]$']), 43)
        self.assertEqual(getOut(), 'This response is invalid.\nThis response is invalid.\n')

        # Test postValidateApplyFunc keyword arg.
        # (The blocklist regex will block uppercase responses, but the
        # postValidateApplyFunc will convert it to uppercase.)
        pauseThenType('42\n41\n')
        self.assertEqual(pyip.inputInt(blocklistRegexes=['[02468]$'], postValidateApplyFunc=lambda x: x+1), 42)
        self.assertEqual(getOut(), 'This response is invalid.\n')


    def test_inputFloat(self):
        self._test_inputNumTemplate(pyip.inputFloat, '42.0', float)

        # Test blocklistRegexes keyword arg, with a single regex.
        pauseThenType('42.0\n43.0\n')
        self.assertEqual(pyip.inputFloat(blocklistRegexes=['42']), 43.0)
        self.assertEqual(getOut(), 'This response is invalid.\n')

        # Test blocklistRegexes keyword arg, with multiple regexes.
        pauseThenType('42.0\n44.0\n43.0\n')
        self.assertEqual(pyip.inputFloat(blocklistRegexes=['42', r'[02468]\.']), 43.0)
        self.assertEqual(getOut(), 'This response is invalid.\nThis response is invalid.\n')

        # Test postValidateApplyFunc keyword arg.
        # (The blocklist regex will block uppercase responses, but the
        # postValidateApplyFunc will convert it to uppercase.)
        pauseThenType('42.0\n41.0\n')
        self.assertEqual(pyip.inputFloat(blocklistRegexes=[r'[02468]\.'], postValidateApplyFunc=lambda x: x+1), 42.0)
        self.assertEqual(getOut(), 'This response is invalid.\n')


    def test_inputChoice(self):
        # Test typical usage.
        pauseThenType('cat\n')
        self.assertEqual(pyip.inputChoice(['cat', 'dog']), 'cat')
        self.assertEqual(getOut(), 'Please select one of: cat, dog\n')

        # Test order of choices.
        pauseThenType('cat\n')
        self.assertEqual(pyip.inputChoice(['dog', 'cat']), 'cat')
        self.assertEqual(getOut(), 'Please select one of: dog, cat\n')

        # Test case-insensitivity.
        pauseThenType('CAT\n')
        self.assertEqual(pyip.inputChoice(['cat', 'dog']), 'cat')
        self.assertEqual(getOut(), 'Please select one of: cat, dog\n')

        # Test custom prompt.
        pauseThenType('cat\n')
        self.assertEqual(pyip.inputChoice(['cat', 'dog'], prompt='Choose:'), 'cat')
        self.assertEqual(getOut(), 'Choose:')

        # Test blank prompt.
        pauseThenType('cat\n')
        self.assertEqual(pyip.inputChoice(['cat', 'dog'], prompt=''), 'cat')
        self.assertEqual(getOut(), '')

        # Test that prompt reappears.
        pauseThenType('\ncat\n')
        self.assertEqual(pyip.inputChoice(['cat', 'dog'], prompt='Choose:'), 'cat')
        self.assertEqual(getOut(), 'Choose:Blank values are not allowed.\nChoose:')

        # Test default keyword arg with retry limit keyword arg.
        pauseThenType('\n\n')
        self.assertEqual(pyip.inputChoice(['cat', 'dog'], default='def', limit=2), 'def')
        self.assertEqual(getOut(), 'Please select one of: cat, dog\nBlank values are not allowed.\nPlease select one of: cat, dog\nBlank values are not allowed.\n')

        # Test default keyword arg with timeout keyword arg.
        pauseThenType('cat\n')
        self.assertEqual(pyip.inputChoice(['cat', 'dog'], default='def', timeout=0.01), 'def')
        self.assertEqual(getOut(), 'Please select one of: cat, dog\n')

        # Test retry limit with no default value.
        with self.assertRaises(pyip.RetryLimitException):
            pauseThenType('\n\n')
            pyip.inputChoice(['cat', 'dog'], limit=2)
        self.assertEqual(getOut(), 'Please select one of: cat, dog\nBlank values are not allowed.\nPlease select one of: cat, dog\nBlank values are not allowed.\n')

        # Test timeout limit with no default value, entering valid input.
        with self.assertRaises(pyip.TimeoutException):
            pauseThenType('cat\n')
            pyip.inputChoice(['cat', 'dog'], timeout=0.01)
        self.assertEqual(getOut(), 'Please select one of: cat, dog\n')

        # Test timeout limit with no default value, entering invalid input.
        with self.assertRaises(pyip.TimeoutException):
            pauseThenType('\n')
            pyip.inputChoice(['cat', 'dog'], timeout=0.01)
        self.assertEqual(getOut(), 'Please select one of: cat, dog\nBlank values are not allowed.\n')

        # Test timeout limit but with valid input and default value.
        pauseThenType('cat\n')
        self.assertEqual(pyip.inputChoice(['cat', 'dog'], default='def', timeout=9999), 'cat')
        self.assertEqual(getOut(), 'Please select one of: cat, dog\n')

        # Test retry limit but with valid input and default value.
        pauseThenType('\ncat\n')
        self.assertEqual(pyip.inputChoice(['cat', 'dog'], default='def', limit=9999), 'cat')
        self.assertEqual(getOut(), 'Please select one of: cat, dog\nBlank values are not allowed.\nPlease select one of: cat, dog\n')

        # Test blank=True with blank input.
        pauseThenType('\n')
        self.assertEqual(pyip.inputChoice(['cat', 'dog'], blank=True), '')
        self.assertEqual(getOut(), 'Please select one of: cat, dog\n')

        # Test blank=True with normal valid input.
        pauseThenType('cat\n')
        self.assertEqual(pyip.inputChoice(['cat', 'dog'], blank=True), 'cat')
        self.assertEqual(getOut(), 'Please select one of: cat, dog\n')

        # Test blank=True with normal valid input and a default value. (Make sure
        # the default value isn't used.)
        pauseThenType('cat\n')
        self.assertEqual(pyip.inputChoice(['cat', 'dog'], blank=True, default='def'), 'cat')
        self.assertEqual(getOut(), 'Please select one of: cat, dog\n')

        # Test applyFunc keyword arg.
        pauseThenType('c\n')
        self.assertEqual(pyip.inputChoice(['cat', 'dog'], applyFunc=lambda x: x + 'at'), 'cat')
        self.assertEqual(getOut(), 'Please select one of: cat, dog\n')

        # Test allowlistRegexes keyword arg.
        pauseThenType('cat\n')
        self.assertEqual(pyip.inputChoice(['cat', 'dog'], allowlistRegexes=['.*']), 'cat')
        self.assertEqual(getOut(), 'Please select one of: cat, dog\n')
        pauseThenType('cat\n')
        self.assertEqual(pyip.inputChoice(['cat', 'dog'], allowlistRegexes=['cat']), 'cat')
        self.assertEqual(getOut(), 'Please select one of: cat, dog\n')

        # Test blocklistRegexes keyword arg, with a single regex.
        pauseThenType('cat\ndog\n')
        self.assertEqual(pyip.inputChoice(['cat', 'dog'], blocklistRegexes=['cat']), 'dog')
        self.assertEqual(getOut(), 'Please select one of: cat, dog\nThis response is invalid.\nPlease select one of: cat, dog\n')

        # Test blocklistRegexes keyword arg, with multiple regexes.
        pauseThenType('cat\ncAT\ndog\n')
        self.assertEqual(pyip.inputChoice(['cat', 'dog'], blocklistRegexes=['cat', r'c\w+']), 'dog')
        self.assertEqual(getOut(), 'Please select one of: cat, dog\nThis response is invalid.\nPlease select one of: cat, dog\nThis response is invalid.\nPlease select one of: cat, dog\n')

        # Test postValidateApplyFunc keyword arg.
        # (The blocklist regex will block uppercase responses, but the
        # postValidateApplyFunc will convert it to uppercase.)
        pauseThenType('CAT\ncat\n')
        self.assertEqual(pyip.inputChoice(['cat', 'dog'], blocklistRegexes=['[A-Z]+'], postValidateApplyFunc=str.upper), 'CAT')
        self.assertEqual(getOut(), 'Please select one of: cat, dog\nThis response is invalid.\nPlease select one of: cat, dog\n')

        # Test strip keyword arg
        pauseThenType('   cat    \n')
        self.assertEqual(pyip.inputChoice(['cat', 'dog']), 'cat')
        self.assertEqual(getOut(), 'Please select one of: cat, dog\n')

        pauseThenType(' cat \ncat\n')
        self.assertEqual(pyip.inputChoice(['cat', 'dog'], strip=False), 'cat')
        self.assertEqual(getOut(), "Please select one of: cat, dog\n' cat ' is not a valid choice.\nPlease select one of: cat, dog\n")

        pauseThenType('xxxcat\n')
        self.assertEqual(pyip.inputChoice(['cat', 'dog'], strip='x'), 'cat')
        self.assertEqual(getOut(), 'Please select one of: cat, dog\n')

        pauseThenType('xyzcatxxx\n')
        self.assertEqual(pyip.inputChoice(['cat', 'dog'], strip='xyz'), 'cat')
        self.assertEqual(getOut(), 'Please select one of: cat, dog\n')


if __name__ == '__main__':
    unittest.main()
    sys.stdout = originalStdout # Restore stdout.
