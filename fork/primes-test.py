#!/usr/bin/env python3

import re
import sys

from os import getpid
from resource import prlimit, RLIMIT_NPROC, RLIMIT_NOFILE 
from subprocess import PIPE, run

from utils import are_equal, format_result

TESTS = [
    {
        'description': 'correct primes up to 10',
        'number': 10
    },
    {
        'description': 'correct primes up to 100',
        'number': 100
    },
    {
        'description': 'correct primes up to 1000',
        'number': 1000
    },
    {
        'description': 'correct primes up to 10000',
        'number': 10000
    }
]

def exec_command(args):
    # limits the number of open file descriptor
    # that the process or any of its child can have
    #
    # it has to be set to one more that the desired number
    prlimit(getpid(), RLIMIT_NOFILE, (10, 100))

    # limits the number of process that can be created
    # by a given process
    #
    # for the number 10000, a threshold of 1900 its OK
    #   (found it empirically -pic)
    prlimit(getpid(), RLIMIT_NPROC, (1900, 2000))

    proc = run(args, stdout=PIPE, stderr=PIPE, universal_newlines=True)

    stderr = proc.stderr

    if stderr is not '':
        raise Exception(stderr)

    output = proc.stdout.split('\n')

    return set(filter(lambda l: l != '', output))

def test_primes(binary_path, max_number):
    # - the `filter` removes lines not matching with the
    # pattern `primo %d`
    # - the `map` transforms the previous pattern leaving
    # just the number part `%d`
    return set(
        map(
            lambda s: int(s.split(' ')[1]),
            filter(
                lambda x: re.search(r'primo \d{1,4}', x),
                exec_command([binary_path, str(max_number)])
            )
        )
    )

def generate_primes(number):
    # JOS code (grade-lab5) to calculate primes in a given range
    rest = range(2, number)
    while rest:
        yield rest[0]
        rest = [n for n in rest if n % rest[0]]

def run_test(binary_path, test_config):
    description = test_config['description']
    number = test_config['number']

    expected_lines = set(generate_primes(number))

    resource_msg = None

    try:
        result_lines = test_primes(binary_path, number)
        res = are_equal(expected_lines, result_lines)
    except Exception as e:
        res = False
        resource_msg = f'Resource error - {e}'

    print(f'  {description}: {format_result(res)}')

    if resource_msg is not None:
        print(resource_msg)
        return res

    if not res:
        diff_res = expected_lines ^ result_lines
        if not (expected_lines <= result_lines):
            # missing prime numbers in result
            assertion_msg = f"""
Prime numbers missing:
---------------------
{diff_res}
            """
        else:
            # not prime numbers in result
            assertion_msg = f"""
NOT prime numbers:
-----------------
{diff_res}
            """
        print(assertion_msg)
    
    return res

def execute_tests(binary_path, tests):
    success = 0
    total = len(tests)

    for test_config in tests:
        res = run_test(binary_path, test_config)
        if res:
            success += 1

    print(f'{success}/{total} passed')

def main(binary_path):
    print('COMMAND: primes')

    execute_tests(binary_path, TESTS)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: primes-test.py PRIMES_BIN_PATH')
        sys.exit(1)

    binary_path = sys.argv[1]

    main(binary_path)
