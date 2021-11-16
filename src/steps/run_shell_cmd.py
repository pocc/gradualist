"""Run a single line shell command.
Triggered with $`shell commands in here`
"""
import os
import re
import subprocess as sp
import shlex


def run_shell_cmd(cmd: str) -> str:
    # replace shell vars if they are env vars
    shell_vars = re.findall(r"\$([a-zA-Z_]+)", cmd)
    for sv in shell_vars:
        env_sv = os.getenv(sv)
        if env_sv:
            cmd = cmd.replace('$' + sv, env_sv)

    try:
        child = sp.run(shlex.split(cmd), stdout=sp.PIPE, stderr=sp.PIPE)
        output_bytes = child.stdout + child.stderr
        output = str(output_bytes, 'utf8')
    except Exception as e:
        output = str(e)
    print(f"\n\nReceived: `{output}`", flush=True)
    return output
