from netwell.checkers import URL, DNS, Port, Path, Repo

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
