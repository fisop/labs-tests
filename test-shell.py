#! /usr/bin/python3 
import os
import shutil
import tempfile
from subprocess import Popen, PIPE, STDOUT

def compare_strings(current, expected):
    if current != expected:
        print(
        """
        Expected:

        {}

        But got:
        
        {}
        """.format(expected.encode() if expected else None, current.encode() if current else None))
        return False
    return True

def launch_test(name, stdin=b'echo hi', shell_binary='./example-shell/sh', timeout=100, expected_stdout=None, expected_stderr=None, check_stdout=False, check_stderr=False, shell=True):
    """launch_test execute an instance of the shell binary to test (located at _shell_binary_)
    with a given _stdin_ and compares stdout to _expected_stdout_ and stderr to _expected_stderr_.
    If both outputs match, then it returns True indicating a successful test. Otherwise it returns false.
    A _timeout_ can be set to limit the excecution.
    """
    print("\nRunning test: {}".format(name))
    try:
        p = Popen(shell_binary, stdin=PIPE, stdout=PIPE, stderr=STDOUT, shell=shell)
        (stdout, stderr) = p.communicate(input=stdin, timeout=timeout)
        if check_stdout:
            if not compare_strings(stdout.decode() if stdout else None, expected_stdout):
                raise Exception("Check stdout failed")
        if check_stderr:
            if not compare_strings(stderr.decode() if stderr else None, expected_stderr):
                raise Exception("Check stderr failed")
    except Exception as e:
        print("""FAIL test: {}""".format(name))
        print("Excception ocurred: {}".format(e))
        return False
    print("PASS test: {}".format(name))
    return True

shell_binary="./example-shell/sh"
reflector_aux="/home/vagrant/lab-tests/reflector"

def test_simple_echo():
    global shell_binary
    name="Test simple echo command"
    command="echo hi\n"
    expected_stdout="hi\n"
    launch_test(name,
        stdin=command.encode(),
        shell_binary=shell_binary,
        expected_stdout=expected_stdout,
        check_stdout=True
        )

def test_simple_env():
    global shell_binary
    name="Test simple env "
    command="env\nHELLO=4 env\nenv"
    expected_stdout="HELLO=4\n"
    launch_test(name,
        stdin=command.encode(),
        shell_binary="sh -c \"" + shell_binary + " | grep HELLO\"",
        expected_stdout=expected_stdout,
        expected_stderr=None,
        check_stdout=True,
        check_stderr=True
        )

def test_redirect_does_not_create():
    # sleep 100 <in.txt >out.txt
    global shell_binary
    global tempdir
    filename=os.path.join(tempdir, "no-existe.txt")
    name="Test stdin redirect does not create file"
    command="echo <{}\n".format(filename)
    expected_stdout="ls: cannot access '{}': No such file or directory\n".format(filename)
    launch_test(name,
        stdin=command.encode(),
        shell_binary="sh -c \"" + shell_binary + " 2>/dev/null 1>/dev/null; ls {}\"".format(filename),
        expected_stdout=expected_stdout,
        expected_stderr=None,
        check_stdout=True,
        check_stderr=True
        )

def test_redirect_does_not_leak_fds():
    global shell_binary
    global tempdir
    global reflector_aux
    filename=os.path.join(tempdir, "leaks-redirect.txt")
    name="Test redirect does leak fds"
    command="{} {}\n".format(reflector_aux, filename)
    expected_stdout="3 {}\n".format(filename)
    launch_test(name,
        stdin=command.encode(),
        shell_binary="sh -c \"" + shell_binary + " 2>/dev/null 1>/dev/null; wc -l {}\"".format(filename),
        expected_stdout=expected_stdout,
        expected_stderr=None,
        check_stdout=True,
        check_stderr=True
        )

def test_pipes_does_not_leak_fds():
    global shell_binary
    global tempdir
    global reflector_aux
    filename=os.path.join(tempdir, "leaks-pipes.txt")
    name="Test pipes does leak fds"
    command="echo hi | cat - | cat - | {} {}\n".format(reflector_aux, filename)
    expected_stdout="3 {}\n".format(filename)
    launch_test(name,
        stdin=command.encode(),
        shell_binary="sh -c \"" + shell_binary + " 2>/dev/null 1>/dev/null; wc -l {}\"".format(filename),
        expected_stdout=expected_stdout,
        expected_stderr=None,
        check_stdout=True,
        check_stderr=True
        )

def test_cd():
    global shell_binary
    global reflector_aux
    filename=os.path.join(tempdir, "leaks-pipes.txt")
    name="Test pipes does leak fds"
    command="cd /home\n/bin/pwd\ncd /proc\n/bin/pwd\ncd sys\n/bin/pwd\ncd kernel\n/bin/pwd\ncd ..\n/bin/pwd\ncd\n/bin/pwd\n".format(reflector_aux, filename)
    expected_stdout="/home\n/proc\n/proc/sys\n/proc/sys/kernel\n/proc/sys\n/home\n"
    launch_test(name,
        stdin=command.encode(),
        shell_binary="HOME=/home sh -c \"" + shell_binary + "\"",
        expected_stdout=expected_stdout,
        expected_stderr=None,
        check_stdout=True,
        check_stderr=True
        )

tempdir=tempfile.mkdtemp(suffix='-shell-test')
print("Test results will be stored in {}".format(tempdir))

test_simple_echo()
test_simple_env()
test_redirect_does_not_create()
test_redirect_does_not_leak_fds()
test_pipes_does_not_leak_fds()
test_cd()

shutil.rmtree(tempdir)
