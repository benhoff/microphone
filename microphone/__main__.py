import sys
import logging

from argparse import ArgumentParser
from configparser import ConfigParser

import pluginmanager

from microphone.messaging import Messaging


def main(context=None, *args, **kwargs):
    """
    kwargs:
        'command_publish_address': in the form of `tcp://*:5555`
        or any other zeromq address format. IE `ipc://*:5555`

        'command_subscribe_address': in the form of `tcp://*:5555`
        or any other zeromq address format. IE `ipc://*:5555`

        'audio_publish_address': in the form of `tcp://*:5555`
        or any other zeromq address format. IE `ipc://*:5555`
    """

    # Get configuration
    args = _get_command_line_args()
    # Get settings filepath
    settings_filepath = args.get('settings_path')
    # Get settings using the settings filepath
    settings = _get_settings(settings_filepath)
    settings = settings.get('microphone', {})
    # TODO: verify that this doesn't break things in new and interesting ways
    settings.update(kwargs)

    plugin_manager = pluginmanager.PluginInterface()
    plugin_manager.set_entry_points('microphone.audioengines')
    plugins = plugin_manager.collect_entry_point_plugins(return_dict=True)

    # find the audio driver or stick to the default of `pyaudio`
    audio_driver = settings.get('audio_driver', 'pyaudio')

    try:
        # NOTE: `AudioDriver` is a class
        AudioDriver = plugins[audio_driver]
    # Fail early if we can't find the plugin we're looking for
    except KeyError:
        logging.error('Audio driver set in microphone settings of {} not foun'
                      'd. Please install or fix your settings file.')

        logging.error('Plugins available: {}'.format(list(plugins.keys())))
        sys.exit(1)

    # TODO: Assume that a computer will only use one audio driver?

    # Also assume that microphones may be physcially displaced from each other
    # which means that they might record simultaneously

    # FIXME: these are not good default addresses
    command_publish_address = settings.get('publish_address',
                                           'tcp://127.0.0.1:6910')

    command_subscribe_address = settings.get('subscribe_address',
                                             'tcp://127.0.0.1:6823')

    audio_publish_address = settings.get('audio_publish_address',
                                         'tcp://127.0.0.1:5012')

    messaging = Messaging(command_publish_address,
                          command_subscribe_address,
                          audio_publish_address)

    audio_driver = AudioDriver(messaging, settings)

    audio_driver.run()


def _get_command_line_args() -> dict:
    parser = ArgumentParser()
    parser.add_argument('--settings_path',
                        default='settings.ini',
                        action='store')

    parser.add_argument('--command_publish_address',
                        nargs='?',
                        action='store')

    parser.add_argument('--command_subscribe_address',
                        nargs='?',
                        action='store')

    parser.add_argument('--audio_publish_address',
                        nargs='?',
                        action='store')

    args = parser.parse_args()

    return vars(args)


def _get_settings(settings_filepath) -> dict:
    config = ConfigParser()
    config.read(settings_filepath)

    config_dict = {s: dict(config.items(s))
                   for s
                   in config.sections()}

    return config_dict


if __name__ == '__main__':
    main()
