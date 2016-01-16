class AttSTT(AbstractSTTEngine):
    """
    Speech-To-Text implementation which relies on the AT&T Speech API.

    This implementation requires an AT&T app_key/app_secret to be present in
    profile.yml. Please sign up at http://developer.att.com/apis/speech and
    create a new app. You can then take the app_key/app_secret and put it into
    your profile.yml:
        ...
        stt_engine: att
        att-stt:
          app_key:    4xxzd6abcdefghijklmnopqrstuvwxyz
          app_secret: 6o5jgiabcdefghijklmnopqrstuvwxyz
    """

    SLUG = "att"

    def __init__(self, app_key, app_secret):
        self._logger = logging.getLogger(__name__)
        self._token = None
        self.app_key = app_key
        self.app_secret = app_secret

    @classmethod
    def get_config(cls):
        # FIXME: Replace this as soon as we have a config module
        config = {}
        # Try to get AT&T app_key/app_secret from config
        profile_path = jasperpath.config('profile.yml')
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = yaml.safe_load(f)
                if 'att-stt' in profile:
                    if 'app_key' in profile['att-stt']:
                        config['app_key'] = profile['att-stt']['app_key']
                    if 'app_secret' in profile['att-stt']:
                        config['app_secret'] = profile['att-stt']['app_secret']
        return config

    @property
    def token(self):
        if not self._token:
            headers = {'content-type': 'application/x-www-form-urlencoded',
                       'accept': 'application/json'}
            payload = {'client_id': self.app_key,
                       'client_secret': self.app_secret,
                       'scope': 'SPEECH',
                       'grant_type': 'client_credentials'}
            r = requests.post('https://api.att.com/oauth/v4/token',
                              data=payload,
                              headers=headers)
            self._token = r.json()['access_token']
        return self._token

    def transcribe(self, fp):
        data = fp.read()
        r = self._get_response(data)
        if r.status_code == requests.codes['unauthorized']:
            # Request token invalid, retry once with a new token
            self._logger.warning('OAuth access token invalid, generating a ' +
                                 'new one and retrying...')
            self._token = None
            r = self._get_response(data)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            self._logger.critical('Request failed with response: %r',
                                  r.text,
                                  exc_info=True)
            return []
        except requests.exceptions.RequestException:
            self._logger.critical('Request failed.', exc_info=True)
            return []
        else:
            try:
                recognition = r.json()['Recognition']
                if recognition['Status'] != 'OK':
                    raise ValueError(recognition['Status'])
                results = [(x['Hypothesis'], x['Confidence'])
                           for x in recognition['NBest']]
            except ValueError as e:
                self._logger.debug('Recognition failed with status: %s',
                                   e.args[0])
                return []
            except KeyError:
                self._logger.critical('Cannot parse response.',
                                      exc_info=True)
                return []
            else:
                transcribed = [x[0].upper() for x in sorted(results,
                                                            key=lambda x: x[1],
                                                            reverse=True)]
                self._logger.info('Transcribed: %r', transcribed)
                return transcribed

    def _get_response(self, data):
        headers = {'authorization': 'Bearer %s' % self.token,
                   'accept': 'application/json',
                   'content-type': 'audio/wav'}
        return requests.post('https://api.att.com/speech/v3/speechToText',
                             data=data,
                             headers=headers)

    @classmethod
    def is_available(cls):
        return diagnose.check_network_connection()
