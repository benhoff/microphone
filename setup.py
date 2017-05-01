import os
from setuptools import find_packages, setup


# directory = os.path.abspath(os.path.dirname(__file__))
"""
with open(os.path.join(directory, 'README.rst')) as f:
    long_description = f.read()
"""

setup(
    name="microphone",
    version='0.3.0',
    description='Sending microphone data using ZeroMQ',
    # long_description=long_description,
    url='https://github.com/benhoff/microphone',
    license='GPL3',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Multimedia :: Sound/Audio :: Capture/Recording',
        'Topic :: Utilities',
        'Operating System :: OS Independent'],
    keywords='sound capture to text',
    author='Ben Hoff',
    author_email='beohoff@gmail.com',
    package_data={'microphone':['resources/congo.wav',
                                'resources/done.wav',
                                'default_settings.ini',]},

    entry_points={'microphone.audioengines': ['pyaudio = microphone.pyaudio_:PyAudio',],
                  'console_scripts': ['microphone-python = microphone.__main__:main'],
                  'vexbot.adapters': ['microphone = microphone.__main__']},

    packages= find_packages(), # exclude=['docs', 'tests']
    install_requires=[
        'pluginmanager>=0.4.1'
        'PyAudio',
        'pyzmq',
        'vexmessage',
        ],

    extras_require={
        'dev': ['flake8']
        },
)
