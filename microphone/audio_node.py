import argparse
import zmq


class AudioNode(object):
    def __init__(self, context=None, **kwargs):
        context = context or zmq.Context()
        self.address_frontend = kwargs.get('address_frontend',
                                           'tcp://*:5555')

        self.address_backend = kwargs.get('address_backend',
                                          'inproc://microphone-audio')

        # create the public facing publish socket
        self.frontend_audio = context.socket(zmq.XPUB)
        print(self.address_frontend)
        self.frontend_audio.bind(self.address_frontend)
        # create the internal subscription endpoint
        self.backend_audio = context.socket(zmq.XSUB)
        self.backend_audio.bind(self.address_backend)

        # forward all audio internal traffic out
        zmq.proxy(self.backend_audio, self.frontend_audio)

    def run(self):
        while True:
            zmq.poll((self.frontend_audio, self.backend_audio))

def main(frontend_address, backend_address):
    audio_node = AudioNode(kwargs={'address_frontend': frontend_address,
                                   'address_backend': backend_address})
    # NOTE: blocking call
    audio_node.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--frontend_address',
                        action='store',
                        default='tcp://*:5555')

    parser.add_argument('--backend_address',
                        action='store',
                        default='tcp://*:5556')

    args = parser.parse_args()
    main(args.frontend_address, args.backend_address)
