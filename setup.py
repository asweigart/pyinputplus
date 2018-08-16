import re
from setuptools import setup

# Load version from module (without loading the whole module)
with open('pyinputplus/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

# Read in the README.md for the long description.
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name='PyInputPlus',
    version=version,
    url='https://github.com/asweigart/pyinputplus',
    author='Al Sweigart',
    author_email='al@inventwithpython.com',
    description=('The input() and raw_input() functions with added validation features.'),
    long_description=long_description,
    license='BSD',
    packages=['pyinputplus'],
    test_suite='tests',
    install_requires=['pysimplevalidate'],
    keywords="input validation text gui message box",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Environment :: MacOS X',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)