#!/usr/bin/env python3

import sys

from math import ceil
from subprocess import PIPE, run

from utils import VALGRIND_COMMAND, are_equal, format_result

MAX_ARGS = 4

TESTS = [
    {
        'description': '[ARGS SENT] - less',
        'amount-arguments': MAX_ARGS - 1
    },
    {
        'description': '[ARGS SENT] - same',
        'amount-arguments': MAX_ARGS
    },
    {
        'description': '[ARGS SENT] - more',
        'amount-arguments': MAX_ARGS + 1
    },
    {
        'description': '[ARGS SENT] - twice',
        'amount-arguments': 2 * MAX_ARGS
    },
    {
        'description': '[ARGS SENT] - above twice',
        'amount-arguments': 2 * MAX_ARGS + 1
    }
]

def exec_command(args, input_lines, run_valgrind=False):
    if run_valgrind:
        args = VALGRIND_COMMAND + args

    encoded_lines = '\n'.join(input_lines) + '\n'

    proc = run(args, stdout=PIPE, stderr=PIPE, input=encoded_lines, universal_newlines=True)

    output = proc.stdout.split('\n')

    if run_valgrind:
        valgrind = proc.stderr.split('\n')
    else:
        valgrind = []

    return set(filter(lambda l: l != '', output)), valgrind

def test_packaging(binary_path, test_lines, run_valgrind=False):
    return exec_command([binary_path, './argcounter.py'], test_lines, run_valgrind)

def generate_input(amount_of_arguments):
    return [f'arg{i}' for i in range(amount_of_arguments)]

def generate_output(amount_of_arguments):
    lines = []

    packages = ceil(amount_of_arguments / MAX_ARGS)
    arg_id = 0

    for id in range(packages):
        pkg_args = min(MAX_ARGS, amount_of_arguments - MAX_ARGS * id)
        for i in range(1, pkg_args + 1):
            lines.append(f'arg[{i}]: arg{arg_id}')
            arg_id += 1

    return set(lines)

def run_test(binary_path, test_config, run_valgrind=False):
    description = test_config['description']
    amount_of_arguments = test_config['amount-arguments']

    test_lines = generate_input(amount_of_arguments)
    expected_lines = generate_output(amount_of_arguments)

    result_lines, valgrind = test_packaging(binary_path, test_lines, run_valgrind)

    res = are_equal(expected_lines, result_lines)

    print(f'  {description}: {format_result(res)}')

    if not res:
        expected_fmt = '\n' + '\n'.join(expected_lines)
        result_fmt = '\n' + '\n'.join(result_lines) if len(result_lines) > 0 else 'no results'
        assertion_msg = f"""
Expected:
--------
{expected_fmt}

Got:
---
{result_fmt}
        """
        print(assertion_msg)

    if run_valgrind:
        print('  VALGRIND OUTPUT:')
        print('\t' + '\t'.join(map(lambda l: l + '\n', valgrind)))

    return res

def execute_tests(binary_path, tests, run_valgrind=False):
    success = 0
    total = len(tests)

    for test_config in tests:
        res = run_test(binary_path, test_config, run_valgrind)
        if res:
            success += 1

    print(f'{success}/{total} passed')

def main(binary_path, run_valgrind):
    print('COMMAND: xargs')
    print(f'packaging arguments [ARGS IN PACKAGE: {MAX_ARGS}]')

    execute_tests(binary_path, TESTS, run_valgrind)
    print()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: xargs-test.py XARGS_BIN_PATH [-v]')
        sys.exit(1)

    binary_path = sys.argv[1]
    run_valgrind = True if len(sys.argv) > 2 and sys.argv[2] == '-v' else False

    main(binary_path, run_valgrind)
