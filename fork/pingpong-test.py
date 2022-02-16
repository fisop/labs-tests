#!/usr/bin/env python3

import re
import sys

from unicodedata import normalize
from subprocess import check_output

from ttp import ttp
from utils import format_result

PROLOG_TEMPLATE = """
Hola, soy PID {{ parent_pid }}:
  - primer pipe me devuelve: [{{ first_pipe_read_fd }}, {{ first_pipe_write_fd }}]
  - segundo pipe me devuelve: [{{ second_pipe_read_fd }}, {{ second_pipe_write_fd }}]
"""

PARENT_TEMPLATE = """
Donde fork me devuelve {{ child_pid }}:
  - getpid me devuelve: {{ parent_pid }}
  - getppid me devuelve: {{ parent_parent_pid }}
  - random me devuelve: {{ random_number }}
  - envío valor {{ random_number_send }} a través de fd={{ pipe_fd_send }}
"""

CHILD_TEMPLATE = """
  - getpid me devuelve: {{ child_pid }}
  - getppid me devuelve: {{ parent_pid }}
  - recibo valor {{ random_number_recv }} vía fd={{ pipe_fd_recv }}
  - reenvío valor en fd={{ pipe_fd_send }} y termino
"""

EPILOG_TEMPLATE = """
Hola, de nuevo PID {{ parent_pid }}:
  - recibí valor {{ random_number_recv }} vía fd={{ pipe_fd_recv }}
"""

PIPE_FDS_RULES = [
    ('first pipe correct fds',
        lambda results: results['prolog']['first_pipe_read_fd'] <
            results['prolog']['first_pipe_write_fd']),
    ('second pipe correct fds',
        lambda results: results['prolog']['second_pipe_read_fd'] <
            results['prolog']['second_pipe_write_fd']),
    ('parent send correct fd',
        lambda results: results['prolog']['first_pipe_write_fd'] ==
            results['parent']['pipe_fd_send']),
    ('child recv correct fd',
        lambda results: results['child']['pipe_fd_recv'] ==
            results['prolog']['first_pipe_read_fd']),
    ('child send correct fd',
        lambda results: results['child']['pipe_fd_send'] ==
            results['prolog']['second_pipe_write_fd']),
    ('parent recv correct fd',
        lambda results: results['epilog']['pipe_fd_recv'] ==
            results['prolog']['second_pipe_read_fd'])
]

PROCESS_IDS_RULES = [
    ('parent pid correct', lambda results:
        results['prolog']['parent_pid'] == results['parent']['parent_pid'] and
        results['prolog']['parent_pid'] == results['epilog']['parent_pid']),
    ('child\'s parent pid correct',
        lambda results: results['prolog']['parent_pid'] == results['child']['parent_pid']),
    ('parent\'s child pid correct',
        lambda results: results['parent']['child_pid'] == results['child']['child_pid']),
    ('parent\'s parent pid correct',
        lambda results: results['parent']['parent_parent_pid'] < results['parent']['parent_pid'])
]

NUMBER_VALUES_RULES = [
    ('parent generated equal to sent',
        lambda results: results['parent']['random_number'] ==
            results['parent']['random_number_send']),
    ('parent generated equal to child recv',
        lambda results: results['parent']['random_number'] ==
            results['child']['random_number_recv']),
    ('parent recv equal to child\'s sent',
        lambda results: results['epilog']['random_number_recv'] ==
            results['child']['random_number_recv']),
    ('parent recv equal to sent',
        lambda results: results['epilog']['random_number_recv'] ==
        results['parent']['random_number_send']),
]

def exec_command(args):
    return check_output(args, universal_newlines=True)

def extract_values(results):
    """
    `results` can be in following forms:
        - f1: [ [ [ {}, {} ] ] ]
        - f2: [ [ {}, {} ] ]
    this functions returns the inner array of matching results
    to be analyzed later by the corresponding section parser
    """

    first_level = results[0]
    second_level = first_level[0]

    if type(second_level) is list:
        return second_level

    return first_level

def extract_section(result_lines, section_template):
    parser = ttp(data=result_lines, template=section_template)

    parser.parse()
    results = parser.result()

    return extract_values(results)

def parse_prolog(result_lines):
    values = extract_section(result_lines, PROLOG_TEMPLATE)

    return values[0]

def parse_parent(result_lines):
    values = extract_section(result_lines, PARENT_TEMPLATE)

    if 'random_number' in values[0]:
        return values[0]

    return values[1]

def parse_child(result_lines):
    values = extract_section(result_lines, CHILD_TEMPLATE)

    if 'random_number_recv' in values[0]:
        return values[0]

    return values[1]

def parse_epilog(result_lines):
    values = extract_section(result_lines, EPILOG_TEMPLATE)

    return values[0]

def parse_output(result_lines):
    return {
        'prolog': parse_prolog(result_lines),
        'parent': parse_parent(result_lines),
        'child': parse_child(result_lines),
        'epilog': parse_epilog(result_lines)
    }

def execute_rules(results, rules):
    success = 0
    total = len(rules)

    for rule_name, rule in rules:
        res = rule(results)
        if res:
            success += 1
        print(f'  {rule_name}: {format_result(res)}')

    print(f'{success}/{total} passed')

def sanitize_output(raw_output):
    # remove accents
    normalized = normalize("NFD", raw_output) \
                    .encode("ascii", "ignore") \
                    .decode()

    formatted = normalized.lower()

    # format output
    formatted = re.sub(r' *- *|\t *- *', '-', formatted)
    formatted = re.sub(r' *\n *\n *', '\n', formatted)
    formatted = re.sub(r' *= *', '=', formatted)
    formatted = re.sub(r' *, *', ', ', formatted)
    formatted = re.sub(r':', '', formatted)
    formatted = re.sub(r':|,|<|>', '', formatted)

    return formatted

def main(binary_path):
    print('COMMAND: pingpong')

    output = exec_command(binary_path)
    output = sanitize_output(output)
    results = parse_output(output)

    print('COMMAND: pingpong')
    print('check pipe fds')
    execute_rules(results, PIPE_FDS_RULES)
    print('check process ids')
    execute_rules(results, PROCESS_IDS_RULES)
    print('check random number values')
    execute_rules(results, NUMBER_VALUES_RULES)
    print()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: pingpong-test.py PINGPONG_BIN_PATH')
        sys.exit(1)

    binary_path = sys.argv[1]

    main(binary_path)
