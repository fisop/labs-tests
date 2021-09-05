#! /usr/bin/python3 
import os
import shutil
import sys
import tempfile
from subprocess import Popen, PIPE, STDOUT
from termcolor import cprint

def multiline(cmds):
    return '\n'.join([cmd.strip() for cmd in cmds]) + '\n'

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

def test_simple_echo(shell_binary: str):
    name="Test simple echo command"
    stdin="echo hi\n"
    expected_stdout="hi\n"
    launch_test(name,
        stdin=stdin.encode(),
        shell_binary=shell_binary,
        expected_stdout=expected_stdout,
        check_stdout=True
        )

def test_simple_env(shell_binary: str):
    name="Test simple env "
    stdin=multiline("""env
                    HELLO=4 env
                    env""".splitlines())
    expected_stdout="HELLO=4\n"
    command="sh -c \"{}\"".format(shell_binary + " | grep HELLO")
    launch_test(name,
        stdin=stdin.encode(),
        shell_binary=command,
        expected_stdout=expected_stdout,
        expected_stderr=None,
        check_stdout=True,
        check_stderr=True
        )

def test_redirect_does_not_create(shell_binary: str):
    # sleep 100 <in.txt >out.txt
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

def test_redirect_does_not_leak_fds(shell_binary: str):
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

def test_pipes_does_not_leak_fds(shell_binary: str):
    global tempdir
    global reflector_aux
    filename=os.path.join(tempdir, "leaks-pipes.txt")
    name="Test pipes does leak fds"
    stdin=multiline("echo hi | cat - | cat - | {} {}".format(reflector_aux, filename).splitlines())
    expected_stdout=multiline("3 {}".format(filename).splitlines())
    command="HOME=/home sh -c \"{}\"".format(
            shell_binary + " 2>/dev/null 1>/dev/null; wc -l {}".format(filename))
    launch_test(name,
        stdin=stdin.encode(),
        shell_binary=command,
        expected_stdout=expected_stdout,
        expected_stderr=None,
        check_stdout=True,
        check_stderr=True
        )

def test_cd(shell_binary: str):
    global reflector_aux
    filename=os.path.join(tempdir, "leaks-pipes.txt")
    name="Test pipes does leak fds"
    stdin=multiline(["cd /home",
            "/bin/pwd",
            "cd /proc",
            "/bin/pwd",
            "cd sys",
            "/bin/pwd",
            "cd kernel",
            "/bin/pwd",
            "cd ..",
            "/bin/pwd",
            "cd",
            "/bin/pwd"])
    expected_stdout=multiline("""/home
                              /proc
                              /proc/sys
                              /proc/sys/kernel
                              /proc/sys
                              /home""".splitlines())

    command="HOME=/home sh -c \"{}\"".format(
            shell_binary)

    launch_test(name,
        stdin=stdin.encode(),
        shell_binary=command,
        expected_stdout=expected_stdout,
        expected_stderr=None,
        check_stdout=True,
        check_stderr=True
        )


def run_tests(shell_binary):
    global tempdir
    global reflector_aux
    tests = [
            test_simple_echo,
            test_simple_env,
            test_redirect_does_not_create,
            test_redirect_does_not_leak_fds,
            test_pipes_does_not_leak_fds,
            test_cd
            ]
    reflector_aux="/home/vagrant/lab-tests/reflector"
    tempdir=tempfile.mkdtemp(suffix='-shell-test')
    print("Test results will be stored in {}".format(tempdir))

    count = 1
    failed = 0
    total = len(tests)
    for test in tests:
        try:
            test(shell_binary)
            cprint("PASS {}/{}: {}".format(count, total, test.__name__), "green")
        except Exception as e:
            cprint("FAIL {}/{}: {}. Exception ocurred: {}".format(count, total, test.__name__, e), "red")
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
    run_tests(shell_binary)
