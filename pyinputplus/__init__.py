"""PyInputPlus
By Al Sweigart al@inventwithpython.com

A Python 2 and 3 module to provide input()- and raw_input()-like functions with additional validation features.

This module relies heavily on PySimpleValidate (also by Al) for the actual
validation. PyInputPlus provides interaction with the user through stdin/stdout
while PySimpleValidate provides the functions that validate the user's input.
"""

# TODO - Figure out a way to get doctests to work with input().

from __future__ import absolute_import, division, print_function

import time

import pysimplevalidate as pysv


__version__ = '0.1.0'

FUNC_TYPE = type(lambda x: x)
METHOD_DESCRIPTOR_TYPE = type(str.upper)

class PyInputPlusException(Exception):
    """Base class for exceptions raised when PyInputPlus functions encounter
    a problem. If PyInputPlus raises an exception that isn't this class, that
    indicates a bug in the module."""
    pass

class TimeoutException(Exception):
    """This exception is raised when the user has failed to enter valid input
    before the timeout period."""
    pass

class RetryLimitException(Exception):
    """This exception is raised when the user has failed to enter valid input
    within the limited number of tries given."""
    pass

"""
TODO - This can be added to a future version if needed.
class MetaDataEntry(object):
    def __init__(self):
        self.startTime = None
        self.endTime = None
        self.time = None
        self.original = None
        self.userInput = None
"""

def _checkLimitAndTimeout(default, startTime, timeout, tries, limit):
    """Returns the default argument if the user has timed out or exceeded the
    limit for number of responses. If default is None and the user has timed
    out/exceeded the limit, a TimeoutException or RetryLimitException is raised,
    respectively.

    if the user enters valid input, but has exceeded the time limit, the user's input is discarded and `default` or `None` is returned.

    Args:
        `default` (str): A string to return as the user input if the user has timed out/exceeded the limit.
        `startTime` (float): The Unix epoch time when the input function was first called.
        `timeout` (float): A number of seconds the user has to enter valid input.
        `tries` (int): The number of times the user has already tried to enter valid input.
        `limit` (int): The number of tries the user has to enter valid input.
    """

    # Check if the user has timed out.

    # NOTE: We return exceptions instead of raising them so the caller
    # won't cause a "During handling of the above exception" message.
    if timeout is not None and startTime + timeout < time.time():
        if default is not None:
            return default
        else:
            return TimeoutException()

    if limit is not None and tries >= limit:
        if default is not None:
            return default
        else:
            return RetryLimitException()

    return None # Returns None if the caller should do nothing.


def _genericInput(prompt='', default=None, timeout=None, limit=None,
                  applyFunc=None, validationFunc=None, postValidateApplyFunc=None):
    """This function is used by the various input*() functions to handle the
    common operations of each input function: displaying prompts, collecting input,
    handling timeouts, etc.

    See the input*() functions for examples of usage.

    Args:
        `prompt` (str): The text to display before each prompt for user input. Identical to the prompt argument for Python's `raw_input()` and `input()` functions.
        `default` (str, None): A default value to use should the user time out or exceed the number of tries to enter valid input.
        `timeout` (int, float): The number of seconds since the first prompt for input after which a TimeoutException is raised the next time the user enters input.
        `limit` (int): The number of tries the user has to enter valid input before the default value is returned.
        `applyFunc` (Callable, None): An optional function that is passed the user's input, and returns the new value to use as the input.
        `validationFunc` (Callable): A function that is passed the user's input value, which raises an exception if the input isn't valid. (The return value of this function is ignored.)
        `postValidateApplyFunc` (Callable): An optional function that is passed the user's input after it has passed validation, and returns a transformed version for the input*() function to return.
    """

    # NOTE: _genericInput() always returns a string. Any type casting must be done by the caller.

    # Validate the parameters.
    if not isinstance(prompt, str):
        raise PyInputPlusException('prompt argument must be a str')
    if not isinstance(default, (str, type(None))):
        raise PyInputPlusException('default argument must be a str or None')
    if not isinstance(timeout, (int, float, type(None))):
        raise PyInputPlusException('timeout argument must be an int or float')
    if not isinstance(limit, (int, type(None))):
        raise PyInputPlusException('limit argument must be an int')
    if not isinstance(validationFunc, (FUNC_TYPE, METHOD_DESCRIPTOR_TYPE)):
        raise PyInputPlusException('validationFunc argument must be a function')
    if not isinstance(applyFunc, (FUNC_TYPE, METHOD_DESCRIPTOR_TYPE, type(None))):
        raise PyInputPlusException('applyFunc argument must be a function or None')
    if not isinstance(postValidateApplyFunc, (FUNC_TYPE, METHOD_DESCRIPTOR_TYPE, type(None))):
        raise PyInputPlusException('postValidateApplyFunc argument must be a function or None')

    startTime = time.time()
    tries = 0

    while True:
        # Get the user input.
        print(prompt, end='')
        userInput = input()
        tries += 1

        # Transform the user input with the applyFunc function.
        if applyFunc is not None:
            userInput = applyFunc(userInput)

        # Run the validation function.
        checkResult = None
        try:
            userInput = validationFunc(userInput) # If validation fails, this function will raise an exception.
        except Exception as exc:
            # Check if they have timed out or reach the retry limit.
            checkResult = _checkLimitAndTimeout(default=default, startTime=startTime, timeout=timeout, tries=tries, limit=limit)
            if checkResult is not None and not isinstance(checkResult, Exception):
                return checkResult
            elif checkResult is None: # None indicates there was no timeout or retry limit reached.
                print(exc) # Display the message of the exception.
                continue
        if isinstance(checkResult, Exception):
            raise checkResult # Raise the Timeout/RetryLimit exception.

        if postValidateApplyFunc is not None:
            return postValidateApplyFunc(userInput)
        else:
            return userInput


def inputStr(prompt='', default=None, blank=False, timeout=None, limit=None,
             strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None):
    """Prompts the user to enter a string. This is similar to Python's input()
    and raw_input() functions, but with PyInputPlus's additional features
    such as timeouts, retry limits, stripping, whitelist/blacklist, etc.

    >>> result = inputStr('Enter name> ')
    Enter name> Al
    >>> result
    'Al'

    >>> result = inputStr('Enter name> ', blacklistRegexes=['^Al$'])
    Enter name> Al
    This response is invalid.
    Enter name> Bob
    >>> result
    'Bob'
    """

    # Validate the arguments passed to pysv.validateNum().
    pysv._validateGenericParameters(blank, strip, whitelistRegexes, blacklistRegexes)

    validationFunc = lambda value: pysv._prevalidationCheck(value, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    result = _genericInput(prompt=prompt, default=default, timeout=timeout,
                           limit=limit, applyFunc=applyFunc,
                           postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)
    return result[1]


def inputNum(prompt='', default=None, blank=False, timeout=None, limit=None,
             strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None,
             min=None, max=None, lessThan=None, greaterThan=None):
    """Prompts the user to enter a number, either an integer or a floating-point
    value. Returns an int or float value (depending on if the user entered a
    decimal in their input.)

    >>> result = inputNum()
    forty two
    'forty two' is not a number.
    42
    >>> result
    42

    >>> result = inputNum()
    9
    >>> type(result)
    <class 'int'>
    >>> result = inputNum()
    9.0
    >>> type(result)
    <class 'float'>

    >>> result = inputNum(min=4)
    3
    Input must be at minimum 4.
    4
    >>> result
    4

    >>> result = inputNum(greaterThan=4)
    4
    Input must be greater than 4.
    4.1
    >>> result
    4.1
    """

    # Validate the arguments passed to pysv.validateNum().
    pysv._validateParamsFor_validateNum(min=min, max=max, lessThan=lessThan, greaterThan=greaterThan)

    validationFunc = lambda value: pysv.validateNum(value, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, min=min, max=max, lessThan=lessThan, greaterThan=greaterThan, _numType='num')

    return _genericInput(prompt=prompt, default=default, timeout=timeout,
                           limit=limit, applyFunc=applyFunc,
                           postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)



def inputInt(prompt='', default=None, blank=False, timeout=None, limit=None,
             strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None,
             min=None, max=None, lessThan=None, greaterThan=None):

    # Validate the arguments passed to pysv.validateNum().
    pysv._validateParamsFor_validateNum(min=min, max=max, lessThan=lessThan, greaterThan=greaterThan)

    validationFunc = lambda value: pysv.validateNum(value, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, min=min, max=max, lessThan=lessThan, greaterThan=greaterThan, _numType='int')

    result = _genericInput(prompt=prompt, default=default, timeout=timeout,
                           limit=limit, applyFunc=applyFunc,
                           postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)

    return int(float(result)) # In case result is a string like '3.2', convert to float first.


def inputFloat(prompt='', default=None, blank=False, timeout=None, limit=None,
             strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None,
             min=None, max=None, lessThan=None, greaterThan=None):

    # Validate the arguments passed to pysv.validateNum().
    pysv._validateParamsFor_validateNum(min=min, max=max, lessThan=lessThan, greaterThan=greaterThan)

    validationFunc = lambda value: pysv.validateNum(value, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, min=min, max=max, lessThan=lessThan, greaterThan=greaterThan, _numType='float')

    result = _genericInput(prompt=prompt, default=default, timeout=timeout,
                           limit=limit, applyFunc=applyFunc,
                           postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)

    return float(result)


def inputChoice(choices, prompt='_default', default=None, blank=False, timeout=None, limit=None,
                strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None,
                caseSensitive=False):

    # Validate the arguments passed to pysv.validateChoice().
    pysv._validateParamsFor_validateChoice(choices, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes,
                   numbered=False, lettered=False, caseSensitive=caseSensitive)

    validationFunc = lambda value: pysv.validateChoice(value, choices=choices, blank=blank,
                    strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, numbered=False, lettered=False,
                    caseSensitive=False)

    if prompt == '_default':
        prompt = 'Please select one of: %s.\n' % (', '.join(choices))

    return _genericInput(prompt=prompt, default=default, timeout=timeout,
                         limit=limit, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


def inputMenu(choices, prompt='_default', default=None, blank=False, timeout=None, limit=None,
              strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None,
              numbered=False, lettered=False, caseSensitive=False):

    # Validate the arguments passed to pysv.validateChoice().
    pysv._validateParamsFor_validateChoice(choices, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes,
                   numbered=numbered, lettered=lettered, caseSensitive=caseSensitive)

    validationFunc = lambda value: pysv.validateChoice(value, choices=choices, blank=blank,
                    strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes,
                    numbered=numbered, lettered=lettered, caseSensitive=False)

    if prompt == '_default':
        prompt = 'Please select one of the following:\n'
        if numbered:
            prompt += '\n'.join([str(i + 1) + '. ' + choices[i] for i in range(len(choices))])
        elif lettered:
            prompt += '\n'.join([chr(65 + i) + '. ' + choices[i] for i in range(len(choices))])
        else:
            prompt += '\n'.join(['* ' + choice for choice in choices])
        prompt += '\n'

    result = _genericInput(prompt=prompt, default=default, timeout=timeout,
                           limit=limit, applyFunc=applyFunc,
                           postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)

    # Since `result` could be a number or letter of the option selected, we
    # need to find the string in `choices` to return. Call pysv.validateChoice()
    # again to get it.
    return pysv.validateChoice(result, choices, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes,
                   numbered=numbered, lettered=lettered, caseSensitive=caseSensitive)


def inputDate(prompt='', formats=None, default=None, blank=False, timeout=None, limit=None,
             strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None):

    if formats is None:
        formats = ('%m/%d/%Y', '%m/%d/%y', '%Y/%m/%d', '%y/%m/%d', '%x')

    validationFunc = lambda value: pysv.validateDate(value, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, formats=formats)

    return _genericInput(prompt=prompt, default=default, timeout=timeout,
                         limit=limit, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


def inputDatetime(prompt='', default=None, blank=False, timeout=None, limit=None,
				  strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None,
				  formats=('%m/%d/%Y %H:%M:%S', '%m/%d/%y %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%y/%m/%d %H:%M:%S', '%x %H:%M:%S',
                   '%m/%d/%Y %H:%M', '%m/%d/%y %H:%M', '%Y/%m/%d %H:%M', '%y/%m/%d %H:%M', '%x %H:%M',
                   '%m/%d/%Y %H:%M:%S', '%m/%d/%y %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%y/%m/%d %H:%M:%S', '%x %H:%M:%S')):

    validationFunc = lambda value: pysv.validateDatetime(value, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, formats=formats)

    return _genericInput(prompt=prompt, default=default, timeout=timeout,
                         limit=limit, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


def inputTime(prompt='', default=None, blank=False, timeout=None, limit=None,
			  strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None,
			  formats=('%H:%M:%S', '%H:%M', '%X')):

    validationFunc = lambda value: pysv.validateTime(value, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, formats=formats)

    return _genericInput(prompt=prompt, default=default, timeout=timeout,
                         limit=limit, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


def inputFilename(prompt='', default=None, blank=False, timeout=None, limit=None,
				  strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None,
				  mustExist=False):

    validationFunc = lambda value: pysv.validateFilename(value, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, mustExist=mustExist)

    return _genericInput(prompt=prompt, default=default, timeout=timeout,
                         limit=limit, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


def inputFilepath(prompt='', default=None, blank=False, timeout=None, limit=None,
				  strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None,
				  mustExist=False):

    validationFunc = lambda value: pysv.validateFilepath(value, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, mustExist=mustExist)

    return _genericInput(prompt=prompt, default=default, timeout=timeout,
                         limit=limit, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


def inputIpAddr(prompt='', default=None, blank=False, timeout=None, limit=None,
				strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None):

    validationFunc = lambda value: pysv.validateIpAddr(value, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    return _genericInput(prompt=prompt, default=default, timeout=timeout,
                         limit=limit, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


def inputRegex(regex, flags=0, prompt='', default=None, blank=False, timeout=None, limit=None,
			   strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None):

    validationFunc = lambda value: pysv.validateRegex(value, regex='', flags=0, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    return _genericInput(prompt=prompt, default=default, timeout=timeout,
                         limit=limit, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


def inputLiteralRegex(prompt='', default=None, blank=False, timeout=None, limit=None,
				      strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None):

    validationFunc = lambda value: pysv.validateRegex(value, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    return _genericInput(prompt=prompt, default=default, timeout=timeout,
                         limit=limit, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


def inputURL(prompt='', default=None, blank=False, timeout=None, limit=None,
		     strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None):

    validationFunc = lambda value: pysv.validateURL(value, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    return _genericInput(prompt=prompt, default=default, timeout=timeout,
                         limit=limit, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


def inputYesNo(prompt='', yesVal='yes', noVal='no', caseSensitive=False,
			   default=None, blank=False, timeout=None, limit=None,
			   strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None):
    """Prompts the user to enter a yes/no response. The user can also enter
    `'y'` or `'n'`.

    """
    validationFunc = lambda value: pysv.validateYesNo(value, yesVal=yesVal, noVal=noVal, caseSensitive=caseSensitive, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    result = _genericInput(prompt=prompt, default=default, timeout=timeout,
                           limit=limit, applyFunc=applyFunc,
                           postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)

    # If validation passes, return the value that pysv.validateYesNo() returned rather than necessarily what the user typed in.
    return pysv.validateYesNo(result, yesVal=yesVal, noVal=noVal, caseSensitive=caseSensitive, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)



def inputBool(prompt='', trueVal='True', falseVal='False', caseSensitive=False,
               default=None, blank=False, timeout=None, limit=None,
               strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None):
    """Prompts the user to enter a True/False response. The user can also enter
    `'t'` or `'f'`. Returns a boolean value.

    """
    validationFunc = lambda value: pysv.validateYesNo(value, yesVal=trueVal, noVal=falseVal, caseSensitive=caseSensitive, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    result = _genericInput(prompt=prompt, default=default, timeout=timeout,
                           limit=limit, applyFunc=applyFunc,
                           postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)

    # If the user entered a response that is compatible with trueVal or falseVal exactly, get those particular exact strings.
    result = pysv.validateYesNo(result, yesVal=trueVal, noVal=falseVal, caseSensitive=caseSensitive, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    # Return a bool value instead of a string.
    if result == trueVal:
        return True
    elif result == falseVal:
        return False
    else:
        return result # Return `result` if a blank or whitelisted value was entered, or postValidateApplyFunc() transformed the value.

def inputName(prompt='', default=None, blank=False, timeout=None, limit=None,
			  strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None):
    raise NotImplementedError()


def inputAddress(prompt='', default=None, blank=False, timeout=None, limit=None,
				 strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None):
    raise NotImplementedError()


def inputState(prompt='', default=None, blank=False, timeout=None, limit=None,
			   strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None):

    validationFunc = lambda value: pysv.validateState(value, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    return _genericInput(prompt=prompt, default=default, timeout=timeout,
                         limit=limit, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


def inputZip(prompt='', default=None, blank=False, timeout=None, limit=None,
		     strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None):

    validationFunc = lambda value: pysv.validateZip(value, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    return _genericInput(prompt=prompt, default=default, timeout=timeout,
                         limit=limit, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


def inputPhone(prompt='', default=None, blank=False, timeout=None, limit=None,
			   strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None):

    validationFunc = lambda value: pysv.validatePhone(value, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    return _genericInput(prompt=prompt, default=default, timeout=timeout,
                         limit=limit, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


#if __name__ == '__main__':
#    import doctest
#    doctest.testmod()
