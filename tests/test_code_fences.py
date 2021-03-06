# Run the tests
import subprocess as sp

expected_resp = rb"""
# Tests
=======
## Test Keywords
================
Received b'Hello World!\n'
## Test Code Snippets
=====================
Received: b'Hello World!\n'
Received: b'Hello World!\n'
Received: b'Hello World!\n'
Received: b'Hello World!\n'
Received: b'Hello World!\n'
Received: b'\nHello World!'
Received: b'Hello World!\n'
Received: b'Hello World!\n'
Got exception when trying to run code:  [Errno 13] Permission denied: 'node'
Received: b'Hello World!\n'
Received: b'Hello, World!\n'
Received: b'Hello World!\n'
Got exception when trying to run code:  [Errno 2] No such file or directory: 'julia'
Received: b'Hello, World!\n'
Got exception when trying to run code:  [Errno 2] No such file or directory: 'groovy'
"""


child = sp.run("python3 src/gradualist.py tests/code_fences.md".split(' '), stdout=sp.PIPE, stderr=sp.PIPE)
actual_resp = (child.stdout + child.stderr)
actual_resp = b'\n#' + actual_resp.split(b'#', 1)[1]
if expected_resp != actual_resp:
    print("Expected:\n`", expected_resp, "`\nActual:\n`", actual_resp, "`", sep='')
else:
    print("Keywords test passed")
