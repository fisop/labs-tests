#!/usr/bin/env python3

import sys

from math import ceil
from subprocess import check_output

from utils import format_result

MAX_ARGS = 4

def exec_command(args, input_lines):
    encoded_lines = '\n'.join(input_lines) + '\n'

    return set(filter(
        lambda l: l != '',
        check_output(args, input=encoded_lines, universal_newlines=True).split('\n')
    ))

def are_equal(expected, current):
    # ^ symmetric difference operator
    diff = expected ^ current

    return len(diff) == 0

def test_packaging(binary_path, test_lines, expected_lines):
    result_lines = exec_command([binary_path, './argcounter.py'], test_lines)

    return are_equal(expected_lines, result_lines)

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

def run_test(binary_path, amount_of_arguments = MAX_ARGS):
    test_lines = generate_input(amount_of_arguments)
    expected_lines = generate_output(amount_of_arguments)

    return test_packaging(binary_path, test_lines, expected_lines)

PACKAGING_TESTS = [
    ('less amount', lambda binary_path: run_test(binary_path, amount_of_arguments=3)),
    ('same amount', lambda binary_path: run_test(binary_path, amount_of_arguments=4)),
    ('more amount', lambda binary_path: run_test(binary_path, amount_of_arguments=6)),
    ('twice the amount', lambda binary_path: run_test(binary_path, amount_of_arguments=8)),
    ('above twice the amount', lambda binary_path: run_test(binary_path, amount_of_arguments=9))
]

def execute_tests(binary_path, tests):
    success = 0
    total = len(tests)

    for test_name, test in tests:
        res = test(binary_path)
        if res:
            success += 1
        print(f'  {test_name}: {format_result(res)}')

    print(f'{success}/{total} passed')

def main(binary_path):
    print('COMMAND: xargs')
    print('packaging arguments')
    execute_tests(binary_path, PACKAGING_TESTS)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: xargs-test.py XARGS_BIN_PATH')
        sys.exit(1)

    binary_path = sys.argv[1]

    main(binary_path)
