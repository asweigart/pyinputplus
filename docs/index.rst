.. PyInputPlus documentation master file, created by
   sphinx-quickstart on Mon Jul  9 16:50:50 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PyInputPlus's documentation!
=======================================


PyInputPlus is a Python 3 and 2 module to provide ``input()`` and ``raw_input()`` like functions with additional validation features. PyInputPlus was created and is maintained by Al Sweigart.

This module relies heavily on PySimpleValidate (also by Al) for the actual
validation. PyInputPlus provides interaction with the user through stdin/stdout
while PySimpleValidate provides the functions that validate the user's input.


Installation
============

You can install PyInputPlus with the pip tool. On Windows, run the following from a Command Prompt window:

    pip install pyinputplus

On macOS and Linux, run the following from a Terminal window:

    pip3 install pyinputplus

The PySimpleValidate and stdiomask modules will also be installed as a part of PyInputPlus's installation.

Quick Start
===========


PyInputPlus's functions will repeatedly prompt the user to enter text until they enter valid input.
A cleaned up version of the input is returned.

It's recommended to import PyInputPlus with the shorter name ``pyip``.

    >>> import pyinputplus as pyip

PyInputPlus's functions all begin with the word ``input``, such as ``inputStr()`` or ``inputDate()``. Collectively, they are referred to in this documentation as the ``input*()`` functions.

You can ask the user for an integer with ``inputInt()``, and the return value will be an integer instead of a string like ``input()`` would return:

    >>> response = pyip.inputInt()
    forty two
    'forty two' is not an integer.
    42
    >>> response
    42

You could specify a prompt, along with any restrictions you'd like to impose:

    >>> response = pyip.inputInt(prompt='Enter your age: ', min=1)
    Enter your age: 0
    Number must be at minimum 1.
    Enter your age: 2
    >>> response
    2

There are several functions for different common types of data:

    >>> response = pyip.inputEmail()
    alinventwithpython.com
    'alinventwithpython.com' is not a valid email address.
    al@inventwithpython.com
    >>> response
    'al@inventwithpython.com'

You could also present a small menu of options to the user:

    >>> response = pyip.inputMenu(['cat', 'dog', 'moose'])
    Please select one of the following:
    * cat
    * dog
    * moose
    cat
    >>> response
    'cat'
    >>> response = pyip.inputMenu(['cat', 'dog', 'moose'], numbered=True)
    Please select one of the following:
    1. cat
    2. dog
    3. moose
    1
    >>> response
    'cat'

See the list of functions to get an idea of the kinds of information you can get from the user.

Common input*() Parameters
--------------------------

The following parameters are available for all of the ``input*()`` functions:

* ``prompt`` (str): The text to display before each prompt for user input. Identical to the prompt argument for Python's raw_input() and input() functions.
* ``default`` (str, None): A default value to use should the user time out or exceed the number of tries to enter valid input.
* ``blank`` (bool): If True, a blank string will be accepted. Defaults to ``False``.
* ``timeout`` (int, float): The number of seconds since the first prompt for input after which a TimeoutException is raised the next time the user enters input.
* ``limit`` (int): The number of tries the user has to enter valid input before the default value is returned.
* ``strip`` (bool, str, None): If None, whitespace is stripped from value. If a str, the characters in it are stripped from value. If False, nothing is stripped.
* ``allowlistRegexes`` (Sequence, None): A sequence of regex str that will explicitly pass validation.
* ``blocklistRegexes`` (Sequence, None): A sequence of regex str or (regex_str, error_msg_str) tuples that, if matched, will explicitly fail validation.
* ``applyFunc`` (Callable, None): An optional function that is passed the user's input, and returns the new value to use as the input.
* ``postValidateApplyFunc`` (Callable, None): An optional function that is passed the user's input after it has passed validation, and returns a transformed version for the ``input*()`` function to return.


inputStr()
----------

The ``inputStr()`` function is the least restrictive function: it accepts all input (except no/blank input). Use this function when you'd like the built-in ``input()`` function but with PyInputPlus's additional features.

Example usage:

    >>> response = pyip.inputStr()
    Hello
    >>> response
    'Hello'
    >>> response = pyip.inputStr(blank=True)

    >>> response
    ''
    >>> response = pyip.inputStr(blocklistRegexes=[r'\d\d', r'[a-z]'])
    42
    This response is invalid.
    hello
    This response is invalid.
    HELLO
    >>> response
    'HELLO'
    >>>

inputCustom()
-------------

Pass a custom function to do validation. This function accepts one string argument, raises an exception if it fails validation (the exception
message is the message shown to the user), and returns None if the user input should be unmodified or returns a new value that `inputCustom()`
should return.

    >>> def isEven(value):
    ...     if float(value) % 2 != 0:
    ...         raise Exception('This is not an even value.')
    ...
    >>> response = pyip.inputCustom(isEven)
    5
    This is not an even value.
    4
    >>> response
    '4'

inputNum(), inputInt(), inputFloat()
------------------------------------

These functions allow the user to enter numbers. They return int or float values, not strings. In addition to the usual keyword arguments, they also have the following:

* ``min`` (None, int): If not None, the minimum accepted numeric value, including the minimum argument.
* ``max`` (None, int): If not None, the maximum accepted numeric value, including the maximum argument.
* ``greaterThan`` (None, int): If not None, the minimum accepted numeric value, not including the greaterThan argument.
* ``lessThan`` (None, int): If not None, the maximum accepted numeric value, not including the lessThan argument.


    >>> import pyinputplus as pyip
    >>> response = pyip.inputNum()
    four
    'four' is not a number.
    42
    >>> response
    42
    >>> type(response)
    <class 'int'>

    >>> response = pyip.inputInt()
    3.14
    '3.14' is not an integer.
    3
    >>> response
    3

    >>> response = pyip.inputFloat()
    3
    >>> response
    3.0

    >>> response = pyip.inputFloat(greaterThan=3, lessThan=5)
    3
    Number must be greater than 3.
    6
    Number must be less than 5.
    4.2
    >>> response
    4.2


inputChoice(), inputMenu()
--------------------------

These functions allow the user to enter one of many provided options. The returned value will match the choice in the provided list, despite different cases or leading/trailing whitespace.

    >>> response = pyip.inputChoice(['cats', 'dogs', 'moose'])
    Please select one of: cats, dogs, moose
    fish
    'fish' is not a valid choice.
    Please select one of: cats, dogs, moose
    dogs
    >>> response
    'dogs'

    >>> response = pyip.inputChoice(['cats', 'dogs', 'moose'])
    Please select one of: cats, dogs, moose
        DOGS
    >>> response
    'dogs'

The ``inputMenu()`` function takes the same arguments as ``inputChoice()`` but presents numbered or lettered options the user can use:

    >>> response = pyip.inputMenu(['cats', 'dogs', 'moose'])
    Please select one of the following:
    * cats
    * dogs
    * moose
    CATS
    >>> response
    'cats'

    >>> response = pyip.inputMenu(['cats', 'dogs', 'moose'], numbered=True)
    Please select one of the following:
    1. cats
    2. dogs
    3. moose
    1
    >>> response
    'cats'

    >>> response = pyip.inputMenu(['cats', 'dogs', 'moose'], lettered=True)
    Please select one of the following:
    A. cats
    B. dogs
    C. moose
    a
    >>> response
    'cats'

inputYesNo(), inputBool()
-------------------------

TODO

inputEmail()
------------

TODO

inputDate(), inputDatetime(), inputTime()
------------------------------------------

TODO

inputMonth(), inputDayOfWeek(), inputDayOfMonth()
-------------------------------------------------

TODO

inputState(), inputZip()
------------------------

TODO

inputIp(), inputURL()
---------------------

TODO

inputRegex()
------------

TODO

inputRegexStr()
---------------

TODO

inputFilename(), inputFilepath()
--------------------------------

TODO

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api
