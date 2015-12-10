==================
Welcome to Netvet!
==================

Given a netvet checkup file `checks.py`:
::

    from netvet.checkers import URL, DNS

    URL('http://fsf.org') \
        .redirects_to('http://www.fsf.org/') \
        .title_matches('Free Software Foundation')
    DNS('fsf.org', 'www.fsf.org').resolves_to('208.118.235.131')

Run `netvet /some/where/checks.py`:

::

    Checking that http://fsf.org redirects to http://www.fsf.org/... OK
    Checking that http://fsf.org title matches "Free Software Foundation"... OK
    Checking that fsf.org resolves to 208.118.235.131... OK
    Checking that www.fsf.org resolves to 208.118.235.131... OK
