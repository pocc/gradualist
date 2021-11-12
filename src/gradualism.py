"""Generate live documentation given markdown files
Inspired by do-nothing scripts:
https://blog.danslimmon.com/2019/07/15/do-nothing-scripting-the-key-to-gradual-automation/

Take a todo list and turn it into a do-nothing script.
The most recent ## heading will be the title of the script
There must be at least 3 steps

A website like this could be the template:
https://support.cloudflare.com/hc/en-us/articles/201720164-Creating-a-Cloudflare-account-and-adding-a-website
"""
import re
import os
import subprocess as sp
import datetime
import getpass
import sys

from run_code_snippets import run_code_snippet

if len(sys.argv) < 2:
    print("Enter a markdown file to work through (no args detected)")
    sys.exit(1)
if not os.path.exists(sys.argv[1]):
    print(f"Markdown file, {sys.argv[1]}, not found")
    sys.exit(1)
if os.name == 'nt':  # clear screen
    os.system('cls')
else:
    os.system('clear')


def get_dt_now():
    return str(datetime.datetime.now())[:19]


def parse_md():
    with open(sys.argv[1]) as f:
        text = f.read()
    text_lines = list(filter(None, text.split('\n')))
    # {"script name": ["1. instruction", "2. instruction", ...], ...}
    scripts = {}
    current_heading = ""
    current_step = ""
    for line in text_lines:
        heading_match = re.match(r"(#+ .*)", line)
        step_match = re.match(r"(\d+\. .*)", line)
        if heading_match:
            current_heading = heading_match[1]
            current_step = ""
            scripts[current_heading] = []
        elif current_heading and step_match:
            current_step = step_match[1]
            scripts[current_heading].append(current_step)
        # Add to last element in list if in a step
        elif current_step:
            scripts[current_heading][-1] += "\n" + line
    return scripts


def parse_step(step, user_vars, completed_steps, QUIET_FLAG):
    was_task_completed = True

    for v in user_vars:  # Replace future occurences of user vars
        step = step.replace('{' + v + '}', user_vars[v])
    var_matches = re.search('{(.*)}.*?', step)
    describe_matches = re.search(r'\d+\. Describe (.*)', step, re.IGNORECASE)
    shell_command = re.search(r'Run[\s\S]*?`\ ?([^`]+)`', step, re.IGNORECASE)
    code_block = re.search(r'Run[\s\S]*?( *)```(.+)([\s\S]+?)```', step)
    step_number_match = re.match(r"(\d+\.)", step)
    step_num = "1."
    if step_number_match:
        step_num = step_number_match[1]
    if var_matches:
        step = step.replace('{', '').replace('}', '')
        if "personal" in var_matches[1]:
            value = getpass.getpass(f"\n{step} ")
        else:
            value = input(f"\n{step} ")
        user_vars[var_matches[1]] = value
    elif describe_matches:
        print(f"\n{step}        ⏎ ⏎  when done\n")
        lines = []
        while True:  # Add lines until \n\n
            line = input()
            if line:
                lines.append(line)
            else:
                break
        desc = describe_matches[1].replace(' ', '_')
        desc = re.sub(r"[^A-Za-z0-9]*", "", desc)
        user_vars[desc] = '\n'.join(lines)
    elif code_block:
        indent = code_block[1]
        cmd_options_str = code_block[2]
        code = code_block[3]
        code = code.replace('\n' + indent, '\n')  # Remove md indent
        # May well have wrong file extension
        cmd = cmd_options_str.split(' ')
        code_lines = code.count('\n')
        ans = ""
        if not QUIET_FLAG:
            yn = "[enter => yes; n => no]"
            ans = input(f"{step_num} Run {code_lines} lines of {cmd} {yn}? ")
        if QUIET_FLAG or not ans.startswith("n"):
            try:
                output = run_code_snippet(cmd_options_str, code)
                print("Received:", output)
            except Exception as e:
                print("Got exception when trying to run code: ", e)
        elif "optional" not in step.lower():
            was_task_completed = False
    elif shell_command:
        cmd = shell_command[1]
        # replace shell vars if they are env vars
        shell_vars = re.findall(r"\$([a-zA-Z_]+)", step)
        for sv in shell_vars:
            env_sv = os.getenv(sv)
            if env_sv:
                cmd = cmd.replace('$' + sv, env_sv)

        shell = os.getenv("SHELL")
        if not shell:
            shell = "your shell"
        ans = ""
        if not QUIET_FLAG:
            yn = "[enter => yes; n => no]"
            ans = input(f"{step_num} {cmd}\n\n    Run this in {shell} {yn}? ")
        if not ans.startswith("n"):
            try:
                child = sp.run(cmd.split(' '), stdout=sp.PIPE, stderr=sp.PIPE)
                output = child.stdout + child.stderr
                print("Received", output)
            except Exception as e:
                print("Got exception when trying to run code: ", e)
        elif "optional" not in step.lower():
            was_task_completed = False
    elif "optional" in step.lower():
        ans = ""
        if not QUIET_FLAG:
            ans = input(f"""
{step}
    [enter => confirm;  s => skip; b => back 1; n => no] """)
        if not ans.startswith("n"):
            was_task_completed = False
        elif ans.startswith("s"):
            print("Skipping this step...")
    else:
        ans = ""
        if not QUIET_FLAG:
            ans = input(f"""
{step}
    [enter => confirm; b => back 1; n => no] """)
        if not ans.startswith("n"):
            was_task_completed = False
    if was_task_completed:
        completed_steps.append(step + "\n    [✔] " + get_dt_now() + '\n')
    else:
        completed_steps.append(step + "\n    [✘] " + get_dt_now() + '\n')
    return completed_steps


def main():
    hasq = '-q' in sys.argv
    sections = parse_md()
    for section in sections:
        section_str = section + '\n' + '=' * len(section)
        print(section_str)

        user_vars = {}
        done_steps = []
        for step in sections[section]:
            done_steps = parse_step(step, user_vars, done_steps, hasq)
        section_words = section.split(' ', 1)[1]
        sect_date = section_words + get_dt_now()
        frontmatter = "---"
        for key in user_vars:
            if "personal" not in key:
                frontmatter += f"\n{key}: "
                data = user_vars[key]
                if '\n' in data:
                    data = data.replace('\n', '\n  ')
                    frontmatter += '>\n'  # For multiline YAML
                frontmatter += data
        frontmatter += "\n---\n"
        sect_date = sect_date.replace(' ', '_')
        sanitized_section = re.sub(r"[^A-Za-z0-9-_]", "", sect_date)
        if done_steps:  # Don't create files for headings with no steps
            done_steps = [section_str + '\n'] + done_steps
            with open(sanitized_section + ".md", 'w') as f:
                content = frontmatter + '\n'.join(done_steps)
                f.write(content)


main()
