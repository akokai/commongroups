# coding: utf-8

"""
Automatically populate compound groups using a chemical database.

Invoking this module runs a collection of commongroups operations:

-  Read compound group definitions either from the web (Google Sheets) or
   from a JSON file if specified.
-  Compile and perform database queries based on group definitions.
-  Output results to Excel and JSON and create a browseable HTML directory.
"""

import logging
import argparse

from commongroups.env import CommonEnv
from commongroups.ops import (batch_process,
                              cmgs_from_file,
                              cmgs_from_googlesheet)
from commongroups import logconf  # pylint: disable=unused-import
logger = logging.getLogger('commongroups')  # pylint: disable=invalid-name


def create_parser():
    """Create command-line argument parser."""
    desc = 'Automatically populate compound groups using a chemical database.'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-p', '--project', help='project name')
    parser.add_argument('-e', '--env_path', help='path to commongroups home')
    parser.add_argument('-d', '--database_url', help='database URL')
    parser.add_argument('-k', '--google_key_file',
                        help='Google credentials file')
    parser.add_argument('-g', '--google_sheet_title',
                        help='title of group definitions Google Sheet')
    parser.add_argument('-w', '--google_worksheet',
                        help='worksheet containing group definitions')
    parser.add_argument('-f', '--params_file',
                        help='read group parameters from file')
    parser.add_argument('-l', '--level', action='count',
                        help='show more logging output in console')
    parser.add_argument('-v', '--version', action='store_true',
                        help='print program version info and quit')
    return parser


def set_console_loglevel(level):
    """Change console log level from default (INFO), if specified."""
    console = logger.handlers[0]
    if not level:
        return
    elif level > 0:
        console.setLevel('DEBUG')


def print_version_info():
    """Print information about the program to the console."""
    from commongroups._about import (desc, __version__, __author__,
                                     __license__, __url__)
    info = '\n'.join(
        ['Common Groups', '{0}', 'version {1}', 'By {2}',
         'This program is distributed under a {3} license.',
         'For more information, see: {4}']
    ).format(desc, __version__, __author__, __license__, __url__)
    print(info)


def main():
    """Run commongroups operations."""
    parser = create_parser()
    args = parser.parse_args()

    if args.version:
        print_version_info()
        return

    set_console_loglevel(args.level)

    opt_keys = [
        'database_url',
        'google_key_file',
        'google_sheet_title',
        'google_worksheet'
    ]
    _args = vars(args)
    opts = {k: _args[k] for k in opt_keys if _args[k] is not None}

    env = CommonEnv(name=args.project,
                    env_path=args.env_path,
                    **opts)

    if args.params_file:
        cmg_gen = cmgs_from_file(env, args.params_file)
    else:
        cmg_gen = cmgs_from_googlesheet(env)

    batch_process(cmg_gen, env)


if __name__ == '__main__':
    main()
