import json
import os

HOME_DIRECTORY = '/app'

def read():
    """
    This is what grabs all the config info. Returns a dictionary that
    has the different config values in it.
    """

    with open(HOME_DIRECTORY + '/Body/global.cfg', 'r') as f:
        config_settings = json.load(f)
    config_settings['CLIENT_SECRET'] = os.environ.get('CLIENTSECRET')
    return config_settings


def save(config_settings):
    with open(HOME_DIRECTORY + '/Body/global.cfg', 'w') as f:
        json.dump(config_settings, f)