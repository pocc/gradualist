"""Run arbitrary code across multiple languages.

No extension required: $command $file
    python, perl, php, ruby, bash, lua, julia, lisp
"""
import shlex
import subprocess as sp
import re
import tempfile
import os
from typing import List

# Command line flags to run a temp file.
# Many languages require their file extension
# Feel free to add your favorite language here
COMPILED_FILE = "temp"
compile_options = {
    "c": ["gcc temp.c -o temp", COMPILED_FILE],
    "cpp": ["g++ temp.cpp -o temp", COMPILED_FILE],
    "go": ["go build temp.go", COMPILED_FILE],
    "java": ["javac temp.java", "java " + COMPILED_FILE],
    "rust": ["rustc temp.rs", COMPILED_FILE],
    "javascript": ["node temp"]
}


def run_code_block(cmd_options_str: str, code: str) -> str:
    try:
        output_bytes = run_code_snippet(cmd_options_str, code)
        output = str(output_bytes, encoding='utf8')
    except Exception as e:
        output = str(e)
    print(f"\n\nReceived: `{output}`", flush=True)
    return output


def run_cmd(compile_args: List[str]) -> bytes:
    """Run a command and close the temp file."""
    child = sp.run(compile_args, stdout=sp.PIPE, stderr=sp.PIPE)
    return child.stdout + child.stderr


def run_code_snippet(args_str: str, script: str):
    """run code given command line options

    Special options in the options string:
        {example.py}: Use this file name in the command
        {}: Replace {} in the command with a temp file
    """
    tempf_path = os.path.join(tempfile.gettempdir(), 'temp')
    tempf = open(tempf_path, 'w')
    if "{}" in args_str:  # User wants to use a temp file
        args_str.replace("{}", tempf.name)
    compile_args = shlex.split(args_str)

    # If we're given only language hint, assume that $language $file will work
    lang = compile_args[0]
    compile_step = lang in compile_options and len(compile_options[lang]) == 2

    if len(compile_args) == 1:
        if compile_step:
            args_str = compile_options[lang][0]
            temp_file = re.search(r'(temp\.\w+)', args_str)
            if temp_file:
                with open(temp_file[1], 'w') as f:
                    f.write(script)
            args = shlex.split(args_str)
            # Compile code as first step
            child = sp.run(args, stdout=sp.PIPE, stderr=sp.PIPE)
            if child.returncode != 0:
                output = (child.stdout + child.stderr).decode()
                print("Problem compiling code", output)
            # Next set of args for 2nd command
            cmd_str = compile_options[lang][1]
            executable_path = os.path.join(os.getcwd(), COMPILED_FILE)
            os.chmod(executable_path, 0o774)  # chmod a+x
            # Issues with java bc java temp works, but not if temp is
            # referred to by its absolute filepath; `java temp.class` fails
            if ' ' in cmd_str:
                args = shlex.split(cmd_str)
            else:
                args = [executable_path]
            output = run_cmd(args)
            tempf.close()
            return output
        else:
            tempf.write(script)
            tempf.seek(0)
            compile_args += [tempf.name]  # Run this language against temp file
            if lang in compile_options:
                compile_str = compile_options[lang][0]
                compile_str = compile_str.replace('temp', tempf.name)
                compile_args = shlex.split(compile_str)
            tempf.close()
            return run_cmd(compile_args)
    else:
        files = re.findall(r"{(.*)}", args_str)
        dstfile = ""
        if len(files) > 1:
            print("Error: Only one named file can be saved to", files[1:])
        elif len(files) > 0:
            dstfile = files[0]
            with open(dstfile, 'w') as f:
                f.write(script)
            args_str = args_str.replace('{' + dstfile + '}', dstfile)
        cmd = shlex.split(args_str)
        output = run_cmd(cmd)
        tempf.close()
        if dstfile:
            os.remove(dstfile)
        return output
