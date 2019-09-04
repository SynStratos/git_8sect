import sys
import argparse

class MyParser(argparse.ArgumentParser):
    description = 'Process script parameters.'

    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

def parse(args):
    parser = MyParser()
    type_group = parser.add_mutually_exclusive_group(required=True)
    type_group.add_argument('-c', '--commits', default=False, action='store_true',
                            help='use sha1 identifier')
    type_group.add_argument('-d', '--dates', default=False, action='store_true',
                        help='use dates')
    type_group.add_argument('-t', '--timestamps', default=False, action='store_true',
                            help='use timestamps')

    parser.add_argument('bad_commit', help='define the sha1 or date of the bad commit')
    parser.add_argument('good_commit', help='define the sha1 or date of the good commit')

    parser.add_argument('-s', '--script', help='define the shell script to run as benchmark')

    args = parser.parse_args(args)

    return args
