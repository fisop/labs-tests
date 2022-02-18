#!/usr/bin/env python3

import sys

from os import makedirs
from pathlib import Path
from shutil import rmtree, copy
from subprocess import check_output

from utils import format_result

TEMP_FISOP_DIR_PATH = '/tmp/fisop-fork'
TEMP_DIR_PATH = 'tmpdirpattern'
TEMP_SUB_DIR_PATH = 'tmpsubdirpattern'
LINES = [
    f'{TEMP_FISOP_DIR_PATH}/{TEMP_DIR_PATH}/tmpfilepattern1',
    f'{TEMP_FISOP_DIR_PATH}/{TEMP_DIR_PATH}/tmpfilepattern2',
    f'{TEMP_FISOP_DIR_PATH}/{TEMP_DIR_PATH}/tmpfilePATTERN',
    f'{TEMP_FISOP_DIR_PATH}/{TEMP_DIR_PATH}/tmpfilePatTerN',
    f'{TEMP_FISOP_DIR_PATH}/{TEMP_DIR_PATH}/tmpfilePAT',
    f'{TEMP_FISOP_DIR_PATH}/{TEMP_DIR_PATH}/{TEMP_SUB_DIR_PATH}/tmpfileinsubdirPAT',
    f'{TEMP_FISOP_DIR_PATH}/{TEMP_DIR_PATH}/{TEMP_SUB_DIR_PATH}/tmpfileinsubdirPaT',
    f'{TEMP_FISOP_DIR_PATH}/{TEMP_DIR_PATH}/{TEMP_SUB_DIR_PATH}/tmpfileinsubdirpat'
]

TESTS = [
    {
        'description': '[SENSITIVE]   - pattern: pat',
        'pattern': 'pat',
        'sensitive': True,
        'expected-lines': {
            'tmpdirpattern/tmpfilepattern2',
            'tmpdirpattern/tmpsubdirpattern/tmpfileinsubdirpat',
            'tmpdirpattern/tmpsubdirpattern',
            'tmpdirpattern/tmpfilepattern1',
            'tmpdirpattern'
        }
    },
    {
        'description': '[SENSITIVE]   - pattern: PAT',
        'pattern': 'PAT',
        'sensitive': True,
        'expected-lines': {
            'tmpdirpattern/tmpfilePAT',
            'tmpdirpattern/tmpsubdirpattern/tmpfileinsubdirPAT',
            'tmpdirpattern/tmpfilePATTERN'
        }
    },
    {
        'description': '[SENSITIVE]   - pattern: Pat',
        'pattern': 'Pat',
        'sensitive': True,
        'expected-lines': {
            'tmpdirpattern/tmpfilePatTerN'
        }
    },
    {
        'description': '[SENSITIVE]   - pattern: pAT',
        'pattern': 'pAT',
        'sensitive': True,
        'expected-lines': set()
    },
    {
        'description': '[INSENSITIVE] - pattern: pat',
        'pattern': 'pat',
        'sensitive': False,
        'expected-lines': {
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
    }
]

def create_test_structure():
    makedirs(f'{TEMP_FISOP_DIR_PATH}/{TEMP_DIR_PATH}/{TEMP_SUB_DIR_PATH}', exist_ok=True)
    for file_path in LINES:
        Path(file_path).touch()

def remove_test_structure():
    rmtree(TEMP_FISOP_DIR_PATH)

def exec_command(args):
    return set(
        map(
            lambda k: k[2:] if k.startswith("./") else k,
            filter(
                lambda l: l != '',
                check_output(args, universal_newlines=True, cwd=TEMP_FISOP_DIR_PATH).split('\n')
            )
        )
    )

def are_equal(expected, current):
    # ^ symmetric difference operator
    diff = expected ^ current

    return len(diff) == 0

def test_pattern_matching(binary_path, pattern, sensitive=True):
    if sensitive:
        command = [binary_path, pattern]
    else:
        command = [binary_path, '-i', pattern]

    return exec_command(command)

def run_test(binary_path, test_config):
    description = test_config['description']
    pattern = test_config['pattern']
    sensitive = test_config['sensitive']
    expected_lines = test_config['expected-lines']

    result_lines = test_pattern_matching(binary_path, pattern, sensitive=sensitive)

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
    create_test_structure()
    tmp_binary_path = f'{TEMP_FISOP_DIR_PATH}/find'
    copy(binary_path, tmp_binary_path)

    print('COMMAND: find')
    execute_tests(tmp_binary_path, TESTS)

    remove_test_structure()
    print()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: find-test.py FIND_BIN_PATH')
        sys.exit(1)

    binary_path = sys.argv[1]

    main(binary_path)
