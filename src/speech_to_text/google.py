class GoogleSTT(AbstractSTTEngine):
    """
    Speech-To-Text implementation which relies on the Google Speech API.

    This implementation requires a Google API key to be present in profile.yml

    To obtain an API key:
    1. Join the Chromium Dev group:
       https://groups.google.com/a/chromium.org/forum/?fromgroups#!forum/chromium-dev
    2. Create a project through the Google Developers console:
       https://console.developers.google.com/project
    3. Select your project. In the sidebar, navigate to "APIs & Auth." Activate
       the Speech API.
    4. Under "APIs & Auth," navigate to "Credentials." Create a new key for
       public API access.
    5. Add your credentials to your profile.yml. Add an entry to the 'keys'
       section using the key name 'GOOGLE_SPEECH.' Sample configuration:
    6. Set the value of the 'stt_engine' key in your profile.yml to 'google'


    Excerpt from sample profile.yml:

        ...
        timezone: US/Pacific
        stt_engine: google
        keys:
            GOOGLE_SPEECH: $YOUR_KEY_HERE

    """

    SLUG = 'google'

    def __init__(self, api_key=None, language='en-us'):
        # FIXME: get init args from config
        """
        Arguments:
        api_key - the public api key which allows access to Google APIs
        """
        self._logger = logging.getLogger(__name__)
        self._request_url = None
        self._language = None
        self._api_key = None
        self._http = requests.Session()
        self.language = language
        self.api_key = api_key

    @property
    def request_url(self):
        return self._request_url

    @property
    def language(self):
        return self._language

    @language.setter
    def language(self, value):
        self._language = value
        self._regenerate_request_url()

    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, value):
        self._api_key = value
        self._regenerate_request_url()

    def _regenerate_request_url(self):
        if self.api_key and self.language:
            query = urllib.parse.urlencode({'output': 'json',
                                      'client': 'chromium',
                                      'key': self.api_key,
                                      'lang': self.language,
                                      'maxresults': 6,
                                      'pfilter': 2})
            self._request_url = urllib.parse.urlunparse(
                ('https', 'www.google.com', '/speech-api/v2/recognize', '',
                 query, ''))
        else:
            self._request_url = None

    @classmethod
    def get_config(cls):
        # FIXME: Replace this as soon as we have a config module
        config = {}
        # HMM dir
        # Try to get hmm_dir from config
        profile_path = jasperpath.config('profile.yml')
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = yaml.safe_load(f)
                if 'keys' in profile and 'GOOGLE_SPEECH' in profile['keys']:
                    config['api_key'] = profile['keys']['GOOGLE_SPEECH']
        return config

    def transcribe(self, fp):
        """
        Performs STT via the Google Speech API, transcribing an audio file and
        returning an English string.

        Arguments:
        audio_file_path -- the path to the .wav file to be transcribed
        """

        if not self.api_key:
            self._logger.critical('API key missing, transcription request ' +
                                  'aborted.')
            return []
        elif not self.language:
            self._logger.critical('Language info missing, transcription ' +
                                  'request aborted.')
            return []

        wav = wave.open(fp, 'rb')
        frame_rate = wav.getframerate()
        wav.close()
        data = fp.read()

        headers = {'content-type': 'audio/l16; rate=%s' % frame_rate}
        r = self._http.post(self.request_url, data=data, headers=headers)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            self._logger.critical('Request failed with http status %d',
                                  r.status_code)
            if r.status_code == requests.codes['forbidden']:
                self._logger.warning('Status 403 is probably caused by an ' +
                                     'invalid Google API key.')
            return []
        r.encoding = 'utf-8'
        try:
            # We cannot simply use r.json() because Google sends invalid json
            # (i.e. multiple json objects, seperated by newlines. We only want
            # the last one).
            response = json.loads(list(r.text.strip().split('\n', 1))[-1])
            if len(response['result']) == 0:
                # Response result is empty
                raise ValueError('Nothing has been transcribed.')
            results = [alt['transcript'] for alt
                       in response['result'][0]['alternative']]
        except ValueError as e:
            self._logger.warning('Empty response: %s', e.args[0])
            results = []
        except (KeyError, IndexError):
            self._logger.warning('Cannot parse response.', exc_info=True)
            results = []
        else:
            # Convert all results to uppercase
            results = tuple(result.upper() for result in results)
            self._logger.info('Transcribed: %r', results)
        return results

    @classmethod
    def is_available(cls):
        return diagnose.check_network_connection()
