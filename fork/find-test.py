#!/usr/bin/env python3

from ast import arg
import sys

from os import makedirs
from pathlib import Path
from shutil import rmtree, copy
from subprocess import PIPE, run

from utils import VALGRIND_COMMAND, are_equal, color, format_result, run_command

TEMP_FISOP_DIR_PATH = '/tmp/fisop-fork'
TEMP_DIR_PATH = 'tmpdirpattern'
TEMP_SUB_DIR_PATH = 'tmpsubdirpattern'
LINES = [
    f'{TEMP_FISOP_DIR_PATH}/{TEMP_DIR_PATH}/.hiddenfilepattern',
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
            'tmpdirpattern/.hiddenfilepattern',
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
            'tmpdirpattern/.hiddenfilepattern',
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

def exec_command(args, run_valgrind=False):
    output, valgrind_report, errors = run_command(args, cwd=TEMP_FISOP_DIR_PATH, run_valgrind=run_valgrind)

    if errors is not None:
        print(f"{color(errors, 'red')}")

    return set(
        map(
            lambda k: k[2:] if k.startswith("./") else k,
            filter(lambda l: l != '', output.split('\n'))
        )
    ), valgrind_report

def test_pattern_matching(binary_path, pattern, sensitive=True, run_valgrind=False):
    if sensitive:
        command = [binary_path, pattern]
    else:
        command = [binary_path, '-i', pattern]

    return exec_command(command, run_valgrind)

def run_test(binary_path, test_config, run_valgrind=False):
    description = test_config['description']
    pattern = test_config['pattern']
    sensitive = test_config['sensitive']
    expected_lines = test_config['expected-lines']

    result_lines, valgrind_report = test_pattern_matching(
        binary_path,
        pattern,
        sensitive=sensitive,
        run_valgrind=run_valgrind
    )

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
        print(valgrind_report)

    return res

def execute_tests(binary_path, tests, run_valgrind=False):
    success = 0
    total = len(tests)

    for test_config in tests:
        res = run_test(binary_path, test_config, run_valgrind)
        if res:
            success += 1

    if not run_valgrind:
        print(f'{success}/{total} passed')

def main(binary_path, run_valgrind):
    create_test_structure()
    tmp_binary_path = f'{TEMP_FISOP_DIR_PATH}/find'
    copy(binary_path, tmp_binary_path)

    print('COMMAND: find')
    execute_tests(tmp_binary_path, TESTS, run_valgrind)

    remove_test_structure()
    print()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: find-test.py FIND_BIN_PATH [-v]')
        sys.exit(1)

    binary_path = sys.argv[1]
    run_valgrind = True if len(sys.argv) > 2 and sys.argv[2] == '-v' else False

    main(binary_path, run_valgrind)
