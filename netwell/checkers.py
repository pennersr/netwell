import os
import re
import sys
from contextlib import contextmanager

import requests


class Outcome:

    def __init__(self):
        self.failed = False

    def fail(self, message=None):
        self.message = message
        self.failed = True


@contextmanager
def rule(description):
    sys.stdout.write(description + '... ')
    outcome = Outcome()
    try:
        yield outcome
    except:
        raise
        outcome.fail()
    if outcome.failed:
        if outcome.message:
            sys.stdout.write('ERROR\nERROR: ' + outcome.message + '\n')
        else:
            sys.stdout.write('ERROR\n')
    else:
        sys.stdout.write('OK')
    sys.stdout.write('\n')


class Checker:
    pass


class URL(Checker):

    def __init__(self, url):
        self.url = url
        self.response = None

    def _fetch(self):
        if not self.response:
            self.response = requests.get(self.url)
        return self.response

    def redirects_to(self, to_url):
        with rule(
                'Checking that {0} redirects to {1}'.format(
                self.url, to_url)) as outcome:
            response = self._fetch()
            if to_url != response.url:
                outcome.fail(
                    '{url} encountered'.format(
                        url=response.url))
        return self

    def title_matches(self, pattern):
        with rule(
                'Checking that {url} title matches "{pattern}"'.format(
                    url=self.url,
                    pattern=pattern)) as outcome:
            response = self._fetch()
            m = re.search('title>(?P<title>[^<]+)</ti', response.text)
            title = m.group('title').strip()
            if not re.search(pattern, title, re.I):
                outcome.fail(
                    'got "{title}"'.format(
                        title=title))
        return self


class DNS(Checker):

    def __init__(self, *netlocs):
        self.netlocs = netlocs

    def resolves_to(self, ip):
        for netloc in self.netlocs:
            self._resolves_to(netloc, ip)

    def _resolves_to(self, netloc, ip):
        with rule(
                'Checking that {netloc} resolves to {ip}'.format(
                    netloc=netloc,
                    ip=ip)) as outcome:
            gip = os.popen("dig @8.8.8.8 +short {0} | tail -1".format(
                netloc)).read().strip()
            if gip != ip:
                outcome.fail('got ' + gip)
