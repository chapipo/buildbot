from future.utils import string_types

from twisted.internet import defer

from buildbot import config
from buildbot.process.results import CANCELLED
from buildbot.process.results import EXCEPTION
from buildbot.process.results import FAILURE
from buildbot.process.results import RETRY
from buildbot.process.results import SKIPPED
from buildbot.process.results import SUCCESS
from buildbot.process.results import WARNINGS
from buildbot.reporters import utils
from buildbot.reporters.http import HttpStatusPushBase
from buildbot.util import httpclientservice
from buildbot.util.logger import Logger

log = Logger()


class SlackStatusPush(HttpStatusPushBase):
    name = "SlackStatusPush"

    def checkConfig(self, endpoint, username=None, channels=None, icon_url=None, **kwargs):
        if not isinstance(endpoint, string_types):
            config.error('endpoint must be a string')
        if not isinstance(username, (string_types, type(None))):
            config.error('username must be a string or None')
        if not isinstance(channels, (list, type(None))):
            config.error('channels must be a list or None')
        if not isinstance(icon_url, (string_types, type(None))):
            config.error('username must be a string or None')

    @defer.inlineCallbacks
    def reconfigService(self, endpoint, username=None, channels=None, icon_url=None, **kwargs):
        yield HttpStatusPushBase.reconfigService(self, **kwargs)
        self._http = yield httpclientservice.HTTPClientService.getService(
            self.master, endpoint,
            debug=self.debug, verify=self.verify)
        self._username = username
        self._channels = channels
        self._icon_url = icon_url

    def getMessage(self, build):
        message = None

        if build['complete']:
            color = {
                SUCCESS: '#8d4',
                WARNINGS: '#fa3',
                FAILURE: '#e88',
                SKIPPED: '#ade',
                EXCEPTION: '#c6c',
                RETRY: '#ecc',
                CANCELLED: '#ecc',
            }.get(build['results'])
            message = {
                "attachments": [
                    {
                        "color": color,
                        "author_name": build['builder']['name'],
                        "title": "Build #%i finished" % (build['number']),
                        "title_link": build['url'],
                        "ts": int(build['complete_at'].timestamp()),
                    }
                ]
            }
        return message

    @defer.inlineCallbacks
    def sendMessage(self, postData):
        response = yield self._http.post("", json=postData)
        if response.code != 200:
            content = yield response.content()
            log.error("{code}: unable to upload status: {content}",
                      code=response.code, content=content)

    @defer.inlineCallbacks
    def send(self, build):
        postData = yield self.getMessage(build)
        if postData is None:
            return

        if self._username is not None:
            postData['username'] = self._username

        if self._icon_url is not None:
            postData['icon_url'] = self._icon_url

        if self._channels is None:
            yield self.sendMessage(postData)
            return

        for channel in self._channels:
            postData['channel'] = channel
            yield self.sendMessage(postData)
