import argparse
from pyaudio_ae import PyAudioEnginePlugin


def main(context=None, address=''):
    engine = PyAudioEnginePlugin(context, address)
    engine.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('address', action='store', default='inproc://microphone')
    args = parser.parse_args()
    main(address=args.address)
