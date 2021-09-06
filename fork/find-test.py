#!/usr/bin/env python3

import sys

from os import makedirs
from pathlib import Path
from shutil import rmtree, copy
from subprocess import check_output

from utils import format_result

TEMP_DIR_PATH = 'tmpdirpattern'
TEMP_SUB_DIR_PATH = 'tmpsubdirpattern'
LINES = [
    f'/tmp/fisop-fork/{TEMP_DIR_PATH}/tmpfilepattern1',
    f'/tmp/fisop-fork/{TEMP_DIR_PATH}/tmpfilepattern2',
    f'/tmp/fisop-fork/{TEMP_DIR_PATH}/tmpfilePATTERN',
    f'/tmp/fisop-fork/{TEMP_DIR_PATH}/tmpfilePatTerN',
    f'/tmp/fisop-fork/{TEMP_DIR_PATH}/tmpfilePAT',
    f'/tmp/fisop-fork/{TEMP_DIR_PATH}/{TEMP_SUB_DIR_PATH}/tmpfileinsubdirPAT',
    f'/tmp/fisop-fork/{TEMP_DIR_PATH}/{TEMP_SUB_DIR_PATH}/tmpfileinsubdirPaT',
    f'/tmp/fisop-fork/{TEMP_DIR_PATH}/{TEMP_SUB_DIR_PATH}/tmpfileinsubdirpat'
]

def create_test_structure():
    makedirs(f'/tmp/fisop-fork/{TEMP_DIR_PATH}/{TEMP_SUB_DIR_PATH}', exist_ok=True)
    for file_path in LINES:
        Path(file_path).touch()

def remove_test_structure():
    rmtree('/tmp/fisop-fork')

def exec_command(args):
    return set(filter(
        lambda l: l != '',
        check_output(args, universal_newlines=True, cwd='/tmp/fisop-fork').split('\n')
    ))

def are_equal(expected, current):
    # ^ symmetric difference operator
    diff = expected ^ current

    return len(diff) == 0

def test_pattern_matching(binary_path, pattern, expected_lines, sensitive=True):
    if sensitive:
        command = [binary_path, pattern]
    else:
        command = [binary_path, '-i', pattern]

    result_lines = exec_command(command)

    return are_equal(expected_lines, result_lines)

def test_case_sensitive_1(binary_path):
    expected_lines = {
        'tmpdirpattern/tmpfilepattern2',
        'tmpdirpattern/tmpsubdirpattern/tmpfileinsubdirpat',
        'tmpdirpattern/tmpsubdirpattern',
        'tmpdirpattern/tmpfilepattern1',
        'tmpdirpattern'
    }
    return test_pattern_matching(binary_path, 'pat', expected_lines)

def test_case_sensitive_2(binary_path):
    expected_lines = {
        'tmpdirpattern/tmpfilePAT',
        'tmpdirpattern/tmpsubdirpattern/tmpfileinsubdirPAT',
        'tmpdirpattern/tmpfilePATTERN'
    }
    return test_pattern_matching(binary_path, 'PAT', expected_lines)

def test_case_sensitive_3(binary_path):
    expected_lines = {
        'tmpdirpattern/tmpfilePatTerN'
    }
    return test_pattern_matching(binary_path, 'Pat', expected_lines)

def test_case_sensitive_4(binary_path):
    expected_lines = set()
    return test_pattern_matching(binary_path, 'pAT', expected_lines)

def test_case_insensitive_1(binary_path):
    expected_lines = {
        'tmpdirpattern/tmpfilePAT',
        'tmpdirpattern/tmpfilepattern2',
        'tmpdirpattern/tmpsubdirpattern/tmpfileinsubdirPAT',
        'tmpdirpattern/tmpsubdirpattern/tmpfileinsubdirpat',
        'tmpdirpattern/tmpsubdirpattern/tmpfileinsubdirPaT',
        'tmpdirpattern/tmpsubdirpattern',
        'tmpdirpattern/tmpfilePATTERN',
        'tmpdirpattern/tmpfilepattern1',
        'tmpdirpattern/tmpfilePatTerN',
        'tmpdirpattern'
    }
    return test_pattern_matching(binary_path, 'pat', expected_lines, sensitive=False)

CASE_SENSITIVE_TESTS = [
    ('pattern: pat', test_case_sensitive_1),
    ('pattern: PAT', test_case_sensitive_2),
    ('pattern: Pat', test_case_sensitive_3),
    ('pattern: pAT', test_case_sensitive_4)
]

CASE_INSENSITIVE_TESTS = [
    ('pattern: pat', test_case_insensitive_1)
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
    create_test_structure()
    tmp_binary_path = f'/tmp/fisop-fork/find'
    copy(binary_path, tmp_binary_path)

    print('COMMAND: find')
    print('case sensitive')
    execute_tests(tmp_binary_path, CASE_SENSITIVE_TESTS)
    print('case insensitive')
    execute_tests(tmp_binary_path, CASE_INSENSITIVE_TESTS)

    remove_test_structure()
    print()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: find-test.py FIND_BIN_PATH')
        sys.exit(1)

    binary_path = sys.argv[1]

    main(binary_path)
