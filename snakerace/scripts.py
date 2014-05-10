import sys
import argparse
import importlib
import subprocess

from snakerace import getlines
from snakerace import tournament


def parse_getlines_params(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--sources', help='filename to be watched for executed lines',
        required=True, nargs='+')

    parser.add_argument(
        '--args', help='program to be executed', nargs='+', required=True)

    return parser.parse_args(args)


def parse_tournament_params(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'race', help='race callable')
    parser.add_argument(
        '--linespec-file', help='File containing line specifications',
        default='-')

    return parser.parse_args(args)


def run_tournament():
    params = parse_tournament_params(sys.argv[1:])
    race_class = get_race(params.race)
    if params.linespec_file == '-':
        linespec_source = sys.stdin
    else:
        linespec_source = open(params.linespec_file, 'rb')

    linespecs = [parse_linespec(line) for line in linespec_source.readlines()]

    race_conditions = tournament.run_tournament(linespecs, race_class())

    if race_conditions:
        for race_condition in race_conditions:
            sys.stderr.write(race_condition)
            sys.stderr.write('\n')

        sys.stderr.write("\nFAILED: %s race conditions\n\n" % len(
            race_conditions))
        sys.exit(1)
    else:
        sys.stdout.write('no race conditions found\n')


def parse_linespec(line):
    linespec = line.split(' ')[0]
    fname, lineno_string = linespec.split(':')
    return (fname, int(lineno_string))


def run_getlines():
    params = parse_getlines_params(sys.argv[1:])
    getlines.run_with_coverage(params.args, params.sources)
    for source in params.sources:
        for line in getlines.getlines(source):
            sys.stdout.write("{source}:{line}\n".format(
                source=source, line=line))


def get_race(path_to_callable):
    module_name, function_name = path_to_callable.split(':')
    module = importlib.import_module(module_name)
    return getattr(module, function_name)
