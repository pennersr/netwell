import os
import re
import socket
import ssl
import subprocess
import sys
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from urllib.parse import urlparse

import requests
from dateutil.parser import parse as parse_date


class RuleFailedException(Exception):
    pass


class Output:
    def __init__(self):
        self.quiet = False
        self.line = ""
        self.line_error = False

    def info(self, text):
        if not self.quiet or self.line_error:
            sys.stdout.write(self.line)
            self.line = ""
            sys.stdout.write(text)
            sys.stdout.flush()
        else:
            self.line += text

    def error(self, text):
        self.line_error = True
        self.info(text)

    def eol(self):
        self.info("\n")
        self.line_error = False
        self.line = ""


output = Output()


class Result:
    def __init__(self):
        self.failures = 0
        self.checks = 0


result = Result()


class Outcome:
    def __init__(self):
        self.failed = False
        self.message = None

    def fail(self, message=None):
        self.message = message
        self.failed = True
        raise RuleFailedException()


@contextmanager
def rule(description):
    output.info(description + "... ")
    outcome = Outcome()
    try:
        result.checks += 1
        yield outcome
    except RuleFailedException:
        pass
    except:  # noqa
        outcome.failed = True
    if outcome.failed:
        result.failures += 1
        if outcome.message:
            output.error("ERROR")
            output.eol()
            output.error("ERROR: " + outcome.message)
        else:
            output.error("ERROR")
    else:
        output.info("OK")
    output.eol()


class Checker:
    pass


class URL(Checker):
    def __init__(self, url):
        self.url = url
        self.response = None

    def _fetch(self):
        if not self.response:
            self.response = requests.get(self.url, timeout=10)
        return self.response

    def redirects_to(self, to_url):
        with rule(
            "Checking that {0} redirects to {1}".format(self.url, to_url)
        ) as outcome:
            response = self._fetch()
            if to_url != response.url:
                outcome.fail("{url} encountered".format(url=response.url))
        return self

    def title_matches(self, pattern):
        with rule(
            'Checking that {url} title matches "{pattern}"'.format(
                url=self.url, pattern=pattern
            )
        ) as outcome:
            response = self._fetch()
            m = re.search("title>(?P<title>[^<]+)</ti", response.text)
            title = m.group("title").strip()
            if not re.search(pattern, title, re.I):
                outcome.fail('got "{title}"'.format(title=title))
        return self

    def has_header(self, header, value=None):
        """
        Checks if the specified header is present. In case a value is
        provided, it is checked if the value matches.
        """
        description = 'Checking that {url} has header "{header}"'
        if value is not None:
            description += ': "{value}"'
        with rule(
            description.format(url=self.url, header=header, value=value)
        ) as outcome:
            response = self._fetch()
            if value is not None:
                actual_value = response.headers.get(header, "")
                if actual_value != value:
                    outcome.fail("got {}".format(actual_value))
            else:
                if header not in response.headers:
                    outcome.fail("not found")
        return self

    def check_response(self, func):
        with rule(
            "Checking that {url} passes {func}".format(
                url=self.url, func=func.__name__
            )
        ) as outcome:
            response = self._fetch()
            func(response, outcome)
        return self

    def _get_netloc_port(self):
        parts = urlparse(self.url)
        netloc, _, port = parts.netloc.partition(":")
        if not port:
            if parts.scheme.lower() == "https":
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
            "Checking that SSL at {netloc}:{port}"
            " is valid for at least {days} days".format(
                netloc=self.netloc, port=self.port, days=days
            )
        ) as outcome:
            try:
                context = ssl.create_default_context()
                with socket.create_connection(
                    (self.netloc, self.port)
                ) as sock:
                    with context.wrap_socket(
                        sock, server_hostname=self.netloc
                    ) as ssl_sock:
                        self.cert = ssl_sock.getpeercert()
            except ssl.SSLError as e:
                outcome.fail("TLS error: {}".format(e))
            else:
                not_before = self._parse_date(self.cert.get("notBefore"))
                not_after = self._parse_date(self.cert.get("notAfter"))

                now = datetime.now()

                if not not_before or not not_after:
                    outcome.fail("Unable to determine SSL dates")

                if now < not_before:
                    outcome.fail("Not valid before {}".format(not_before))

                if now + timedelta(days=days) > not_after:
                    outcome.fail("Not valid after {}".format(not_after))

            return self

    def _parse_date(self, d):
        for fmt in ["%c", "%b %d %H:%M:%S %Y %Z"]:
            try:
                return datetime.strptime(d, fmt)
            except ValueError:
                pass


class DNS(Checker):
    def __init__(self, *netlocs):
        self.netlocs = netlocs

    def resolves_to(self, ip):
        for netloc in self.netlocs:
            self._resolves_to(netloc, ip)

    def _resolves_to(self, netloc, ip):
        with rule(
            "Checking that {netloc} resolves to {ip}".format(
                netloc=netloc, ip=ip
            )
        ) as outcome:
            sockets = socket.getaddrinfo(netloc, None)
            ips = [endpoint[4][0] for endpoint in sockets]
            if ip not in ips:
                outcome.fail("got " + ips)


class Path(Checker):
    def __init__(self, path):
        self.path = path

    def modified_within(self, **kwargs):
        after = datetime.now() - timedelta(**kwargs)
        with rule(
            "Checking that {path} was modified after {dt}".format(
                path=self.path, dt=after
            )
        ) as outcome:
            t = os.path.getmtime(self.path)
            dt = datetime.fromtimestamp(t)
            if dt < after:
                outcome.fail("Last modified at {}".format(dt))

    def free_space(self, mb=None, gb=None):
        assert not mb or not gb
        if mb is not None:
            unit = "MB"
            bytes_per_unit = 1024 ** 2
        else:
            unit = "GB"
            bytes_per_unit = 1024 ** 3
        value = mb or gb
        with rule(
            "Checking that {path} has {value} {unit} free space".format(
                unit=unit, path=self.path, value=value
            )
        ) as outcome:
            st = os.statvfs(self.path)
            free = st.f_bavail * st.f_frsize
            # total = (st.f_blocks * st.f_frsize)
            # used = (st.f_blocks - st.f_bfree) * st.f_frsize
            free /= bytes_per_unit
            if free < value:
                outcome.fail(
                    "Only {free:.1f} {unit} free".format(free=free, unit=unit)
                )


class Repo(Checker):
    def __init__(self, path):
        self.path = path

    def is_clean(self):
        with rule(
            "Checking that repository {path} is clean".format(path=self.path)
        ) as outcome:
            if not os.path.exists(os.path.join(self.path, ".git")):
                outcome.fail("No repository present")
            if not self._run_exit_0(["git", "diff", "--exit-code"]):
                outcome.fail("Local unstaged changes found")
            if not self._run_exit_0(
                ["git", "diff", "--cached", "--exit-code"]
            ):
                outcome.fail("Uncommitted, staged changes found")
            if self._has_untracked():
                outcome.fail("Untracked files found")

    def _has_untracked(self):
        out = subprocess.check_output(
            [
                "git",
                "ls-files",
                "--other",
                "--exclude-standard",
                "--directory",
                "--no-empty-directory",
            ],
            cwd=self.path,
        )
        return len(out) > 0

    def _run_exit_0(self, args):
        try:
            subprocess.check_output(args, cwd=self.path)
            ret = True
        except subprocess.CalledProcessError:
            ret = False
        return ret
