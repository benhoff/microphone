import argparse
_RATE = 160000
_BITS = 16
_CHANNEL = 1
_CHUNKSIZE = 1024
_DRIVER = 'pyaudio'
_PUBLISH_ADDRESS = 'tcp://*:5555'
_RESPONSE_ADDRESS = 'tcp://*:5556'


class MicArgParser(argparse.ArgumentParser):
    def __init__(self):
        super().__init__(prog='Microphone', description='audio capture')

        self.add_argument('--audio-driver', '-ad',
                           action='store',
                           default=_DRIVER)

        self.add_argument('--audio_address', '-aa',
                          action='store',
                          default=_PUBLISH_ADDRESS)

        self.add_argument('--communication_address', '-ca',
                          action='store',
                          default=_RESPONSE_ADDRESS)

        self.add_argument('--rate', '-r',
                          action='store',
                          default=_RATE,
                          type=int)

        self.add_argument('--bits', '-b',
                          action='store',
                          default=_BITS,
                          type=int)

        self.add_argument('--chunksize', '-chk',
                          action='store',
                          default=_CHUNKSIZE,
                          type=int)

        self.add_argument('--channel', '-chl',
                          action='store',
                          default=_CHANNEL,
                          type=int)
