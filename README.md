# PyInputPlus

A Python 2 and 3 module to provide input()- and raw_input()-like functions with additional validation features, including:

* Re-prompting the user if they enter invalid input.
* Validating for numeric, boolean, date, time, or yes/no responses.
* Timeouts or retry limits for user responses.
* Specifying regexes for whitelists or blacklists of responses.
* Specifying ranges for numeric inputs.
* Presenting menus with bulleted, lettered, or numbered options.
* Allowing case-sensitive or case-insensitive responses.

Installation
============

    pip install pyinputplus

Example Usage
=============

    >>> import pyinputplus as pyip
    >>> result = pyip.inputStr()

    Blank values are not allowed.
    Hello
    >>> result
    'Hello'

    >>> result = pyip.inputNum()
    forty two
    'forty two' is not a number.
    42
    >>> result
    42

    >>> result = pyip.inputNum(min=4, max=6)
    3
    Input must be at minimum 4.
    7
    Input must be at maximum 6.
    4
    >>> result
    4

    >>> result = pyip.inputNum(greaterThan=4, lessThan=6)
    4
    Input must be greater than 4.
    4.1
    >>> result
    4.1

    >>> result = pyip.inputStr('Favorite animal> ', blacklistRegexes=['moose'])
    Favorite animal> moose
    This response is invalid.
    Favorite animal> cat
    >>> result
    'cat'

    >>> result = inputMenu(['dog', 'cat', 'moose'])
    Please select one of the following:
    * dog
    * cat
    * moose
    DoG
    >>> result
    'dog'

    >>> result = inputMenu(['dog', 'cat', 'moose'], lettered=True, numbered=False)
    Please select one of the following:
    A. dog
    B. cat
    C. moose
    b
    >>> result
    'cat'

Common Input Function Parameters
================================

All input functions have the following parameters:

* `prompt` (str): The text to display before each prompt for user input. Identical to the prompt argument for Python's `raw_input()` and `input()` functions. Default
* `default` (str, None): A default value to use should the user time out or exceed the number of tries to enter valid input.
* `blank` (bool): If `True`, blank strings will be allowed as valid user input.
* `timeout` (int, float): The number of seconds since the first prompt for input after which a TimeoutException is raised the next time the user enters input.
* `limit` (int): The number of tries the user has to enter valid input before the default value is returned.
* `strip` (bool, str, None): If `True`, whitespace is stripped from `value`. If a str, the characters in it are stripped from value. If `None`, nothing is stripped. Defaults to `True`.
* `whitelistRegexes` (Sequence, None): A sequence of regex str that will explicitly pass validation, even if they aren't numbers. Defaults to `None`.
* `blacklistRegexes` (Sequence, None): A sequence of regex str or (regex_str, response_str) tuples that, if matched, will explicitly fail validation. Defaults to `None`.
* `applyFunc` (Callable, None): An optional function that is passed the user's input, and returns the new value to use as the input.
* `validationFunc` (Callable): A function that is passed the user's input value, which raises an exception if the input isn't valid. (The return value of this function is ignored.)
* `postValidateApplyFunc` (Callable): An optional function that is passed the user's input after it has passed validation, and returns a transformed version for the input function to return.

Other input functions may have additional parameters.

Input Functions
===============

* `inputStr()` - Accepts a string. Use this if you basically want Python's `input()` or `raw_input()`, but with PyInputPlus features such as whitelist/blacklist, timeouts, limits, etc.
* `inputNum()` - Accepts a numeric number. Additionally has `min` and `max` parameters for inclusive bounds and `greaterThan` and `lessThan` parameters for exclusive bounds. Returns an int or float, not a str.
* `inputInt()` - Accepts an integer number. Also has `min`/`max`/`greaterThan`/`lessThan` parameters. Returns an int, not a str.
* `inputFloat()` - Accepts a floating-point number. Also has `min`/`max`/`greaterThan`/`lessThan` parameters. Returns a float, not a str.
* `inputBool()` - Accepts a case-insensitive form of `'True'`, `'T'`, `'False'`, or `'F'` and returns a bool value.
* `inputChoice()` - Accepts one of the strings in the list of strings passed for its `choices` parameter.
* `inputMenu()` - Similar to `inputChoice()`, but will also present the choices in a menu with 1, 2, 3... or A, B, C... options if `numbered` or `lettered` are set to `True`.
* `inputDate()` - Accepts a date typed in one of the `strftime` formats passed to the `formats` parameter. (This has several common formats by default.) Returns a `datetime.date` object.
* `inputDatetime()` - Same as `inputDate()`, except it handles dates and times. (This has several common formats by default.) Returns a `datetime.datetime` object.
* `inputTime()` - Same as `inputDate()`, except it handles times. (This has several common formats by default.) Returns a `datetime.time` object.
* `inputYesNo()` - Accepts a case-insensitive form of `'Yes'`, `'Y'`, `'No'`, or `'N'` and returns `'yes'` or `'no'`.
