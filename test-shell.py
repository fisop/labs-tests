#! /usr/bin/python3 
from subprocess import Popen, PIPE, STDOUT

try:
    print("Running test shell")
    p = Popen('./sh', stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    print("Popen succeeded")
    (stdout, stderr) = p.communicate(input=b'echo hi', timeout=10)
    print(stdout)
    print(stderr)
except Exception as e:
    print("Excception ocurred")
    print(e)


