import sys

import praw
from requests import ConnectionError
from praw.errors import OAuthInvalidGrant

import configReader as cfgReader
from loggingSetup import create_logger

__author__ = 'Eliminioa'

class Connector(object):
    USER_SCOPES = {'bot': ('edit',
                           'identity',
                           'privatemessages',
                           'read',
                           'submit'),
                   'player': ('identity')
                   }

    def __init__(self):
        """
        This provides a method of connecting to an account on reddit. It has
        two user classes, 'bot' and 'player' which indicate which scopes it
        needs to grab.

        :return: An Connector instance with an active, unauthenticated reddit
                connection.
        """
        # Defining instance variables
        #TODO Make access info lookup SQL
        self.log = create_logger(__name__)
        self.cfg = cfgReader.ConfigReader()
        self.access_infos = self.cfg._access_infos
        self.r = praw.Reddit(
            user_agent=self.cfg._user_agent
        )

        try:
            self.r.get_subreddit('periwinkle')
        except ConnectionError as e:
            self.log.exception('Cannot connect to Reddit!')
            raise e
        self.log.debug('Connected to reddit with user agent %(ua)s' %
                       {'ua': self.cfg._user_agent}
                       )

        self.r.set_oauth_app_info(
            client_id=self.cfg._client_id,
            client_secret=self.cfg._client_secret,
            redirect_uri=self.cfg._redirect_uri
        )

        # UNWRAPPING METHODS AND WRAPPING CUSTOM METHODS
        # Unwrap all the methods from PRAW that use a reddit instance
        for instanceMethod in dir(self.r):
            if not instanceMethod.startswith(('__', '_')) and not instanceMethod.isupper():
                exec '''self.%(varName)s = self.r.%(varName)s''' % {'varName': instanceMethod}
        pass

    def connect_to_reddit(self, access_code):
        """
        As labeled...

        :param access_code: OAuth code
        """
        try:
            access_information = self.r.get_access_information(
                code=access_code
            )
        except OAuthInvalidGrant as e:
            self.log.exception('Bad OAuth code!')
            raise

        self.r.set_access_credentials(**access_information)
        self.log.debug('Logged into reddit with %(account)s' %
                       {'account': self.account_info}
                       )

        self.cfg._access_infos[self.r.get_me().name] = access_information

    def get_OAuth_URL(self, user_class):
        user_class_scope = Connector.USER_SCOPES[user_class]

        OAuth_URL = self.r.get_authorize_url(
            state='ChromaAutomationSuite',
            scope=user_class_scope,
            refreshable=True
        )

        return OAuth_URL

    def refresh_token(self):
        """
        Refresh the user's token.
        """
        self.cfg._access_infos[self.username] = self.r.refresh_access_information(
            self.access_infos[self.username]['refresh_token']
        )

    def set_user(self, user):
        """
        Sets which user the bot is representing. Can also be used to
        reconnect to Reddit.

        :return: True if the user was retrieved correctly.
        """
        try:
            self.r.set_access_credentials(**self.access_infos[user])
        except KeyError as e:
            self.log.exception('Invalid user: {}'.format(user))
            raise e
        except OAuthInvalidGrant as e:
            self.log.exception('Bad OAuth code for! {}'.format(user))
            raise e
        try:
            self.r.get_me()
            return True
        except:
            e = sys.exc_info()[0]
            return e

    def get_mods_of_subreddit(self, subreddit, string=False):
        """
        Get the moderators of a given subreddit.

        :param subreddit: The name of the subreddit to get the mods of
        :param string: Whether mods should be returned as Redditor objects
                        or as strings
        :return: A list of the mods, either as Redditor objects or strings
        """
        if string:
            mods = [str(m) for m in self.r.get_subreddit(subreddit).get_moderators()]
        else:
            mods = self.r.get_subreddit(subreddit).get_moderators()
        return mods

    @property
    def account_info(self):
        return self.r.get_me()

    @property
    def username(self):
        return self.account_info.name

# finally, make the Connector object
antenna = Connector()
