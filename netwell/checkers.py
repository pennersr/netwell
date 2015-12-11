import os
import re
import sys
from contextlib import contextmanager

import requests
from urllib.parse import urlparse
from dateutil.parser import parse as parse_date
from datetime import date, timedelta


class RuleFailedException(Exception):
    pass


class Output:

    def __init__(self):
        self.quiet = False
        self.line = ''
        self.line_error = False

    def info(self, text):
        if not self.quiet or self.line_error:
            sys.stdout.write(self.line)
            self.line = ''
            sys.stdout.write(text)
            sys.stdout.flush()
        else:
            self.line += text

    def error(self, text):
        self.line_error = True
        self.info(text)

    def eol(self):
        self.info('\n')
        self.line_error = False
        self.line = ''


output = Output()


class Outcome:

    def __init__(self):
        self.failed = False

    def fail(self, message=None):
        self.message = message
        self.failed = True
        raise RuleFailedException()


@contextmanager
def rule(description):
    output.info(description + '... ')
    outcome = Outcome()
    try:
        yield outcome
    except RuleFailedException:
        pass
    except:
        outcome.fail()
    if outcome.failed:
        if outcome.message:
            output.error('ERROR')
            output.eol()
            output.error('ERROR: ' + outcome.message)
        else:
            output.error('ERROR')
    else:
        output.info('OK')
    output.eol()


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

    def _get_netloc_port(self):
        parts = urlparse(self.url)
        netloc, _, port = parts.netloc.partition(':')
        if not port:
            if parts.scheme.lower() == 'https':
                port = 443
            else:
                port = 80
        return netloc, port


class Port(Checker):

    def __init__(self, netloc, port):
        self.netloc = netloc
        self.port = port

    def ssl_valid_for(self, *, days):
        with rule(
                'Checking that SSL at {netloc}:{port}'
                ' is valid for at least {days} days'.format(
                    netloc=self.netloc,
                    port=self.port,
                    days=days)) as outcome:
            cmd = ('openssl s_client -connect {netloc}:{port} </dev/null'
                   ' 2>/dev/null | openssl x509 -noout -dates'.format(
                       netloc=self.netloc,
                       port=self.port))
            not_before = None
            not_after = None
            with os.popen(cmd) as f:
                for line in f.readlines():
                    key, _, value = line.strip().partition('=')
                    if key in ['notBefore', 'notAfter']:
                        value = parse_date(value).date()
                        if key == 'notBefore':
                            not_before = value
                        else:
                            not_after = value
            if not not_before or not not_after:
                outcome.fail('Unable to determine SSL dates')
            now = date.today()
            if now < not_before:
                outcome.fail('Not valid before {}'.format(
                    not_before))
            if now + timedelta(days=days) > not_after:
                outcome.fail('Not valid after {}'.format(
                    not_after))
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
