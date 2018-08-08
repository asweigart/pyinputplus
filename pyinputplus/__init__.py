# PyInputPlus
# By Al Sweigart
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


def _genericInput(prompt='', default=None, blank=False, timeout=None, limit=None,
                  strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None,
                  validationFunc=None, preamble=None):
    # NOTE: _genericInput() always returns a string. Any type casting must be done by the caller.

    # Validate the parameters.
    pysv._validateGenericParameters(blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    if not isinstance(prompt, str):
        raise PyInputPlusException('prompt argument must be a str')
    if not isinstance(default, (str, type(None))):
        raise PyInputPlusException('default argument must be a str or None')
    blank = bool(blank)
    if not isinstance(timeout, (int, float, type(None))):
        raise PyInputPlusException('timeout argument must be an int or float')
    if not isinstance(limit, (int, type(None))):
        raise PyInputPlusException('limit argument must be an int')
    if not isinstance(strip, (str, type(None), bool)):
        raise PyInputPlusException('strip argument must be a str, None, or bool')
    if not isinstance(validationFunc, (FUNC_TYPE, METHOD_DESCRIPTOR_TYPE)):
        raise PyInputPlusException('validationFunc argument must be a function')
    if not isinstance(applyFunc, (FUNC_TYPE, METHOD_DESCRIPTOR_TYPE, type(None))):
        raise PyInputPlusException('applyFunc argument must be a function')

    startTime = time.time()
    tries = 0

    while True:
        # Get the user input.
        #import pdb;pdb.set_trace()
        if preamble is not None:
            print(preamble, end=''
                )
        print(prompt, end='')
        userInput = input()
        assert userInput is not None
        tries += 1

        # Strip the user input according to the strip parameter.
        if strip is not None:
            if strip is True:
                userInput = userInput.strip()
            elif strip is not False:
                userInput = userInput.strip(strip)

        # Check if we should return the default value.
        if userInput == '' and default is not None:
            return default

        # Transform the user input with the applyFunc function.
        if applyFunc is not None:
            userInput = applyFunc(userInput)

        checkResult = None

        # Run the validation function.
        try:
            validationFunc(userInput) # If validation fails, this function will raise an exception.
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
    def validationFunc(value):
        return pysv._handleBlankValues(value, blank=blank, strip=strip) in (True, None)

    return _genericInput(prompt=prompt, default=default, blank=blank, timeout=timeout,
                         limit=limit, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


def inputNum(prompt='', default=None, blank=False, timeout=None, limit=None,
             strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None,
             min=None, max=None, lessThan=None, greaterThan=None):

    # Validate the arguments passed to pysv.validateNum().
    pysv._validateParamsFor_validateNum(min=min, max=max, lessThan=lessThan, greaterThan=greaterThan)

    validationFunc = lambda value: pysv.validateNum(value, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, min=min, max=max, lessThan=lessThan, greaterThan=greaterThan, _numType='num') in (True, None)

    result = _genericInput(prompt=prompt, default=default, blank=blank, timeout=timeout,
                           limit=limit, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, applyFunc=applyFunc,
                           postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)

    if whitelistRegexes is not None and result in whitelistRegexes:
        return result

    if '.' in result:
        return float(result)
    else:
        return int(result)


def inputInt(prompt='', default=None, blank=False, timeout=None, limit=None,
             strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None,
             min=None, max=None, lessThan=None, greaterThan=None):

    # Validate the arguments passed to pysv.validateNum().
    pysv._validateParamsFor_validateNum(min=min, max=max, lessThan=lessThan, greaterThan=greaterThan)

    validationFunc = lambda value: pysv.validateNum(value, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, min=min, max=max, lessThan=lessThan, greaterThan=greaterThan, _numType='int') in (True, None)

    result = _genericInput(prompt=prompt, default=default, blank=blank, timeout=timeout,
                           limit=limit, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, applyFunc=applyFunc,
                           postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)

    if whitelistRegexes is not None and result in whitelistRegexes:
        return result

    return int(float(result)) # In case result is a string like '3.2', convert to float first.


def inputFloat(prompt='', default=None, blank=False, timeout=None, limit=None,
             strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None,
             min=None, max=None, lessThan=None, greaterThan=None):

    # Validate the arguments passed to pysv.validateNum().
    pysv._validateParamsFor_validateNum(min=min, max=max, lessThan=lessThan, greaterThan=greaterThan)

    validationFunc = lambda value: pysv.validateNum(value, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, min=min, max=max, lessThan=lessThan, greaterThan=greaterThan, _numType='float') in (True, None)

    result = _genericInput(prompt=prompt, default=default, blank=blank, timeout=timeout,
                         limit=limit, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)

    if whitelistRegexes is not None and result in whitelistRegexes:
        return result

    return float(result)


def inputChoice(choices, prompt='', default=None, blank=False, timeout=None, limit=None,
                strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None,
                preamble='_default', numbered=False, lettered=False, caseSensitive=False):

    # Validate the arguments passed to pysv.validateChoice().
    pysv._validateParamsFor_validateChoice(choices, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes,
                   numbered=numbered, lettered=lettered, caseSensitive=caseSensitive)

    def validationFunc(value):
        return pysv.validateChoice(value, choices=choices, blank=blank,
                    strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, numbered=False, lettered=False,
                    caseSensitive=False)

    if preamble == '_default':
        preamble = 'Please select one of: %s.\n' % (', '.join(choices))

    return _genericInput(prompt=prompt, default=default, blank=blank, timeout=timeout,
                         limit=limit, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc,
                         preamble=preamble)


def inputMenu(choices, prompt='', default=None, blank=False, timeout=None, limit=None,
                strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None,
                preamble='_default', numbered=False, lettered=False, caseSensitive=False):

    # Validate the arguments passed to pysv.validateChoice().
    pysv._validateParamsFor_validateChoice(choices, blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes,
                   numbered=numbered, lettered=lettered, caseSensitive=caseSensitive)

    def validationFunc(value):
        return pysv.validateChoice(value, choices=choices, blank=blank,
                    strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, numbered=False, lettered=False,
                    caseSensitive=False)

    if preamble == '_default':
        preamble = 'Please select one of the following:\n'
        if numbered:
            preamble += '\n'.join([str(i + 1) + '. ' + choices[i] for i in range(len(choices))])
        elif lettered:
            preamble += '\n'.join([chr(65 + i) + '. ' + choices[i] for i in range(len(choices))])
        else:
            preamble += '\n'.join(['* ' + choice for choice in choices])
        preamble += '\n'

    return _genericInput(prompt=prompt, default=default, blank=blank, timeout=timeout,
                         limit=limit, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc,
                         preamble=preamble)


def inputDate(prompt='', formats=None, default=None, blank=False, timeout=None, limit=None,
             strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None):

    if formats is None:
        formats = ('%m/%d/%Y', '%m/%d/%y', '%Y/%m/%d', '%y/%m/%d', '%x')

    def validationFunc(value):
        return pysv.validateDate(value, blank=blank, strip=strip,
                                 whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, formats=formats)

    return _genericInput(prompt=prompt, default=default, blank=blank, timeout=timeout,
                         limit=limit, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


def inputDatetime(prompt='', default=None, blank=False, timeout=None, limit=None,
				  strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None,
				  formats=('%m/%d/%Y %H:%M:%S', '%m/%d/%y %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%y/%m/%d %H:%M:%S', '%x %H:%M:%S',
                   '%m/%d/%Y %H:%M', '%m/%d/%y %H:%M', '%Y/%m/%d %H:%M', '%y/%m/%d %H:%M', '%x %H:%M',
                   '%m/%d/%Y %H:%M:%S', '%m/%d/%y %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%y/%m/%d %H:%M:%S', '%x %H:%M:%S')):

    def validationFunc(value):
        return pysv.validateDatetime(value, blank=blank, strip=strip,
                                     whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, formats=formats)

    return _genericInput(prompt=prompt, default=default, blank=blank, timeout=timeout,
                         limit=limit, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


def inputTime(prompt='', default=None, blank=False, timeout=None, limit=None,
			  strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None,
			  formats=('%H:%M:%S', '%H:%M', '%X')):

    def validationFunc(value):
        return pysv.validateTime(value, blank=blank, strip=strip,
                                 whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, formats=formats)

    return _genericInput(prompt=prompt, default=default, blank=blank, timeout=timeout,
                         limit=limit, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


def inputFilename(prompt='', default=None, blank=False, timeout=None, limit=None,
				  strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None,
				  mustExist=False):

    def validationFunc(value):
        return pysv.validateFilename(value, blank=blank, strip=strip,
                                     whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, mustExist=mustExist)

    return _genericInput(prompt=prompt, default=default, blank=blank, timeout=timeout,
                         limit=limit, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


def inputFilepath(prompt='', default=None, blank=False, timeout=None, limit=None,
				  strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None,
				  mustExist=False):

    def validationFunc(value):
        return pysv.validateFilepath(value, blank=blank, strip=strip,
                                     whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, mustExist=mustExist)

    return _genericInput(prompt=prompt, default=default, blank=blank, timeout=timeout,
                         limit=limit, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


def inputIpAddr(prompt='', default=None, blank=False, timeout=None, limit=None,
				strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None):

    def validationFunc(value):
        return pysv.validateIpAddr(value, blank=blank, strip=strip,
                                   whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    return _genericInput(prompt=prompt, default=default, blank=blank, timeout=timeout,
                         limit=limit, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


def inputRegex(regex, flags=0, prompt='', default=None, blank=False, timeout=None, limit=None,
			   strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None):

    def validationFunc(value):
        return pysv.validateRegex(value, regex='', flags=0,
        				blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    return _genericInput(prompt=prompt, default=default, blank=blank, timeout=timeout,
                         limit=limit, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


def inputLiteralRegex(prompt='', default=None, blank=False, timeout=None, limit=None,
				      strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None):

    def validationFunc(value):
        return pysv.validateRegex(value, blank=blank, strip=strip,
                                  whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    return _genericInput(prompt=prompt, default=default, blank=blank, timeout=timeout,
                         limit=limit, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


def inputURL(prompt='', default=None, blank=False, timeout=None, limit=None,
		     strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None):

    def validationFunc(value):
        return pysv.validateURL(value, blank=blank, strip=strip,
                                whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)


    return _genericInput(prompt=prompt, default=default, blank=blank, timeout=timeout,
                         limit=limit, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


def inputYesNo(prompt='', yes='yes', no='no', caseSensitive=False,
			   default=None, blank=False, timeout=None, limit=None,
			   strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None):

    def validationFunc(value):
        return pysv.validateYesNo(value, yes=yes, no=no, caseSensitive=caseSensitive,
        						blank=blank, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    result = _genericInput(prompt=prompt, default=default, blank=blank, timeout=timeout,
                         limit=limit, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)
    return result[0].upper()


def inputName(prompt='', default=None, blank=False, timeout=None, limit=None,
			  strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None):

    def validationFunc(value):
        return pysv.validateName(value, blank=blank, strip=strip,
                                 whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    return _genericInput(prompt=prompt, default=default, blank=blank, timeout=timeout,
                         limit=limit, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


def inputAddress(prompt='', default=None, blank=False, timeout=None, limit=None,
				 strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None):

    def validationFunc(value):
        return pysv.validateAddress(value, blank=blank, strip=strip,
                                    whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    return _genericInput(prompt=prompt, default=default, blank=blank, timeout=timeout,
                         limit=limit, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


def inputState(prompt='', default=None, blank=False, timeout=None, limit=None,
			   strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None):

    def validationFunc(value):
        return pysv.validateState(value, blank=blank, strip=strip,
                                  whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    return _genericInput(prompt=prompt, default=default, blank=blank, timeout=timeout,
                         limit=limit, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


def inputZip(prompt='', default=None, blank=False, timeout=None, limit=None,
		     strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None):

    def validationFunc(value):
        return pysv.validateZip(value, blank=blank, strip=strip,
                                whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    return _genericInput(prompt=prompt, default=default, blank=blank, timeout=timeout,
                         limit=limit, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)


def inputPhone(prompt='', default=None, blank=False, timeout=None, limit=None,
			   strip=True, whitelistRegexes=None, blacklistRegexes=None, applyFunc=None, postValidateApplyFunc=None):

    def validationFunc(value):
        return pysv.validatePhone(value, blank=blank, strip=strip,
                                  whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes)

    return _genericInput(prompt=prompt, default=default, blank=blank, timeout=timeout,
                         limit=limit, strip=strip, whitelistRegexes=whitelistRegexes, blacklistRegexes=blacklistRegexes, applyFunc=applyFunc,
                         postValidateApplyFunc=postValidateApplyFunc, validationFunc=validationFunc)
