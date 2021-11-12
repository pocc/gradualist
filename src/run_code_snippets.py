"""Run arbitrary code across multiple languages.

No extension required: $command $file
    python, perl, php, ruby, bash, lua, julia, lisp
"""
import subprocess as sp
import re
import tempfile
import os

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


def run_cmd(compile_args, tempf):
    """Run a command and close the temp file."""
    child = sp.run(compile_args, stdout=sp.PIPE, stderr=sp.PIPE)
    tempf.close()
    return child.stdout + child.stderr


def run_code_snippet(args_str: str, script: str):
    """run code given command line options

    Special options in the options string:
        {example.py}: Use this file name in the command
        {}: Replace {} in the command with a temp file
    """
    tempf = tempfile.NamedTemporaryFile()
    if "{}" in args_str:  # User wants to use a temp file
        args_str.replace("{}", tempf.name)
    compile_args = args_str.split(' ')

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
            args = args_str.split(' ')
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
                args = cmd_str.split(' ')
            else:
                args = [executable_path]
            output = run_cmd(args, tempf)
            return output
        else:
            tempf.write(bytes(script, encoding='utf8'))
            tempf.seek(0)
            compile_args += [tempf.name]  # Run this language against temp file
            if lang in compile_options:
                compile_str = compile_options[lang][0]
                compile_str = compile_str.replace('temp', tempf.name)
                compile_args = compile_str.split(' ')
            return run_cmd(compile_args, tempf)
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
        cmd = args_str.split(' ')
        output = run_cmd(cmd, tempf)
        if dstfile:
            os.remove(dstfile)
        return output
