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

    args = parser.parse_args()
    SourceFileLoader("specfile", args.specfile[0]).load_module()
