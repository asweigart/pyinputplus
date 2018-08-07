from setuptools import setup


setup(
    name='PyInputPlus',
    version=__import__('pyinputplus').__version__,
    url='https://github.com/asweigart/pyinputplus',
    author='Al Sweigart',
    author_email='al@inventwithpython.com',
    description=('The input() and raw_input() functions with added validation features.'),
    license='BSD',
    packages=['pyinputplus'],
    test_suite='tests',
    install_requires=['pymsgbox', 'pydidyoumean'],
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
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
        'Programming Language :: Python :: 3.5'
        'Programming Language :: Python :: 3.6'
        'Programming Language :: Python :: 3.7'
    ],
)