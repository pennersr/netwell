===================
Welcome to Netwell!
===================

.. image:: https://badge.fury.io/py/netwell.svg
   :target: http://badge.fury.io/py/netwell

.. image:: https://travis-ci.org/pennersr/netwell.svg
   :target: http://travis-ci.org/pennersr/netwell

.. image:: https://img.shields.io/pypi/v/netwell.svg
   :target: https://pypi.python.org/pypi/netwell

.. image:: https://pennersr.github.io/img/bitcoin-badge.svg
   :target: https://blockchain.info/address/1AJXuBMPHkaDCNX2rwAy34bGgs7hmrePEr

.. image:: https://img.shields.io/badge/code%20style-pep8-green.svg
   :target: https://www.python.org/dev/peps/pep-0008/


Installation
============

Python 3 is required::

   $ pip install netwell


Quickstart
==========

Given a netwell checkup file `checks.py`:
::

    from netwell.checkers import URL, DNS, Port, Repo, Path

    URL('http://fsf.org') \
        .redirects_to('https://www.fsf.org/') \
        .title_matches('Free Software Foundation') \
        .has_header('Content-Type', 'text/html;charset=utf-8')
    Port('fsf.org', 443).ssl_valid_for(days=3000)
    DNS('fsf.org', 'www.fsf.org').resolves_to('209.51.188.174')
    Path('/').free_space(gb=1)
    Path('/var/log/syslog').modified_within(hours=1)
    Repo('/home/deploy/src/project').is_clean()

    def custom_check(response, outcome):
        data = response.json()
        if data:
            outcome.fail('Other data expected')

    URL('http://httpbin.org/get').check_response(custom_check)

Then, run:

::

    $ netwell /some/where/checks.py
    Checking that http://fsf.org redirects to http://www.fsf.org/... OK
    Checking that http://fsf.org title matches "Free Software Foundation"... OK
    Checking that http://fsf.org has header "Content-Type": "text/html;charset=utf-8"... OK
    Checking that SSL at fsf.org:443 is valid for at least 3000 days... ERROR
    ERROR: Not valid after 2016-10-13
    Checking that fsf.org resolves to 208.118.235.131... OK
    Checking that www.fsf.org resolves to 208.118.235.131... OK
    Checking that / has 1 GB free space... ERROR
    ERROR: Only 0.5 GB free
    Checking that /var/log/syslog was modified after 2015-12-27 22:21:05.873355... OK
    Checking that http://httpbin.org/get passes custom_check... ERROR
    ERROR: Other data expected
    Checking that repository /home/deploy/src/project is clean... ERROR
    ERROR: Untracked files found


Use `--quiet` to only output the error messages, if any.
