"""PyInputPlus by Al Sweigart al@inventwithpython.com

A Python 2 and 3 module to provide input()- and raw_input()-like functions with additional validation features.
"""

# TODO - Figure out a way to get doctests to work with input().

# TODO - Possible future feature: using cmdline for tab-completion and history.

from __future__ import absolute_import, division, print_function

import time
from typing import Union, Any, Optional, Callable, Sequence, Pattern

import pysimplevalidate as pysv  # type: ignore
import stdiomask  # type: ignore

__version__ = "0.2.12"  # type: str


class PyInputPlusException(Exception):
    """
    Base class for exceptions raised when PyInputPlus functions
    encounter a problem. If PyInputPlus raises an exception that isn't
    this class, that indicates a bug in the module.
    """

    pass


class ValidationException(PyInputPlusException):
    """
    This exception is raised when a ``validate*()`` function is called and
    the input fails validation. For example, ``validateInt('four')`` will
    raise this. This exception class is for all the PySimpleValidate
    wrapper functions (``validateStr()``, etc.) that PyInputPlus provides
    so that ``pyinputplus.ValidationException`` is raised instead of
    ``pysimplevalidate.ValidationException``.
    """

    pass


class TimeoutException(Exception):
    """
    This exception is raised when the user has failed to enter valid
    input before the timeout period.
    """

    pass


class RetryLimitException(Exception):
    """
    This exception is raised when the user has failed to enter valid
    input within the limited number of tries given.
    """

    pass


def parameters():
    """
    Common parameters for all ``input*()`` functions in PyInputPlus:

    * ``prompt`` (str): The text to display before each prompt for user input. Identical to the prompt argument for Python's ``raw_input()`` and ``input()`` functions.
    * ``default`` (str, None): A default value to use should the user time out or exceed the number of tries to enter valid input.
    * ``blank`` (bool): If ``True``, a blank string will be accepted. Defaults to ``False``.
    * ``timeout`` (int, float): The number of seconds since the first prompt for input after which a ``TimeoutException`` is raised the next time the user enters input.
    * ``limit`` (int): The number of tries the user has to enter valid input before the default value is returned.
    * ``strip`` (bool, str, None): If ``None``, whitespace is stripped from value. If a str, the characters in it are stripped from value. If ``False``, nothing is stripped.
    * ``allowlistRegexes`` (Sequence, None): A sequence of regex str that will explicitly pass validation.
    * ``blocklistRegexes`` (Sequence, None): A sequence of regex str or ``(regex_str, error_msg_str)`` tuples that, if matched, will explicitly fail validation.
    * ``applyFunc`` (Callable, None): An optional function that is passed the user's input, and returns the new value to use as the input.
    * ``postValidateApplyFunc`` (Callable, None): An optional function that is passed the user's input after it has passed validation, and returns a transformed version for the ``input*()`` function to return.
    """
    pass  # This "function" only exists so you can call `help()`


def _checkLimitAndTimeout(startTime, timeout, tries, limit):
    # type: (float, Optional[float], int, Optional[int]) -> Union[None, TimeoutException, RetryLimitException]
    """Returns a ``TimeoutException`` or ``RetryLimitException`` if the user has
    exceeded those limits, otherwise returns ``None``.

    * ``startTime`` (float): The Unix epoch time when the input function was first called.
    * ``timeout`` (float): A number of seconds the user has to enter valid input.
    * ``tries`` (int): The number of times the user has already tried to enter valid input.
    * ``limit`` (int): The number of tries the user has to enter valid input.
    """

    # NOTE: We return exceptions instead of raising them so the caller
    # can still display the original validation exception message.
    if timeout is not None and startTime + timeout < time.time():
        return TimeoutException()

    if limit is not None and tries >= limit:
        return RetryLimitException()

    return None  # Returns None if there was neither a timeout or limit exceeded.


def _genericInput(
    prompt="",
    default=None,
    timeout=None,
    limit=None,
    applyFunc=None,
    validationFunc=None,
    postValidateApplyFunc=None,
    passwordMask=None,
):
    # type: (str, Any, Optional[float], Optional[int], Optional[Callable], Optional[Callable], Optional[Callable], Optional[str]) -> Any
    """This function is used by the various input*() functions to handle the
    common operations of each input function: displaying prompts, collecting input,
    handling timeouts, etc.

    See the ``input*()`` functions for examples of usage.

    Note that the user must provide valid input within both the timeout limit
    AND the retry limit, otherwise ``TimeoutException`` or ``RetryLimitException`` is
    raised (unless there's a default value provided, in which case the default
    value is returned.)

    Note that the ``postValidateApplyFunc()`` is not called on the default value,
    if a default value is provided.

    Run ``help(pyinputplus.parameters)`` for an explanation of the common parameters.

    * ``passwordMask`` (str, None): An optional argument. If not ``None``, this ``getpass.getpass()`` is used instead of
    """

    # NOTE: _genericInput() can return any type of value. Any type casting must be done by the caller.
    # Validate the parameters.
    if not isinstance(prompt, str):
        raise PyInputPlusException("prompt argument must be a str")
    if not isinstance(timeout, (int, float, type(None))):
        raise PyInputPlusException("timeout argument must be an int or float")
    if not isinstance(limit, (int, type(None))):
        raise PyInputPlusException("limit argument must be an int")
    if not callable(validationFunc):
        raise PyInputPlusException("validationFunc argument must be a function")
    if not (callable(applyFunc) or applyFunc is None):
        raise PyInputPlusException("applyFunc argument must be a function or None")
    if not (callable(postValidateApplyFunc) or postValidateApplyFunc is None):
        raise PyInputPlusException("postValidateApplyFunc argument must be a function or None")
    if passwordMask is not None and (not isinstance(passwordMask, str) or len(passwordMask) > 1):
        raise PyInputPlusException("passwordMask argument must be None or a single-character string.")

    startTime = time.time()
    tries = 0

    while True:
        # Get the user input.
        print(prompt, end="")
        if passwordMask is None:
            userInput = input()
        else:
            userInput = stdiomask.getpass(prompt="", mask=passwordMask)
        tries += 1

        # Transform the user input with the applyFunc function.
        if applyFunc is not None:
            userInput = applyFunc(userInput)

        # Run the validation function.
        try:
            possibleNewUserInput = validationFunc(
                userInput
            )  # If validation fails, this function will raise an exception. Returns an updated value to use as user input (e.g. stripped of whitespace, etc.)
            if possibleNewUserInput is not None:
                userInput = possibleNewUserInput
        except Exception as exc:
            # Check if they have timed out or reach the retry limit. (If so,
            # the TimeoutException/RetryLimitException overrides the validation
            # exception that was just raised.)
            limitOrTimeoutException = _checkLimitAndTimeout(
                startTime=startTime, timeout=timeout, tries=tries, limit=limit
            )

            print(exc)  # Display the message of the validation exception.

            if isinstance(limitOrTimeoutException, Exception):
                if default is not None:
                    # If there was a timeout/limit exceeded, return the default value if there is one.
                    return default
                else:
                    # If there is no default, then raise the timeout/limit exception.
                    raise limitOrTimeoutException
            else:
                # If there was no timeout/limit exceeded, let the user enter input again.
                continue

        # The previous call to _checkLimitAndTimeout() only happens when the
        # user enteres invalid input. Now we should check for a timeout even if
        # the last input was valid.
        if timeout is not None and startTime + timeout < time.time():
            # It doesn't matter that the user entered valid input, they've
            # exceeded the timeout so we either return the default or raise
            # TimeoutException.
            if default is not None:
                return default
            else:
                raise TimeoutException()

        if postValidateApplyFunc is not None:
            return postValidateApplyFunc(userInput)
        else:
            return userInput


def inputStr(
    prompt="",
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
):
    # type: (str, Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable]) -> Any
    """Prompts the user to enter any string input. This is similar to Python's ``input()``
    and ``raw_input()`` functions, but with PyInputPlus's additional features
    such as timeouts, retry limits, stripping, allowlist/blocklist, etc.

    Validation can be performed by the validationFunc argument, which raises
    an exception if the input is invalid. The exception message is used to
    tell the user why the input is invalid.

    Run ``help(pyinputplus.parameters)`` for an explanation of the common parameters.

    >>> result = inputStr('Enter name> ')
    Enter name> Al
    >>> result
    'Al'
    """

    # Validate the arguments passed to pysv.validateNum().
    pysv._validateGenericParameters(blank, strip, allowRegexes, blockRegexes)

    validationFunc = lambda value: pysv._prevalidationCheck(
        value, blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes, excMsg=None,
    )[1]

    return _genericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        applyFunc=applyFunc,
        postValidateApplyFunc=postValidateApplyFunc,
        validationFunc=validationFunc,
    )


def inputCustom(
    customValidationFunc,
    prompt="",
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
):
    # type: (Callable, str, Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable]) -> Any
    """Prompts the user to enter input. This is similar to Python's ``input()``
    and ``raw_input()`` functions, but with PyInputPlus's additional features
    such as timeouts, retry limits, stripping, allowlist/blocklist, etc.

    Validation can be performed by the ``customValidationFunc`` argument, which raises
    an exception if the input is invalid. The exception message is used to
    tell the user why the input is invalid.

    Run ``help(pyinputplus.parameters)`` for an explanation of the common parameters.

    * ``customValidationFunc`` (Callable): A function that is used to validate the input. Validation fails if it raises an exception, and the exception message is displayed to the user.

    >>> def raiseIfUppercase(text):
    ...     if text.isupper():
    ...         raise Exception('Input cannot be uppercase.')
    ...
    >>> inputCustom(raiseIfUppercase)
    HELLO
    Input cannot be uppercase.
    Hello
    'Hello'
    """

    # Validate the arguments passed to pysv.validateNum().
    pysv._validateGenericParameters(blank, strip, allowRegexes, blockRegexes)

    # Our validationFunc argument must also call pysv._prevalidationCheck()
    def validationFunc(value):
        value = pysv._prevalidationCheck(
            value, blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes, excMsg=None,
        )[1]
        return customValidationFunc(value)

    return _genericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        applyFunc=applyFunc,
        postValidateApplyFunc=postValidateApplyFunc,
        validationFunc=validationFunc,
    )


def inputNum(
    prompt="",
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
    min=None,
    max=None,
    greaterThan=None,
    lessThan=None,
):
    # type: (str, Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable], Optional[float], Optional[float], Optional[float], Optional[float]) -> Any

    """Prompts the user to enter a number, either an integer or a floating-point
    value. Returns an int or float value (depending on if the user entered a
    decimal in their input.)

    Run ``help(pyinputplus.parameters)`` for an explanation of the common parameters.

    * ``min`` (None, float): If not ``None``, the minimum accepted numeric value, including the minimum argument.
    * ``max`` (None, float): If not ``None``, the maximum accepted numeric value, including the maximum argument.
    * ``greaterThan`` (None, float): If not ``None``, the minimum accepted numeric value, not including the ``greaterThan`` argument.
    * ``lessThan`` (None, float): If not ``None``, the maximum accepted numeric value, not including the ``lessThan`` argument.

    >>> import pyinputplus as pyip
    >>> response = pyip.inputNum()
    forty two
    'forty two' is not a number.
    42
    >>> response
    42
    >>> response = pyip.inputNum()
    9
    >>> type(response)
    <class 'int'>
    >>> response = pyip.inputNum()
    9.0
    >>> type(response)
    <class 'float'>
    >>> response = pyip.inputNum(min=4)
    3
    Number must be at minimum 4.
    4
    >>> response
    4
    >>> response = pyip.inputNum(greaterThan=4)
    4
    Number must be greater than 4.
    4.1
    >>> response
    4.1
    >>> response = pyip.inputNum(limit=2)
    dog
    'dog' is not a number.
    cat
    'cat' is not a number.
    Traceback (most recent call last):
        ...
    pyinputplus.RetryLimitException
    """

    # Validate the arguments passed to pysv.validateNum().
    pysv._validateParamsFor_validateNum(min=min, max=max, lessThan=lessThan, greaterThan=greaterThan)

    validationFunc = lambda value: pysv.validateNum(
        value,
        blank=blank,
        strip=strip,
        allowRegexes=allowRegexes,
        blockRegexes=blockRegexes,
        min=min,
        max=max,
        lessThan=lessThan,
        greaterThan=greaterThan,
        _numType="num",
    )

    return _genericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        applyFunc=applyFunc,
        postValidateApplyFunc=postValidateApplyFunc,
        validationFunc=validationFunc,
    )


def inputInt(
    prompt="",
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
    min=None,
    max=None,
    lessThan=None,
    greaterThan=None,
):
    # type: (str, Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable], Optional[float], Optional[float], Optional[float], Optional[float]) -> Any
    """Prompts the user to enter an integer value. Returns the integer as an
    int value.

    Run ``help(pyinputplus.parameters)`` for an explanation of the common parameters.

    * ``min`` (None, float): If not ``None``, the minimum accepted numeric value, including the minimum argument.
    * ``max`` (None, float): If not ``None``, the maximum accepted numeric value, including the maximum argument.
    * ``greaterThan`` (None, float): If not ``None``, the minimum accepted numeric value, not including the ``greaterThan`` argument.
    * ``lessThan`` (None, float): If not ``None``, the maximum accepted numeric value, not including the ``lessThan`` argument.

    >>> import pyinputplus as pyip
    >>> response = pyip.inputInt()
    42
    >>> response
    42
    >>> type(response)
    <class 'int'>
    >>> response = pyip.inputInt(min=4)
    4
    >>> response
    4
    >>> response = pyip.inputInt(min=4)
    3
    Number must be at minimum 4.
    -5
    Number must be at minimum 4.
    5
    >>> response
    5
    >>> response = pyip.inputInt(blockRegexes=[r'[13579]$'])
    43
    This response is invalid.
    41
    This response is invalid.
    42
    >>> response
    42
    >>> response = pyip.inputInt()
    42.0
    >>> response
    42
    >>> type(response)
    <class 'int'>
    """
    # Validate the arguments passed to pysv.validateNum().
    pysv._validateParamsFor_validateNum(min=min, max=max, lessThan=lessThan, greaterThan=greaterThan)

    validationFunc = lambda value: pysv.validateNum(
        value,
        blank=blank,
        strip=strip,
        allowRegexes=allowRegexes,
        blockRegexes=blockRegexes,
        min=min,
        max=max,
        lessThan=lessThan,
        greaterThan=greaterThan,
        _numType="int",
    )

    result = _genericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        applyFunc=applyFunc,
        validationFunc=validationFunc,
    )

    try:
        result = int(float(result))
    except ValueError:
        # In case _genericInput() returned the default value or an allowlist value, return that as is instead.
        pass

    if postValidateApplyFunc is None:
        return result
    else:
        return postValidateApplyFunc(result)


def inputFloat(
    prompt="",
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
    min=None,
    max=None,
    lessThan=None,
    greaterThan=None,
):
    # type: (str, Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable], Optional[float], Optional[float], Optional[float], Optional[float]) -> Any
    """Prompts the user to enter a floating point number value.
    Returns the number as a float.

    Run ``help(pyinputplus.parameters)`` for an explanation of the common parameters.

    * ``min`` (None, float): If not ``None``, the minimum accepted numeric value, including the minimum argument.
    * ``max`` (None, float): If not ``None``, the maximum accepted numeric value, including the maximum argument.
    * ``greaterThan`` (None, float): If not ``None``, the minimum accepted numeric value, not including the ``greaterThan`` argument.
    * ``lessThan`` (None, float): If not ``None``, the maximum accepted numeric value, not including the ``lessThan`` argument.

    >>> import pyinputplus as pyip
    >>> response = pyip.inputFloat()
    42
    >>> response
    42.0
    >>> type(response)
    <class 'float'>
    """
    # Validate the arguments passed to pysv.validateNum().
    pysv._validateParamsFor_validateNum(min=min, max=max, lessThan=lessThan, greaterThan=greaterThan)

    validationFunc = lambda value: pysv.validateNum(
        value,
        blank=blank,
        strip=strip,
        allowRegexes=allowRegexes,
        blockRegexes=blockRegexes,
        min=min,
        max=max,
        lessThan=lessThan,
        greaterThan=greaterThan,
        _numType="float",
    )

    result = _genericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        applyFunc=applyFunc,
        validationFunc=validationFunc,
    )

    try:
        result = float(result)
    except ValueError:
        # In case _genericInput() returned the default value or an allowlist value, return that as is instead.
        pass

    if postValidateApplyFunc is None:
        return result
    else:
        return postValidateApplyFunc(result)


def inputChoice(
    choices,
    prompt="_default",
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
    caseSensitive=False,
):
    # type: (Sequence[str], str, Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable], bool) -> Any
    """Prompts the user to enter one of the provided choices.
    Returns the selected choice as a string.

    Run ``help(pyinputplus.parameters)`` for an explanation of the common parameters.

    * ``choices`` (Sequence): A sequence of strings, one of which the user must enter.
    * ``aseSensitive`` (bool): If ``True``, the user must enter a choice that matches the case of the string in choices. Defaults to False.

    >>> import pyinputplus as pyip
    >>> response = pyip.inputChoice(['dog', 'cat'])
    Please select one of: dog, cat
    dog
    >>> response
    'dog'
    >>> response = pyip.inputChoice(['dog', 'cat'])
    Please select one of: dog, cat
    CAT
    >>> response
    'cat'
    >>> response = pyip.inputChoice(['dog', 'cat'])
    Please select one of: dog, cat
    mouse
    'mouse' is not a valid choice.
    Please select one of: dog, cat
    Dog
    >>> response
    'dog'
    """

    # Validate the arguments passed to pysv.validateChoice().
    pysv._validateParamsFor_validateChoice(
        choices,
        blank=blank,
        strip=strip,
        allowRegexes=allowRegexes,
        blockRegexes=blockRegexes,
        numbered=False,
        lettered=False,
        caseSensitive=caseSensitive,
    )

    validationFunc = lambda value: pysv.validateChoice(
        value,
        choices=choices,
        blank=blank,
        strip=strip,
        allowRegexes=allowRegexes,
        blockRegexes=blockRegexes,
        numbered=False,
        lettered=False,
        caseSensitive=False,
    )

    if prompt == "_default":
        prompt = "Please select one of: %s\n" % (", ".join(choices))

    return _genericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        applyFunc=applyFunc,
        postValidateApplyFunc=postValidateApplyFunc,
        validationFunc=validationFunc,
    )


def inputMenu(
    choices,
    prompt="_default",
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
    numbered=False,
    lettered=False,
    caseSensitive=False,
):
    # type: (Sequence[str], str, Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable], bool, bool, bool) -> Any
    """Prompts the user to enter one of the provided choices.
    Also displays a small menu with bulleted, numbered, or lettered options.
    Returns the selected choice as a string.

    Run ``help(pyinputplus.parameters)`` for an explanation of the common parameters.

    >>> import pyinputplus as pyip
    >>> response = pyip.inputMenu(['dog', 'cat'])
    Please select one of the following:
    * dog
    * cat
    DOG
    >>> response
    'dog'
    >>> response = pyip.inputMenu(['dog', 'cat'], numbered=True)
    Please select one of the following:
    1. dog
    2. cat
    2
    >>> response
    'cat'
    >>> response = pyip.inputMenu(['dog', 'cat'], lettered=True)
    Please select one of the following:
    A. dog
    B. cat
    B
    >>> response
    'cat'
    >>> response = pyip.inputMenu(['dog', 'cat'], lettered=True)
    Please select one of the following:
    A. dog
    B. cat
    dog
    >>> response
    'dog'
    >>> import pyinputplus as pyip
    >>> response = pyip.inputMenu(['dog', 'cat'], caseSensitive=True)
    Please select one of the following:
    * dog
    * cat
    Dog
    'Dog' is not a valid choice.
    Please select one of the following:
    * dog
    * cat
    dog
    >>> response
    'dog'
    """
    # Validate the arguments passed to pysv.validateChoice().
    pysv._validateParamsFor_validateChoice(
        choices,
        blank=blank,
        strip=strip,
        allowRegexes=allowRegexes,
        blockRegexes=blockRegexes,
        numbered=numbered,
        lettered=lettered,
        caseSensitive=caseSensitive,
    )

    validationFunc = lambda value: pysv.validateChoice(
        value,
        choices=choices,
        blank=blank,
        strip=strip,
        allowRegexes=allowRegexes,
        blockRegexes=blockRegexes,
        numbered=numbered,
        lettered=lettered,
        caseSensitive=caseSensitive,
    )

    if prompt == "_default":
        prompt = "Please select one of the following:\n"

    if numbered:
        prompt += "\n".join([str(i + 1) + ". " + choices[i] for i in range(len(choices))])
    elif lettered:
        prompt += "\n".join([chr(65 + i) + ". " + choices[i] for i in range(len(choices))])
    else:
        prompt += "\n".join(["* " + choice for choice in choices])
    prompt += "\n"

    result = _genericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        applyFunc=applyFunc,
        validationFunc=validationFunc,
    )

    # Since ``result`` could be a number or letter of the option selected, we
    # need to find the string in ``choices`` to return. Call ``pysv.validateChoice()``
    # again to get it.
    result = pysv.validateChoice(
        result,
        choices,
        blank=blank,
        strip=strip,
        allowRegexes=allowRegexes,
        blockRegexes=blockRegexes,
        numbered=numbered,
        lettered=lettered,
        caseSensitive=caseSensitive,
    )
    if postValidateApplyFunc is None:
        return result
    else:
        return postValidateApplyFunc(result)


def inputDate(
    prompt="",
    formats=None,
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
):
    # type: (str, Union[str, Sequence[str]], Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable]) -> Any
    """Prompts the user to enter a date, formatted as a strptime-format in the formats list.
    Returns a datetime.date object.

    Run ``help(pyinputplus.parameters)`` for an explanation of the common parameters.

    >>> import pyinputplus as pyip
    >>> response = pyip.inputDate()
    2019/10/31
    >>> response
    datetime.date(2019, 10, 31)
    >>> response = pyip.inputDate()
    Oct 2019
    'Oct 2019' is not a valid date.
    10/31/2019
    >>> response
    datetime.date(2019, 10, 31)
    >>> response = pyip.inputDate(formats=['%b %Y'])
    Oct 2019
    >>> response
    datetime.date(2019, 10, 1)
    """
    if formats is None:
        formats = ("%m/%d/%Y", "%m/%d/%y", "%Y/%m/%d", "%y/%m/%d", "%x")

    validationFunc = lambda value: pysv.validateDate(
        value, formats=formats, blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes,
    )

    return _genericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        applyFunc=applyFunc,
        postValidateApplyFunc=postValidateApplyFunc,
        validationFunc=validationFunc,
    )


def inputDatetime(
    prompt="",
    formats=(
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%y %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%y/%m/%d %H:%M:%S",
        "%x %H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%m/%d/%y %H:%M",
        "%Y/%m/%d %H:%M",
        "%y/%m/%d %H:%M",
        "%x %H:%M",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%y %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%y/%m/%d %H:%M:%S",
        "%x %H:%M:%S",
    ),
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
):
    # type: (str, Union[str, Sequence[str]], Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable]) -> Any
    """Prompts the user to enter a datetime, formatted as a strptime-format in the formats list.
    Returns a ``datetime.datetime`` object.

    Run ``help(pyinputplus.parameters)`` for an explanation of the common parameters.

    >>> import pyinputplus as pyip
    >>> response = pyip.inputDatetime()
    2019/10/31 12:00:01
    >>> response
    datetime.datetime(2019, 10, 31, 12, 0, 1)
    >>> response = pyip.inputDatetime(formats=['hour %H minute %M'])
    hour 12 minute 1
    >>> response
    datetime.datetime(1900, 1, 1, 12, 1)
    """
    validationFunc = lambda value: pysv.validateDatetime(
        value, formats=formats, blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes,
    )

    return _genericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        applyFunc=applyFunc,
        postValidateApplyFunc=postValidateApplyFunc,
        validationFunc=validationFunc,
    )


def inputTime(
    prompt="",
    formats=("%H:%M:%S", "%H:%M", "%X"),
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
):
    # type: (str, Union[str, Sequence[str]], Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable]) -> Any
    """Prompts the user to enter a date, formatted as a strptime-format in the formats list.
    Returns a ``datetime.time`` object.

    Run ``help(pyinputplus.parameters)`` for an explanation of the common parameters.

    >>> import pyinputplus as pyip
    >>> response = pyip.inputTime()
    12:00:01
    >>> response
    datetime.time(12, 0, 1)
    >>> response = pyip.inputTime()
    12:00
    >>> response
    datetime.time(12, 0)
    >>> response = pyip.inputTime(formats=['hour %H minute %M'])
    hour 12 minute 1
    >>> response
    datetime.time(12, 1)
    """

    validationFunc = lambda value: pysv.validateTime(
        value, formats=formats, blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes,
    )

    return _genericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        applyFunc=applyFunc,
        postValidateApplyFunc=postValidateApplyFunc,
        validationFunc=validationFunc,
    )


def inputUSState(
    prompt="",
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
    returnStateName=False,
):
    # type: (str, Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable], bool) -> Any
    """Prompts the user to enter United States state name or abbreviation.
    Returns the state abbreviation (unless ``returnStateName`` is ``True``, in which case the full state name in titlecase is returned.)

    Run ``help(pyinputplus.parameters)`` for an explanation of the common parameters.

    * ``returnStateName`` (bool): If ``True``, the full state name is returned, i.e. ``'California'``. Otherwise, the abbreviation, i.e. ``'CA'``. Defaults to ``False``.

    >>> import pyinputplus as pyip
    >>> response = pyip.inputUSState()
    ca
    >>> response
    'CA'
    >>> response = pyip.inputUSState()
    California
    >>> response
    'CA'
    >>> response = pyip.inputUSState(returnStateName=True)
    ca
    >>> response
    'California'
    """
    validationFunc = lambda value: pysv.validateUSState(
        value,
        blank=blank,
        strip=strip,
        allowRegexes=allowRegexes,
        blockRegexes=blockRegexes,
        returnStateName=returnStateName,
    )

    return _genericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        applyFunc=applyFunc,
        postValidateApplyFunc=postValidateApplyFunc,
        validationFunc=validationFunc,
    )


def inputMonth(
    prompt="",
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
):
    # type: (str, Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable]) -> Any
    """Prompts the user to enter a month name.
    Returns a string of the selected month name in titlecase.

    Run ``help(pyinputplus.parameters)`` for an explanation of the common parameters.

    >>> import pyinputplus as pyip
    >>> response = pyip.inputMonth()
    3
    >>> response
    'March'
    >>> response = pyip.inputMonth()
    Mar
    >>> response
    'March'
    >>> response = pyip.inputMonth()
    MARCH
    >>> response
    'March'
    """

    # TODO add returnNumber and returnAbbreviation parameters.

    validationFunc = lambda value: pysv.validateMonth(
        value, blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes,
    )

    return _genericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        applyFunc=applyFunc,
        postValidateApplyFunc=postValidateApplyFunc,
        validationFunc=validationFunc,
    )


def inputDayOfWeek(
    prompt="",
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
):
    # type: (str, Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable]) -> Any
    """Prompts the user for a day of the week.
    Returns the day name in titlecase.

    Run ``help(pyinputplus.parameters)`` for an explanation of the common parameters.

    >>> import pyinputplus as pyip
    >>> response = pyip.inputDayOfWeek()
    mon
    >>> response
    'Monday'
    >>> response = pyip.inputDayOfWeek()
    FRIDAY
    >>> response
    'Friday'
    """

    # TODO - add returnNumber and return abbreivation parameters.

    validationFunc = lambda value: pysv.validateDayOfWeek(
        value, blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes,
    )

    return _genericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        applyFunc=applyFunc,
        postValidateApplyFunc=postValidateApplyFunc,
        validationFunc=validationFunc,
    )


def inputDayOfMonth(
    year,
    month,
    prompt="",
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
):
    # type: (int, int, str, Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable]) -> Any
    """Prompts the user to enter a numeric month from 1 to 28, 30, or 31
    (or 29 for leap years), depending on the given month and year.
    Returns the entered day as an integer.

    Run ``help(pyinputplus.parameters)`` for an explanation of the common parameters.

    * ``year`` (int): The given year, which determines the range of days in the month.
    * ``month`` (int): The given month, which determines the range of days that can be selected.

    >>> import pyinputplus as pyip
    >>> response = pyip.inputDayOfMonth(2019, 10)
    31
    >>> response
    31
    >>> response = pyip.inputDayOfMonth(2000, 2)
    29
    >>> response
    29
    >>> response = pyip.inputDayOfMonth(2001, 2)
    29
    '29' is not a day in the month of February 2001
    1
    >>> response
    1
    """
    validationFunc = lambda value: pysv.validateDayOfMonth(
        value, year, month, blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes,
    )

    return _genericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        applyFunc=applyFunc,
        postValidateApplyFunc=postValidateApplyFunc,
        validationFunc=validationFunc,
    )


def inputIP(
    prompt="",
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
):
    # type: (str, Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable]) -> Any
    """Prompt the user to enter an IPv4 or IPv6 address.
    Returns the entered IP address as a string.

    Run ``help(pyinputplus.parameters)`` for an explanation of the common parameters.

    """
    validationFunc = lambda value: pysv.validateIP(
        value, blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes,
    )

    return _genericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        applyFunc=applyFunc,
        postValidateApplyFunc=postValidateApplyFunc,
        validationFunc=validationFunc,
    )


def inputRegex(
    regex,
    flags=0,
    prompt="",
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
):
    # type: (Union[str, Pattern], int, str, Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable]) -> Any
    """Prompt the user to enter a string that matches the provided regex string (or regex object) and flags.
    Returns the entered string.

    Run ``help(pyinputplus.parameters)`` for an explanation of the common parameters.
    """
    validationFunc = lambda value: pysv.validateRegex(
        value, regex=regex, flags=flags, blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes,
    )

    return _genericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        applyFunc=applyFunc,
        postValidateApplyFunc=postValidateApplyFunc,
        validationFunc=validationFunc,
    )


def inputRegexStr(
    prompt="",
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
):
    # type: (str, Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable]) -> Any
    """Prompt the user to enter a regular expression string. (Only Python-style
    regex strings are accepted, not Perl- or JavaScript-style.)
    Returns the entered regular expression string.

    Run ``help(pyinputplus.parameters)`` for an explanation of the common parameters.

    """
    validationFunc = lambda value: pysv.validateRegexStr(
        value, blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes,
    )

    return _genericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        applyFunc=applyFunc,
        postValidateApplyFunc=postValidateApplyFunc,
        validationFunc=validationFunc,
    )


def inputURL(
    prompt="",
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
):
    # type: (str, Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable]) -> Any
    """Prompts the user to enter a URL.
    Returns the URL as a string.

    Run ``help(pyinputplus.parameters)`` for an explanation of the common parameters.

    >>> import pyinputplus as pyip
    >>> response = pyip.inputURL()
    hello world
    'hello world' is not a valid URL.
    https://google.com
    >>> response
    'https://google.com'
    >>> response = pyip.inputURL()
    google.com
    >>> response
    'google.com'
    >>> response = pyip.inputURL()
    mailto:al@inventwithpython.com
    >>> response
    'mailto:al@inventwithpython.com'
    """
    validationFunc = lambda value: pysv.validateURL(
        value, blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes,
    )

    return _genericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        applyFunc=applyFunc,
        postValidateApplyFunc=postValidateApplyFunc,
        validationFunc=validationFunc,
    )


def inputYesNo(
    prompt="",
    yesVal="yes",
    noVal="no",
    caseSensitive=False,
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
):
    # type: (str, str, str, bool, Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable]) -> Any
    """Prompts the user to enter a yes/no response.
    The user can also enter y/n and use any case.
    Returns the ``yesVal`` or ``noVal`` argument (which default to ``'yes'`` and ``'no'``), depending on the user's selection.

    Run ``help(pyinputplus.parameters)`` for an explanation of the common parameters.

    >>> import pyinputplus as pyip
    >>> response = pyip.inputYesNo()
    yes
    >>> response
    'yes'
    >>> response = pyip.inputYesNo()
    NO
    >>> response
    'no'
    >>> response = pyip.inputYesNo()
    Y
    >>> response
    'yes'
    >>> response = pyip.inputYesNo(yesVal='oui', noVal='no')
    oui
    >>> response
    'oui'
    """
    validationFunc = lambda value: pysv.validateYesNo(
        value,
        yesVal=yesVal,
        noVal=noVal,
        caseSensitive=caseSensitive,
        blank=blank,
        strip=strip,
        allowRegexes=allowRegexes,
        blockRegexes=blockRegexes,
    )

    result = _genericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        applyFunc=applyFunc,
        validationFunc=validationFunc,
    )

    # If validation passes, return the value that pysv.validateYesNo() returned rather than necessarily what the user typed in.
    result = pysv.validateYesNo(
        result,
        yesVal=yesVal,
        noVal=noVal,
        caseSensitive=caseSensitive,
        blank=blank,
        strip=strip,
        allowRegexes=allowRegexes,
        blockRegexes=blockRegexes,
    )

    if postValidateApplyFunc is None:
        return result
    else:
        return postValidateApplyFunc(result)


def inputBool(
    prompt="",
    trueVal="True",
    falseVal="False",
    caseSensitive=False,
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
):
    # type: (str, str, str, bool, Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable]) -> Any
    """Prompts the user to enter a True/False response.
    The user can also enter t/f and in any case.
    Returns a boolean value.

    Run ``help(pyinputplus.parameters)`` for an explanation of the common parameters.

    >>> import pyinputplus as pyip
    >>> response = pyip.inputBool()
    true
    >>> response
    True
    >>> type(response)
    <class 'bool'>
    >>> response = pyip.inputBool()
    F
    >>> response
    False
    """
    validationFunc = lambda value: pysv.validateYesNo(
        value,
        yesVal=trueVal,
        noVal=falseVal,
        caseSensitive=caseSensitive,
        blank=blank,
        strip=strip,
        allowRegexes=allowRegexes,
        blockRegexes=blockRegexes,
    )

    result = _genericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        applyFunc=applyFunc,
        validationFunc=validationFunc,
    )

    # If the user entered a response that is compatible with trueVal or falseVal exactly, get those particular exact strings.
    result = pysv.validateBool(
        result,
        caseSensitive=caseSensitive,
        blank=blank,
        strip=strip,
        allowRegexes=allowRegexes,
        blockRegexes=blockRegexes,
    )

    if postValidateApplyFunc is None:
        return result
    else:
        return postValidateApplyFunc(result)


def inputZip(
    prompt="",
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
):
    # type: (str, Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable]) -> Any
    """Prompts the user to enter a 3 to 5-digit US zip code.
    Returns the zipcode as a string.

    Run ``help(pyinputplus.parameters)`` for an explanation of the common parameters.
    """
    validationFunc = lambda value: pysv.validateRegex(
        value,
        regex=r"(\d){3,5}(-\d\d\d\d)?",
        blank=blank,
        strip=strip,
        allowRegexes=allowRegexes,
        blockRegexes=blockRegexes,
        excMsg="That is not a valid zip code.",
    )

    return _genericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        applyFunc=applyFunc,
        postValidateApplyFunc=postValidateApplyFunc,
        validationFunc=validationFunc,
    )


# TODO - Finish the following
def inputName(
    prompt="",
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
):
    # type: (str, Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable]) -> Any
    raise NotImplementedError()


def inputAddress(
    prompt="",
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
):
    # type: (str, Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable]) -> Any
    raise NotImplementedError()


def inputPhone(
    prompt="",
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
):
    # type: (str, Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable]) -> Any
    raise NotImplementedError()


def inputFilename(
    prompt="",
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
):
    # type: (str, Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable]) -> Any
    """Prompts the user to enter a filename.
    Filenames can't contain \\ / : * ? " < > | or end with a space.
    Note that this validates filenames, not filepaths. The / and \\ characters are invalid for filenames.
    Returns the filename as a string.

    Run ``help(pyinputplus.parameters)`` for an explanation of the common parameters.
    """
    validationFunc = lambda value: pysv.validateFilename(
        value, blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes,
    )

    return _genericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        applyFunc=applyFunc,
        postValidateApplyFunc=postValidateApplyFunc,
        validationFunc=validationFunc,
    )


def inputFilepath(
    prompt="",
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
    mustExist=False,
):
    # type: (str, Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable], bool) -> Any
    """Prompts the user to enter a filepath. If mustExist is True, then this filepath must exist on the local filesystem.
    Returns the filepath as a string.

    Run ``help(pyinputplus.parameters)`` for an explanation of the common parameters.
    """
    validationFunc = lambda value: pysv.validateFilepath(
        value, blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes, mustExist=mustExist,
    )

    return _genericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        applyFunc=applyFunc,
        postValidateApplyFunc=postValidateApplyFunc,
        validationFunc=validationFunc,
    )


def inputEmail(
    prompt="",
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip=None,
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
):
    # type: (str, Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable]) -> Any
    """Prompts the user to enter an email address.
    Returns the email address as a string.

    Run ``help(pyinputplus.parameters)`` for an explanation of the common parameters.

    >>> import pyinputplus as pyip
    >>> response = pyip.inputEmail()
    hello world
    'hello world' is not a valid email address.
    al@inventwithpython.com
    >>> response
    'al@inventwithpython.com'
    """
    validationFunc = lambda value: pysv.validateEmail(
        value, blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes,
    )

    return _genericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        applyFunc=applyFunc,
        postValidateApplyFunc=postValidateApplyFunc,
        validationFunc=validationFunc,
    )


def inputPassword(
    prompt="",
    mask="*",
    default=None,
    blank=False,
    timeout=None,
    limit=None,
    strip="",
    allowRegexes=None,
    blockRegexes=None,
    applyFunc=None,
    postValidateApplyFunc=None,
):
    # type: (str, str, Any, bool, Optional[float], Optional[int], Union[None, str, bool], Union[None, Sequence[Union[Pattern, str]]], Union[None, Sequence[Union[Pattern, str, Sequence[Union[Pattern, str]]]]], Optional[Callable], Optional[Callable]) -> Any
    """Prompts the user to enter a password. Mask characters will be displayed
    instead of the actual characters. If ``correctPassword`` is ``None``, then any input
    is accepted and returned by ``inputPassword()``. The default for strip is ``''`` so
    that no whitespace striping occurs.

    By default, ``limit`` is set to 1, so an incorrect password attempt results in
    raising ``RetryLimitException``. If ``limit`` is set to ``None``, then user is asked
    again for a correct password forever. The ``wrongPasswordMsg`` string is displayed
    whenever the user enters an incorrect password.

    If ``correctPassword`` is set to None, all input is accepted.

    The ``mask`` is the character used to display instead of the actual keystrokes.
    It can be set to ``None`` (don't hide keystrokes), a blank string (don't show
    anything as the user types), or a single-character string (show this
    character instead of the keystroke). It can't be set to a multi-character
    string.

    Run ``help(pyinputplus.parameters)`` for an explanation of the common parameters."""

    if mask is not None and len(mask) > 1:
        raise PyInputPlusException("mask argument must be None, '', or a single-character string.")

    pysv._validateGenericParameters(blank, strip, allowRegexes, blockRegexes)

    validationFunc = lambda value: pysv._prevalidationCheck(
        value, blank=blank, strip=strip, allowRegexes=allowRegexes, blockRegexes=blockRegexes, excMsg=None,
    )[1]

    return _genericInput(
        prompt=prompt,
        default=default,
        timeout=timeout,
        limit=limit,
        applyFunc=applyFunc,
        postValidateApplyFunc=postValidateApplyFunc,
        validationFunc=validationFunc,
        passwordMask=mask,
    )


# Wrap all of the PySimpleValidate functions so that they can be called
# from PyInputPlus and will raise pyinputplus.ValidationException instead.
for functionName in (
    "validateStr",
    "validateNum",
    "validateInt",
    "validateFloat",
    "validateChoice",
    "validateTime",
    "validateDate",
    "validateDatetime",
    "validateFilename",
    "validateFilepath",
    "validateIP",
    "validateIPv4",
    "validateIPv6",
    "validateRegex",
    "validateRegexStr",
    "validateURL",
    "validateEmail",
    "validateYesNo",
    "validateBool",
    "validateUSState",
    "validateName",
    "validateAddress",
    "validatePhone",
    "validateMonth",
    "validateDayOfWeek",
    "validateDayOfMonth",
):
    exec(
        """def %s(value, *args, **kwargs):
    try:
        return pysv.%s(value, *args, **kwargs)
    except pysv.ValidationException as e:
        raise ValidationException(str(e))"""
        % (functionName, functionName)
    )
