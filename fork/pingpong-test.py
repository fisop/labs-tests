#!/usr/bin/env python3

from doctest import FAIL_FAST
import re
import sys

from unicodedata import normalize
from subprocess import PIPE, run

from ttp import ttp
from utils import VALGRIND_COMMAND, color, format_result

PROLOG_KEYWORDS = [
    'parent_pid',
    'first_pipe_read_fd',
    'first_pipe_write_fd',
    'second_pipe_read_fd',
    'second_pipe_write_fd'
]

PROLOG_TEMPLATE = """
hola soy pid {{ parent_pid }}
-primer pipe me devuelve [{{ first_pipe_read_fd }} {{ first_pipe_write_fd }}]
-segundo pipe me devuelve [{{ second_pipe_read_fd }} {{ second_pipe_write_fd }}]
"""

PARENT_KEYWORDS = [
    'child_pid',
    'parent_pid',
    'parent_parent_pid',
    'random_number',
    'random_number_send',
    'pipe_fd_send'
]

PARENT_TEMPLATE = """
donde fork me devuelve {{ child_pid }}
-getpid me devuelve {{ parent_pid }}
-getppid me devuelve {{ parent_parent_pid }}
-random me devuelve {{ random_number }}
-envio valor {{ random_number_send }} a traves de fd={{ pipe_fd_send }}
"""

CHILD_KEYWORDS = [
    'child_pid',
    'parent_pid',
    'random_number_recv',
    'pipe_fd_recv',
    'pipe_fd_send'
]

CHILD_TEMPLATE = """
-getpid me devuelve {{ child_pid }}
-getppid me devuelve {{ parent_pid }}
-recibo valor {{ random_number_recv }} via fd={{ pipe_fd_recv }}
-reenvio valor en fd={{ pipe_fd_send }} y termino
"""

EPILOG_KEYWORDS = [
    'parent_pid',
    'random_number_recv',
    'pipe_fd_recv'
]

EPILOG_TEMPLATE = """
hola de nuevo pid {{ parent_pid }}
-recibi valor {{ random_number_recv }} via fd={{ pipe_fd_recv }}
"""

PIPE_FDS_RULES = [
    ('[PROLOG] - first pipe correct fd numbers',
        lambda results: results['prolog']['first_pipe_read_fd'] <
            results['prolog']['first_pipe_write_fd']),
    ('[PROLOG] - second pipe correct fd numbers',
        lambda results: results['prolog']['second_pipe_read_fd'] <
            results['prolog']['second_pipe_write_fd']),
    ('[PARENT] - correct fd number [SEND]',
        lambda results: results['prolog']['first_pipe_write_fd'] ==
            results['parent']['pipe_fd_send']),
    ('[PARENT] - correct fd number [RECV]',
        lambda results: results['epilog']['pipe_fd_recv'] ==
            results['prolog']['second_pipe_read_fd']),
    ('[CHILD]  - correct fd number [SEND]',
        lambda results: results['child']['pipe_fd_send'] ==
            results['prolog']['second_pipe_write_fd']),
    ('[CHILD]  - correct fd number [RECV]',
        lambda results: results['child']['pipe_fd_recv'] ==
            results['prolog']['first_pipe_read_fd'])
]

PROCESS_IDS_RULES = [
    ('[EPILOG] - correct pid number',
        lambda results: results['epilog']['parent_pid'] == results['prolog']['parent_pid']),
    ('[PARENT] - correct parent pid number',
        lambda results: results['parent']['parent_pid'] == results['prolog']['parent_pid']),
    ('[CHILD]  - correct parent pid number',
        lambda results: results['child']['parent_pid'] == results['prolog']['parent_pid']),
    ('[PARENT] - correct child pid number',
        lambda results: results['parent']['child_pid'] == results['child']['child_pid']),
    ('[PARENT] - correct relation of pid and ppid',
        lambda results: results['parent']['parent_parent_pid'] < results['parent']['parent_pid'])
]

NUMBER_VALUES_RULES = [
    ('[PARENT] - correct relation of generated and sent value',
        lambda results: results['parent']['random_number'] ==
            results['parent']['random_number_send']),
    ('[CHILD]  - correct relation of parent\'s generated and received value',
        lambda results: results['parent']['random_number'] ==
            results['child']['random_number_recv']),
    ('[PARENT] - correct relation of received and child\'s sent',
        lambda results: results['epilog']['random_number_recv'] ==
            results['child']['random_number_recv']),
    ('[EPILOG] - correct relation of parent\'s received and sent',
        lambda results: results['epilog']['random_number_recv'] ==
            results['parent']['random_number_send']),
]

def exec_command(args, run_valgrind=False):
    if run_valgrind:
        args = VALGRIND_COMMAND + args

    proc = run(args, stdout=PIPE, stderr=PIPE, universal_newlines=True)

    if run_valgrind:
        valgrind = proc.stderr.split('\n')
    else:
        valgrind = []

    return proc.stdout, valgrind

def extract_values(results):
    """
    `results` can be in following forms:
        - f1: [ [ [ {}, {} ] ] ]
        - f2: [ [ {}, {} ] ]
        - f3: [[]] - particular case of the f2
                    but with no matches inside
    this functions returns the inner array of matching results
    to be analyzed later by the corresponding section parser
    """

    first_level = results[0]

    if len(first_level) == 0:
        return [{}]

    second_level = first_level[0]

    if type(second_level) is list:
        return second_level

    return first_level

def extract_section(result_lines, section_template):
    parser = ttp(data=result_lines, template=section_template)

    parser.parse()
    results = parser.result()

    return extract_values(results)

def validate_output(current_keys, expected_keys, context):
    for k in expected_keys:
        if k not in current_keys:
            raise Exception(f"{color('PARSING ERROR', 'red')} - Keyword '{k}' not found in {context} section")

def parse_prolog(result_lines):
    values = extract_section(result_lines, PROLOG_TEMPLATE)

    res = values[0]
    res_keys = res.keys()

    validate_output(res_keys, PROLOG_KEYWORDS, 'PROLOG')

    return res

def parse_parent(result_lines):
    values = extract_section(result_lines, PARENT_TEMPLATE)

    filtered_values = list(filter(lambda x: 'random_number' in x, values))

    if len(filtered_values) == 0:
        res = values[0]
    else:
        res = filtered_values[0]

    res_keys = res.keys()

    validate_output(res_keys, PARENT_KEYWORDS, 'PARENT')

    return res

def parse_child(result_lines):
    values = extract_section(result_lines, CHILD_TEMPLATE)

    filtered_values = list(filter(lambda x: 'random_number_recv' in x, values))

    if len(filtered_values) == 0:
        res = values[0]
    else:
        res = filtered_values[0]

    res_keys = res.keys()

    validate_output(res_keys, CHILD_KEYWORDS, 'CHILD')

    return res

def parse_epilog(result_lines):
    values = extract_section(result_lines, EPILOG_TEMPLATE)

    res = values[0]
    res_keys = res.keys()

    validate_output(res_keys, EPILOG_KEYWORDS, 'EPILOG')

    return res

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

def execute_tests(binary_path, run_valgrind = False):
    output, valgrind = exec_command([binary_path], run_valgrind)
    output = sanitize_output(output)

    try:
        results = parse_output(output)
    except Exception as e:
        print(e)
        sys.exit(1)

    print('check pipe fds')
    execute_rules(results, PIPE_FDS_RULES)
    print('check process ids')
    execute_rules(results, PROCESS_IDS_RULES)
    print('check random number values')
    execute_rules(results, NUMBER_VALUES_RULES)

    if run_valgrind:
        print('  VALGRIND OUTPUT:')
        print('\t' + '\t'.join(map(lambda l: l + '\n', valgrind)))

def main(binary_path, run_valgrind):
    print('COMMAND: pingpong')

    execute_tests(binary_path, run_valgrind)

    print()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: pingpong-test.py PINGPONG_BIN_PATH [-v]')
        sys.exit(1)

    binary_path = sys.argv[1]
    run_valgrind = True if len(sys.argv) > 2 and sys.argv[2] == '-v' else False

    main(binary_path, run_valgrind)
