from netwell import checkers
import argparse

from importlib.machinery import SourceFileLoader


def handle():
    parser = argparse.ArgumentParser(
        description='Run checkups for your net infrastructure.')
    parser.add_argument(
        'specfile',
        metavar='specfile',
        type=str,
        nargs=1,
        help='The netwell spec file')
    parser.add_argument(
        '-q',
        '--quiet',
        action='store_true',
        help='Quiet, only report errors')

    args = parser.parse_args()
    checkers.output.quiet = args.quiet
    SourceFileLoader("specfile", args.specfile[0]).load_module()
