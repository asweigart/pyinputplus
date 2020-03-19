import re, io
from setuptools import setup, find_packages

# Load version from module (without loading the whole module)
with open('src/pyinputplus/__init__.py', 'r') as fo:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fo.read(), re.MULTILINE).group(1)

# Read in the README.md for the long description.
with io.open('README.md', encoding='utf-8') as fo:
    long_description = fo.read()

setup(
    name='PyInputPlus',
    version=version,
    url='https://github.com/asweigart/pyinputplus',
    author='Al Sweigart',
    author_email='al@inventwithpython.com',
    description=('Provides more featureful versions of input() and raw_input().'),
    license='BSD',
    long_description=long_description,
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    test_suite='tests',
    install_requires=['pysimplevalidate>=0.2.7', 'stdiomask>=0.0.3', 'typing;python_version<"3.5"'],
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
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)