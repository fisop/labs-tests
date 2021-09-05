#! /usr/bin/python3 
import os
import shutil
import sys
import tempfile
import yaml
from yaml.loader import SafeLoader
from subprocess import Popen, PIPE, STDOUT
from termcolor import cprint

def compare_strings(current, expected):
    if current != expected:
        message="""
        Expected:

        {}

        But got:
        
        {}
        """.format(expected.encode() if expected else None, current.encode() if current else None)
        return message
    return None

def launch_test(name, stdin=b'echo hi', shell_binary='./example-shell/sh', timeout=100, expected_stdout=None, expected_stderr=None, check_stdout=False, check_stderr=False, shell=True):
    """launch_test execute an instance of the shell binary to test (located at _shell_binary_)
    with a given _stdin_ and compares stdout to _expected_stdout_ and stderr to _expected_stderr_.
    If both outputs match, then it returns True indicating a successful test. Otherwise it returns false.
    A _timeout_ can be set to limit the excecution.
    """
    p = Popen(shell_binary, stdin=PIPE, stdout=PIPE, stderr=STDOUT, shell=shell)
    (stdout, stderr) = p.communicate(input=stdin, timeout=timeout)
    if check_stdout:
        msg = compare_strings(stdout.decode() if stdout else None, expected_stdout)
        if msg:
            raise Exception("Check stdout failed: {}".format(msg))
    if check_stderr:
        msg = compare_strings(stderr.decode() if stderr else None, expected_stderr)
        if msg:
            raise Exception("Check stderr failed: {}".format(msg))

def substitude_vars(target: str, subs):
    if not target:
        return target

    for subs_from, subs_to in subs:
        target = target.replace(subs_from, subs_to)
    return target

class ShellTest():
    def __init__(self, filepath: str, sub_map):
        data = ""
        with open(filepath) as f:
            data = yaml.load(f, Loader=SafeLoader)
        self.name = data['name']
        self.description = data['description']
        self.command = data['command']
        self.command = substitude_vars(self.command, sub_map)
        self.stdin = data['stdin'] if 'stdin' in data else None
        self.stdin = substitude_vars(self.stdin, sub_map)
        self.expected_stdout = data['expected_stdout'] if 'expected_stdout' in data else None
        self.expected_stdout = substitude_vars(self.expected_stdout, sub_map)
        self.expected_stderr = data['expected_stderr'] if 'expected_stderr' in data else None
        self.expected_stderr = substitude_vars(self.expected_stderr, sub_map)

    def run(self):
        launch_test(self.name,
            stdin=self.stdin.encode(),
            shell_binary=self.command,
            expected_stdout=self.expected_stdout,
            expected_stderr=self.expected_stderr,
            check_stdout=True,
            check_stderr=True
            )

def custom_test(subs_map, filepath: str):
    sh = ShellTest(filepath, subs_map)
    sh.run()
    return

def run_custom_test(shell_binary: str):
    global tempdir
    global reflector_aux
    reflector_aux="/home/vagrant/lab-tests/reflector"
    tempdir=tempfile.mkdtemp(suffix='-shell-test')
    print("Test results will be stored in {}".format(tempdir))

    subs_map = [('{shell_binary}', shell_binary),
            ('{tempdir}', tempdir),
            ('{reflector}', reflector_aux),
            ]
    
    tests = ['simple_echo',
            'simple_env',
            'redirect_does_not_create',
            'redirect_does_not_leak_fds',
            'pipes_does_not_leak_fds',
            'cd_basic',
            'cd_home',
            'cd_back',
            'redirect_stdin',
            ]

    count = 1
    failed = 0
    total = len(tests)
    for test in tests:
        try:
            custom_test(subs_map, "./tests/{}.yaml".format(test))
            cprint("PASS {}/{}: {}".format(count, total, test), "green")
        except Exception as e:
            cprint("FAIL {}/{}: {}. Exception ocurred: {}".format(count, total, test, e), "red")
            failed += 1
        finally:
            count += 1

    cprint("{} out of {} tests passed".format(total - failed, total), "yellow" if failed else "green")

    shutil.rmtree(tempdir)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("{}: {} <test-shell-binary>".format(sys.argv[0], sys.argv[0]))
        exit()
    shell_binary=sys.argv[1]
    print(shell_binary)
    run_custom_test(shell_binary)
