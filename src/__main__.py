import argparse

from .mic import Mic

def main(args=None):
    parser = argparse.ArgumentParser(prog='Vex',
                                     description='Speech to text using PyAudio and choice of speech analyzer')

    parser.add_argument(['--provider', '-p'],
                        action='store')
    
    # TODO: add in option to specify a file like mp3
    # parser.add_argument(['-file', '-f'])


if __name__ == '__main__':
    main()
