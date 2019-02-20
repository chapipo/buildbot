# This file is part of Buildbot.  Buildbot is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright Buildbot Team Members

import datetime

from mock import Mock

from twisted.internet import defer
from twisted.trial import unittest

from buildbot import config
from buildbot.process.results import CANCELLED
from buildbot.process.results import EXCEPTION
from buildbot.process.results import FAILURE
from buildbot.process.results import RETRY
from buildbot.process.results import SKIPPED
from buildbot.process.results import SUCCESS
from buildbot.process.results import WARNINGS
from buildbot.reporters.slack import SlackStatusPush
from buildbot.test.fake import fakemaster
from buildbot.test.fake import httpclientservice as fakehttpclientservice
from buildbot.test.util.logging import LoggingMixin
from buildbot.test.util.reporter import ReporterTestMixin
from buildbot.util import UTC


class TestSlackStatusPush(unittest.TestCase, ReporterTestMixin, LoggingMixin):

    def setUp(self):
        # ignore config error if txrequests is not installed
        self.patch(config, '_errors', Mock())
        self.master = fakemaster.make_master(
            testcase=self, wantData=True, wantDb=True, wantMq=True)

    @defer.inlineCallbacks
    def tearDown(self):
        if self.master.running:
            yield self.master.stopService()

    @defer.inlineCallbacks
    def createReporter(self, **kwargs):
        endpoint = kwargs.get('endpoint', "toto")
        self.sp = SlackStatusPush(**kwargs)
        self._http = yield fakehttpclientservice.HTTPClientService.getFakeService(
            self.master, self, endpoint, debug=None, verify=None)
        yield self.sp.setServiceParent(self.master)
        yield self.master.startService()

    @defer.inlineCallbacks
    def setupBuildResults(self, results):
        self.insertTestData([results], results)
        build = yield self.master.data.get(("builds", 20))
        return build

    def test_urlTypeCheck(self):
        SlackStatusPush(2)
        config._errors.addError.assert_any_call('endpoint must be a string')

    def test_channelsTypeCheck(self):
        SlackStatusPush('api', channels="channel")
        config._errors.addError.assert_any_call('channels must be a list or None')

    @defer.inlineCallbacks
    def test_build_finished_success(self):
        yield self.createReporter(endpoint="t")
        build = yield self.setupBuildResults(SUCCESS)
        build['complete'] = True
        complete_at = datetime.datetime(1980, 6, 15, 12, 31, 15, tzinfo=UTC)
        build['complete_at'] = complete_at
        self._http.expect(
            'post',
            '',
            json={'attachments': [{'color': '#8d4', 'author_name': 'Builder0', 'title': 'Build #0 finished', 'title_link': 'http://localhost:8080/#builders/79/builds/0', 'ts': int(complete_at.timestamp())}]})

        self.sp.buildFinished(('build', 20, 'finished'), build)

    @defer.inlineCallbacks
    def test_build_finished_cancelled(self):
        yield self.createReporter(endpoint="t")
        build = yield self.setupBuildResults(CANCELLED)
        build['complete'] = True
        complete_at = datetime.datetime(1980, 6, 15, 12, 31, 15, tzinfo=UTC)
        build['complete_at'] = complete_at
        self._http.expect(
            'post',
            '',
            json={'attachments': [{'color': '#ecc', 'author_name': 'Builder0', 'title': 'Build #0 finished', 'title_link': 'http://localhost:8080/#builders/79/builds/0', 'ts': int(complete_at.timestamp())}]})

        self.sp.buildFinished(('build', 20, 'finished'), build)

    @defer.inlineCallbacks
    def test_build_finished_exception(self):
        yield self.createReporter(endpoint="t")
        build = yield self.setupBuildResults(EXCEPTION)
        build['complete'] = True
        complete_at = datetime.datetime(1980, 6, 15, 12, 31, 15, tzinfo=UTC)
        build['complete_at'] = complete_at
        self._http.expect(
            'post',
            '',
            json={'attachments': [{'color': '#c6c', 'author_name': 'Builder0', 'title': 'Build #0 finished', 'title_link': 'http://localhost:8080/#builders/79/builds/0', 'ts': int(complete_at.timestamp())}]})

        self.sp.buildFinished(('build', 20, 'finished'), build)

    @defer.inlineCallbacks
    def test_build_finished_failure(self):
        yield self.createReporter(endpoint="t")
        build = yield self.setupBuildResults(FAILURE)
        build['complete'] = True
        complete_at = datetime.datetime(1980, 6, 15, 12, 31, 15, tzinfo=UTC)
        build['complete_at'] = complete_at
        self._http.expect(
            'post',
            '',
            json={'attachments': [{'color': '#e88', 'author_name': 'Builder0', 'title': 'Build #0 finished', 'title_link': 'http://localhost:8080/#builders/79/builds/0', 'ts': int(complete_at.timestamp())}]})

        self.sp.buildFinished(('build', 20, 'finished'), build)

    @defer.inlineCallbacks
    def test_build_finished_retry(self):
        yield self.createReporter(endpoint="t")
        build = yield self.setupBuildResults(RETRY)
        build['complete'] = True
        complete_at = datetime.datetime(1980, 6, 15, 12, 31, 15, tzinfo=UTC)
        build['complete_at'] = complete_at
        self._http.expect(
            'post',
            '',
            json={'attachments': [{'color': '#ecc', 'author_name': 'Builder0', 'title': 'Build #0 finished', 'title_link': 'http://localhost:8080/#builders/79/builds/0', 'ts': int(complete_at.timestamp())}]})

        self.sp.buildFinished(('build', 20, 'finished'), build)

    @defer.inlineCallbacks
    def test_build_finished_cancelled(self):
        yield self.createReporter(endpoint="t")
        build = yield self.setupBuildResults(CANCELLED)
        build['complete'] = True
        complete_at = datetime.datetime(1980, 6, 15, 12, 31, 15, tzinfo=UTC)
        build['complete_at'] = complete_at
        self._http.expect(
            'post',
            '',
            json={'attachments': [{'color': '#ecc', 'author_name': 'Builder0', 'title': 'Build #0 finished', 'title_link': 'http://localhost:8080/#builders/79/builds/0', 'ts': int(complete_at.timestamp())}]})

        self.sp.buildFinished(('build', 20, 'finished'), build)

    @defer.inlineCallbacks
    def test_build_finished_warnings(self):
        yield self.createReporter(endpoint="t")
        build = yield self.setupBuildResults(WARNINGS)
        build['complete'] = True
        complete_at = datetime.datetime(1980, 6, 15, 12, 31, 15, tzinfo=UTC)
        build['complete_at'] = complete_at
        self._http.expect(
            'post',
            '',
            json={'attachments': [{'color': '#fa3', 'author_name': 'Builder0', 'title': 'Build #0 finished', 'title_link': 'http://localhost:8080/#builders/79/builds/0', 'ts': int(complete_at.timestamp())}]})

        self.sp.buildFinished(('build', 20, 'finished'), build)

    @defer.inlineCallbacks
    def test_build_finished_username(self):
        yield self.createReporter(endpoint="t", username="bb")
        build = yield self.setupBuildResults(SUCCESS)
        build['complete'] = True
        complete_at = datetime.datetime(1980, 6, 15, 12, 31, 15, tzinfo=UTC)
        build['complete_at'] = complete_at
        self._http.expect(
            'post',
            '',
            json={'username': 'bb', 'attachments': [{'color': '#8d4', 'author_name': 'Builder0', 'title': 'Build #0 finished', 'title_link': 'http://localhost:8080/#builders/79/builds/0', 'ts': int(complete_at.timestamp())}]})

        self.sp.buildFinished(('build', 20, 'finished'), build)

    @defer.inlineCallbacks
    def test_build_finished_channels(self):
        yield self.createReporter(endpoint="t", channels=["chan0", "chan1"])
        build = yield self.setupBuildResults(SUCCESS)
        build['complete'] = True
        complete_at = datetime.datetime(1980, 6, 15, 12, 31, 15, tzinfo=UTC)
        build['complete_at'] = complete_at
        self._http.expect(
            'post',
            '',
            json={'channel': 'chan0', 'attachments': [{'color': '#8d4', 'author_name': 'Builder0', 'title': 'Build #0 finished', 'title_link': 'http://localhost:8080/#builders/79/builds/0', 'ts': int(complete_at.timestamp())}]})
        self._http.expect(
            'post',
            '',
            json={'channel': 'chan1', 'attachments': [{'color': '#8d4', 'author_name': 'Builder0', 'title': 'Build #0 finished', 'title_link': 'http://localhost:8080/#builders/79/builds/0', 'ts': int(complete_at.timestamp())}]})

        self.sp.buildFinished(('build', 20, 'finished'), build)

    @defer.inlineCallbacks
    def test_build_finished_icon_url(self):
        yield self.createReporter(endpoint="t", icon_url="bb")
        build = yield self.setupBuildResults(SUCCESS)
        build['complete'] = True
        complete_at = datetime.datetime(1980, 6, 15, 12, 31, 15, tzinfo=UTC)
        build['complete_at'] = complete_at
        self._http.expect(
            'post',
            '',
            json={'icon_url': 'bb', 'attachments': [{'color': '#8d4', 'author_name': 'Builder0', 'title': 'Build #0 finished', 'title_link': 'http://localhost:8080/#builders/79/builds/0', 'ts': int(complete_at.timestamp())}]})

        self.sp.buildFinished(('build', 20, 'finished'), build)

    @defer.inlineCallbacks
    def test_no_message_sent_empty_message(self):
        yield self.createReporter(endpoint="toto")
        build = yield self.setupBuildResults(SUCCESS)
        self.sp.buildStarted(('build', 20, 'finished'), build)

    @defer.inlineCallbacks
    def test_postData_error(self):
        yield self.createReporter(endpoint="toto")
        build = yield self.setupBuildResults(SUCCESS)
        self.sp.getMessage = Mock()
        message = {'test': 1}
        self.sp.getMessage.return_value = message
        self._http.expect(
            'post',
            '',
            json=message,
            code=404,
            content_json={})
        self.setUpLogging()
        self.sp.buildFinished(('build', 20, 'finished'), build)
        self.assertLogged('404: unable to upload status')
