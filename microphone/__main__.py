from microphone._argparser import MicArgParser
from microphone.communication_node import CommunicationNode


def main(*args, **kwargs):
    """
    kwargs:
        'publish_address': in the form of `tcp:///*:5555`
        or any other zeromq address format. IE `ipc:///*:5555`

        'response_address': in the form of `tcp:///*:5555`
        or any other zeromq address format. IE `ipc:///*:5555`
    """
    # TODO: parse args and kwargs
    communication_node = CommunicationNode(None, **kwargs)
    communication_node.run()



if __name__ == '__main__':
    parser = MicArgParser()
    args = parser.parse_args()
    main(*args)
