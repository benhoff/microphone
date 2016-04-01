import argparse
from microphone.node import Node


def main(context=None, *args, **kwargs):
    """
    kwargs:
        'publish_address': in the form of `tcp:///*:5555`
        or any other zeromq address format. IE `ipc:///*:5555`

        'response_address': in the form of `tcp:///*:5555`
        or any other zeromq address format. IE `ipc:///*:5555`
    """
    # TODO: parse args and kwargs
    node = node(context, **kwargs)
    node.run()


def _get_kwargs():
    parser = argparse.ArgumentParser(prog='Microphone',
                                     description='audio capture')

    parser.add_argument('--audio-driver', '-ad',
                       action='store',
                       default='pyaudio')

    parser.add_argument('--audio_address', '-aa',
                      action='store',
                      default='tcp://127.0.0.1:5555')

    parser.add_argument('--communication_address', '-ca',
                      action='store',
                      default='tcp://127.0.0.1:5556')

    parser.add_argument('--rate', '-r',
                      action='store',
                      default=160000,
                      type=int)

    parser.add_argument('--bits', '-b',
                      action='store',
                      default=16,
                      type=int)

    parser.add_argument('--chunksize', '-chk',
                      action='store',
                      default=1024,
                      type=int)

    parser.add_argument('--channel', '-chl',
                      action='store',
                      default=1,
                      type=int)

    return vars(parser.parse_args())


if __name__ == '__main__':
    kwargs= _get_kwargs()
    main(**kwargs)
