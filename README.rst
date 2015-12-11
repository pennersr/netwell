===================
Welcome to Netwell!
===================

Installation
============

Python 3 is required::

   $ pip install netwell


Quickstart
==========

Given a netwell checkup file `checks.py`:
::

    from netwell.checkers import URL, DNS, Port

    URL('http://fsf.org') \
        .redirects_to('http://www.fsf.org/') \
        .title_matches('Free Software Foundation')
    Port('fsf.org', 443).ssl_valid_for(days=3000)
    DNS('fsf.org', 'www.fsf.org').resolves_to('208.118.235.131')

Then, run:

::

    $ netwell /some/where/checks.py
    Checking that http://fsf.org redirects to http://www.fsf.org/... OK
    Checking that http://fsf.org title matches "Free Software Foundation"... OK
    Checking that SSL at fsf.org:443 is valid for at least 3000 days... ERROR
    ERROR: Not valid after 2016-10-13
    Checking that fsf.org resolves to 208.118.235.131... OK
    Checking that www.fsf.org resolves to 208.118.235.131... OK

Use `--quiet` to only output the error messages, if any.
