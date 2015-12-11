"""
    _   __     __                ____
   / | / /__  / /__      _____  / / /
  /  |/ / _ \/ __/ | /| / / _ \/ / /
 / /|  /  __/ /_ | |/ |/ /  __/ / /
/_/ |_/\___/\__/ |__/|__/\___/_/_/
"""

VERSION = (0, 1, 1, 'final', 0)

__title__ = 'netwell'
__version_info__ = VERSION
__version__ = '.'.join(map(str, VERSION[:3])) + ('-{}{}'.format(
    VERSION[3], VERSION[4] or '') if VERSION[3] != 'final' else '')
__author__ = 'Raymond Penners'
__license__ = 'MIT'
__copyright__ = 'Copyright 2015 Raymond Penners'
