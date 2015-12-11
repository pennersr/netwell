from netwell.checkers import URL, DNS

URL('http://fsf.org') \
    .redirects_to('http://www.fsf.org/') \
    .title_matches('Free Software Foundation')
DNS('fsf.org', 'www.fsf.org').resolves_to('208.118.235.131')
