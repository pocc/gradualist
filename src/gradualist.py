"""Gradualist

Generate live documentation given markdown files
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
import datetime
import sys
from typing import Dict, List, Tuple
import glob
from pathlib import Path
from logic.loop import while_loop

from parsers import parse_md
from steps.get_line import get_text_line
from steps.get_paragraph import get_text_paragraph
from steps.run_code_blocks import run_code_block
from steps.run_shell_cmd import run_shell_cmd
from steps.verify_done import launch_interrupt
from utils import prettify_date_diff, getchar, get_dt_now

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


def check_longform(user_vars: Dict[str, str], step: str):
    """Check if this requires a multiline response. If so, call it"""
    describe_matches = re.search(r'\d+\. (?:Describe (.*))', step, re.IGNORECASE)
    if describe_matches:
        topic = describe_matches[1]
        new_kv = get_text_paragraph(topic)
        for k in new_kv:
            user_vars[k] = new_kv[k]
    return describe_matches is not None


def check_oneline(user_vars: Dict[str, str], step: str):
    """Check if this requires a one line response. If so, call it."""
    var_matches = re.findall(r'.*(?:\${(.*)}|((?:the|a|an|this|your|to|for) [^{}]*?)[:?])', step)
    if var_matches:
        # Ask the to define their variable for the first time
        # Times after this will be static y/n questions
        var_name = list(filter(None, var_matches[0]))[0]
        new_kv = get_text_line(step, var_name)
        for k in new_kv:
            user_vars[k] = new_kv[k]
    return len(var_matches) > 0


def check_code_block(step: str, CONFIRM_FLAG: bool, paragraphs: List[str]) -> bool:
    code_block = re.search(r'Run[\s\S]*?( *)```(.+)([\s\S]+?)```', step)
    if code_block:
        indent = code_block[1]
        cmd_options_str = code_block[2]
        indented_code = code_block[3]
        code = indented_code.replace('\n' + indent, '\n')  # Remove md indent

        if CONFIRM_FLAG:
            resp = input(f"Run `{cmd_options_str}` against `{code}`? [y/n]")
            if resp != 'y':
                return False
        output = run_code_block(cmd_options_str, code)
        paragraphs += [cmd_options_str, code, output]
        return True
    return False


def check_shell_cmd(step: str, CONFIRM_FLAG: bool, paragraphs: List[str]) -> bool:
    shell_command = re.search(r'Run[\s\S]*?`\ ?([^`]+)`', step, re.IGNORECASE)
    if shell_command:
        cmd = shell_command[1]
        if CONFIRM_FLAG:
            resp = input(f"Run `{cmd}`? [y/n]")
            if resp != 'y':
                return False
        output = run_shell_cmd(cmd)
        paragraphs += [cmd, output]
        return True
    return False


def check_loop(step: str, paragraphs: List[str]) -> str:
    loop_matches = re.search(r'^\s*(\d+\. [Ww]hile .*?)[,\n]\s*([^,\n]*)(?:[\n,]\s*logging (.+))?', step)
    if loop_matches:
        condition = loop_matches[1]
        task = loop_matches[2]
        logvars = loop_matches[3]
        loop_resp, status_char = while_loop(condition, task, logvars)
        paragraphs += [loop_resp]
        return status_char
    return ''


def parse_step_delegate(step: str, user_vars: Dict[str, str], CONFIRM_FLAG: bool, paragraphs: List[str]):
    if check_longform(user_vars, step):
        return 'w'  # Words
    if check_code_block(step, CONFIRM_FLAG, paragraphs):
        return 'w'
    if check_shell_cmd(step, CONFIRM_FLAG, paragraphs):
        return 'w'
    if check_oneline(user_vars, step):
        return 'w'
    status_char = check_loop(step, paragraphs)
    return status_char


def parse_step(step: str, user_vars: Dict[str, str], completed_steps: List[str], CONFIRM_FLAG: bool) -> Tuple[List[str], bool]:
    time_start = datetime.datetime.now()
    paragraphs: List[str] = []
    for v in user_vars:  # Replace future occurences of user vars, both explicit and implicit
        step = step.replace('${' + v + '}', user_vars[v])
        step = step.replace(v, user_vars[v])

    start_text = f"    {get_dt_now()[11:]}      Started "
    # Add a 2nd newline after the step line for readability
    step = re.sub(r"^([^\n]*\n) ", r"\1\n ", step)
    print(step + ' ', end='', flush=True)
    status_char = parse_step_delegate(step, user_vars, CONFIRM_FLAG, paragraphs)

    if status_char:
        print(start_text, flush=True)
    else:
        # Default. yes/no toggle of whether it's done or not
        print('\n' + start_text, flush=True)
        log_lines, status_char = launch_interrupt()
        paragraphs = log_lines

    step_status = get_step_status(time_start, status_char, step)
    print(step_status, flush=True)
    completed_steps.append(step + '\n' + step_status + "\n\n".join(paragraphs))
    return completed_steps, status_char == 'b'


def get_step_status(time_start: datetime.datetime, status_char: str, step: str) -> str:
    prev_step = -1
    prev_step_mat = re.search(r"(\d+)", step)
    if prev_step_mat:
        prev_step = int(prev_step_mat[1]) - 1
    time_taken_full = str((datetime.datetime.now() - time_start))
    time_taken = prettify_date_diff(time_taken_full)
    if status_char in ['\r', '\n', 'w']:
        step_status = f"    {get_dt_now()[11:]}  ✅  Done"
    elif status_char == 's':
        step_status = f"    {get_dt_now()[11:]}  ❌  Skipped"
    elif status_char == 'b':
        step_status = f"    {get_dt_now()[11:]}  ⬆️   Return to {prev_step}."
    else:
        step_status = "    ??? Unknown status. Please create an issue " + get_dt_now()
    step_status += f"\n     {time_taken}\n"
    return step_status


def main():
    markdown_files = sys.argv[1:]
    sections = parse_md(markdown_files)
    print("do[\\n]e ✅\t[s]kip ❌\t[b]ack ⬆️ \t[l]og 💡\t[t]angent ✨\n[h]elp   ❔\t[q]uit 🚪\n")

    hasq = '-q' in sys.argv
    heading_time_start = datetime.datetime.now()
    text_to_write = ""
    top_heading = True
    user_vars: Dict[str, str] = {}
    for section in sections:
        section_str = section + '\n' + '=' * len(section)
        print(section_str, end='')
        if top_heading:
            print(f"\n  ⏳ {get_dt_now()}\n")
            top_heading = False
        else:
            print("\n")

        done_steps: List[str] = []
        i = 0
        step_num = 0
        while i < len(sections[section]):
            step = sections[section][i]
            step_num_mat = re.search(r"(\d+)", step)
            if step_num_mat:
                new_step_num = int(step_num_mat[1])
                if new_step_num >= step_num:
                    step_num = new_step_num
                else:  # Step numbers should not be decreasing
                    break
            done_steps, back = parse_step(step, user_vars, done_steps, hasq)
            if back:
                # All numbers up to this poit have been increasing
                # So resetting it to 0 won't cause a section skip
                step_num = 0
                done_steps.pop()
                if i > 0:
                    done_steps.pop()
                    i -= 1
            else:
                i += 1
        if done_steps:  # Don't create files for headings with no steps
            done_steps = ['\n' + section + '\n'] + done_steps
            text_to_write += '\n'.join(done_steps)
    heading_time_end = datetime.datetime.now()
    time_spent_full = str(heading_time_end - heading_time_start)
    time_spent = prettify_date_diff(time_spent_full)
    print(f"  ⏳ {get_dt_now()}")
    offset = ' ' * (13 - len(time_spent))
    print(f"     Total:{offset}{time_spent}")
    frontmatter = "---"
    for key in user_vars:
        if "personal" not in key:
            frontmatter += f"\n{key}: "
            data = user_vars[key]
            if '\n' in data:
                data = data.replace('\n', '\n  ')
                frontmatter += f'>\n  {data}'  # For multiline YAML
            else:
                frontmatter += f"\"{data}\""
    frontmatter += "\n---\n"
    text_to_write = frontmatter + text_to_write

    home = str(Path.home())
    log_dir = os.path.join(home, 'log')
    if not os.path.exists('log'):
        os.makedirs(log_dir, exist_ok=True)
    output_file = get_dt_now()[:10] + ".md"
    output_path = os.path.join(log_dir, output_file)
    print("\n\n[Enter] to save output 💾 | [q] to quit 🚪")
    ch = getchar()  # will quit on q
    if ch == 'q':
        print("Quitting...")
        sys.exit(1)
    with open(output_path, 'a') as f:
        f.write(text_to_write)
    print("💾 ", output_path)


def cleanup():  # Remove detritus, esp on ^C
    for f in glob.glob("temp*"):
        os.remove(f)


try:
    main()
finally:
    cleanup()
