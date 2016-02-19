import argparse
from pyaudio_ae import PyAudioEnginePlugin


def main(context=None,
         communication_address='',
         audio_address=''):

    engine = PyAudioEnginePlugin(context,
                                 communication_address,
                                 audio_address)

    engine.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('communication_address',
                        action='store',
                        default='inproc://microphone')

    parser.add_argument('audio_address',
                        action='store',
                        default='tcp://127.0.0.1:5556')

    args = parser.parse_args()

    main(communication_address=args.communication_address,
         audio_address=args.audio_address)
