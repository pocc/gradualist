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
    last_heading = ""
    for line in text_lines:
        heading_match = re.match(r"(#+ .*)", line)
        step_match = re.match(r"(\d+\. .*)", line)
        if heading_match:
            last_heading = heading_match[1]
            scripts[last_heading] = []
        elif last_heading and step_match:
            scripts[last_heading].append(step_match[1])
        else:  # Add to last element in list
            scripts[last_heading][-1] += "\n" + line
    return scripts


def parse_step(step, user_vars, completed_steps):
    was_task_completed = True

    for v in user_vars:  # Replace future occurences of user vars
        step = step.replace('{' + v + '}', user_vars[v])
    var_matches = re.search('{(.*)}.*?', step)
    shell_command = re.search(r'`\$ ?([^`]+)`', step)
    code_block = re.search(r'```(\w+)([\s\S]+?)```', step)
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
    elif code_block:
        language, code = code_block[1], code_block[2]
        code_lines = code.count('\n')
        ans = input(f"{step_num} Run {code_lines} lines of {language} [y/n]? ")
        if ans.startswith("y"):
            cmd = [language, "donothing_code"]
            try:
                with open("donothing_code", 'w') as f:
                    f.write(code)
                child = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
                output = (child.stdout + child.stderr).decode()
                tabbed_output = output.replace('\n', '\n    ')
                print(f"    Received\n    `{tabbed_output}`")
                os.remove("donothing_code")
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
        ans = input(f"{step_num} {cmd}\n\n    Run this in {shell} [y/n]? ")
        if ans.startswith("y"):
            try:
                child = sp.run(cmd.split(' '), stdout=sp.PIPE, stderr=sp.PIPE)
                output = (child.stdout + child.stderr).decode()
                tabbed_output = output.replace('\n', '\n    ')
                print(f"    Received\n    `{tabbed_output}`")
            except Exception as e:
                print("Got exception when trying to run code: ", e)
        elif "optional" not in step.lower():
            was_task_completed = False
    elif "optional" in step.lower():
        ans = input(f"""
{step}
    ENTER => continue  |  s => skip  |  b => go back 1 """)
        if not ans.startswith("y"):
            was_task_completed = False
        elif ans.startswith("s"):
            print("Skipping this step...")
    else:
        ans = input(f"""
{step}
    ENTER => continue  |  b => go back 1 """)
        if not ans.startswith("y"):
            was_task_completed = False
    if was_task_completed:
        completed_steps.append(step + "\n    [✔] " + get_dt_now() + '\n')
    else:
        completed_steps.append(step + "\n    [✘] " + get_dt_now() + '\n')
    return completed_steps


def main():
    sections = parse_md()
    for section in sections:
        section_str = section + '\n' + '=' * len(section)
        print(section_str)

        user_vars = {}
        completed_steps = []
        for step in sections[section]:
            completed_steps += parse_step(step, user_vars, completed_steps)
        section_words = section.split(' ', 1)[1]
        sect_date = section_words + get_dt_now()
        frontmatter = "---"
        for key in user_vars:
            if "personal" not in key:
                frontmatter += f"\n{key}: {user_vars[key]}"
        frontmatter += "\n---\n"
        sect_date = sect_date.replace(' ', '_')
        sanitized_section = re.sub(r"[^A-Za-z0-9-_]", "", sect_date)
        completed_steps = [section_str + '\n'] + completed_steps
        with open(sanitized_section + ".md", 'w') as f:
            content = frontmatter + '\n'.join(completed_steps)
            f.write(content)


main()
