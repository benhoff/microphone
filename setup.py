import os
from setuptools import find_packages, setup


# directory = os.path.abspath(os.path.dirname(__file__))
"""
with open(os.path.join(directory, 'README.rst')) as f:
    long_description = f.read()
"""

setup(
    name="microphone",
    version='0.0.4',
    description='Text to Speech for python',
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
    entry_points={'microphone.audioengines': ['pyaudio = microphone.audioengines.pyaudio_ae',
                                              'base = microphone.audioengine_plugin']},

    packages= find_packages(), # exclude=['docs', 'tests']
    install_requires=[
        'pluginmanager',
        'PyAudio',
        'pyzmq'
        ],

    extras_require={
        'dev': ['flake8']
        },
)
