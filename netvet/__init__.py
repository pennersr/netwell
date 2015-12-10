"""
 _______          __ ____   ____      __
 \      \   _____/  |\   \ /   /_____/  |_
 /   |   \_/ __ \   __\   Y   // __ \   __\
/    |    \  ___/|  |  \     /\  ___/|  |
\____|__  /\___  >__|   \___/  \___  >__|
        \/     \/                  \/
"""

VERSION = (0, 1, 0, 'dev', 0)

__title__ = 'netvet'
__version_info__ = VERSION
__version__ = '.'.join(map(str, VERSION[:3])) + ('-{}{}'.format(
    VERSION[3], VERSION[4] or '') if VERSION[3] != 'final' else '')
__author__ = 'Raymond Penners'
__license__ = 'MIT'
__copyright__ = 'Copyright 2015 Raymond Penners'
