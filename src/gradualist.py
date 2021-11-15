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
import tty
import termios
import glob
from pathlib import Path

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


COMMAND_KEYS = ["\n", "\r", "s", "b", "q"]


def get_dt_now():
    return str(datetime.datetime.now())[:19]


def prettify_date_diff(date_str):
    """replace 0 in date diff with ' ', strip mantissa"""
    time_taken = date_str.split('.')[0]
    time_taken_mat = re.match(r"^[0:]+", time_taken)
    if time_taken_mat:
        zeros = time_taken_mat[0]
        time_taken = time_taken.replace(zeros, len(zeros) * " ")
        if time_taken[-1] == " ":
            time_taken = time_taken[:-1] + "0"
    return time_taken


def parse_md():
    text = ""
    for source_md in sys.argv[1:]:
        source_path = os.path.abspath(source_md)
        if os.path.exists(source_path):
            print(source_path, end='\n\n')
            with open(source_md) as f:
                text += f.read()
        else:
            print("File not found", source_path)
    text = re.sub(r"\* \[.\]", "1.", text)  # Remove checkboxes
    text_lines = list(filter(None, text.split('\n')))
    # {"script name": ["1. instruction", "2. instruction", ...], ...}
    scripts = {}
    current_heading = ""
    current_step = ""
    sublist_path = ""
    for line in text_lines:
        heading_match = re.match(r"(#+ .*)", line)
        step_match = re.match(r"(\d+\.)( .*)", line)
        substep_regex = r"(\s+)(\d+\.)( .*)"
        substep_match = re.match(substep_regex, line)
        if heading_match:
            current_heading = heading_match[1]
            current_step = ""
            scripts[current_heading] = []
        elif current_heading and step_match:  # First step, 1.
            current_step = step_match[1] + step_match[2]
            sublist_path = step_match[1]
            scripts[current_heading].append(current_step)
        elif substep_match:
            indents = substep_match[1]
            indent_level = indents.replace('\t', '    ').count('    ')
            # step 1. under a step 1. becomes 1.1., which is the sublist_path
            altered_path_list = sublist_path.split('.')[:indent_level]
            altered_path_list += [substep_match[2]]
            sublist_path = '.'.join(altered_path_list)
            sublist_total = sublist_path + substep_match[3]
            scripts[current_heading].append(sublist_total)
        # Add to last element in list if in a step
        elif current_step:
            scripts[current_heading][-1] += "\n" + line

    return scripts


# https://gist.github.com/jasonrdsouza/1901709
def getchar():
    # Returns a single character from standard input
    ch = ''
    if os.name == 'nt':  # how it works on windows
        import msvcrt
        ch = msvcrt.getch()
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    if ord(ch) == 3 or ord(ch) == 4:
        print(f'^{chr(ord(ch)+64)}')
        quit()  # handle ctrl+C or ctrl+D
    if ch.lower() == 'q':
        print("Exiting...")
        quit()
    return ch


def get_multiline_input():
    """Get multiple lines. Quits on "\n\n" """
    lines = []
    while True:  # Add lines until \n\n
        print("        ", end='')
        line = input()
        if line:
            lines.append(line)
        else:
            break
    return '\n'.join(lines)


def parse_step(step, user_vars, completed_steps, QUIET_FLAG):
    was_task_completed = False
    back_one_step = False
    skipping = False
    paragraphs = []
    step_num = "1."
    time_start = datetime.datetime.now()

    for v in user_vars:  # Replace future occurences of user vars
        step = step.replace('{' + v + '}', user_vars[v])

    var_matches = re.search('{(.*)}.*?', step)
    question_regex = r'\d+\. ((who|what|when|where|why|how|which) .*)\?'
    question_word_matches = re.search(question_regex, step, re.IGNORECASE)
    describe_matches = re.search(r'\d+\. Describe (.*)', step, re.IGNORECASE)
    shell_command = re.search(r'Run[\s\S]*?`\ ?([^`]+)`', step, re.IGNORECASE)
    code_block = re.search(r'Run[\s\S]*?( *)```(.+)([\s\S]+?)```', step)
    loop_matches = re.search(r'^\s*(\d+\. [Ww]hile .*)[,\n]\s*(.*)(?:[\n,]\s*log(?:ging)? \[(.*)\])?', step)

    step_number_match = re.match(r"(\d+\.)", step)
    if step_number_match:
        step_num = step_number_match[1]
    # If someone asks a question, they expect an answer
    if question_word_matches and not describe_matches:
        describe_matches = question_word_matches
    if var_matches:
        step = step.replace('{', '').replace('}', '')
        if "personal" in var_matches[1]:
            value = getpass.getpass(f"\n{step} ")
        else:
            value = input(f"\n{step} ")
        var_name = var_matches[1].replace(' ', '_').lower()
        var_name = re.sub(r"[^A-Za-z0-9_]*", "", var_name)
        user_vars[var_name] = value
        was_task_completed = True
    elif describe_matches:
        start = get_dt_now()[11:]
        step_text = f"""{step}        When done hit enter on a newline\n"""
        print(step_text)
        multiline_input = get_multiline_input()
        print(f"\n    {start}      Started")
        desc = describe_matches[1].replace(' ', '_').lower()
        desc = re.sub(r"[^A-Za-z0-9_]*", "", desc)
        user_vars[desc] = multiline_input
        was_task_completed = True
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
            yn = "                    Enter ✅ | [b]ack ⬆️  | [s]kip ❌ "
            print(f"{step_num} Run {code_lines} lines of {cmd} {yn} ")
            ans = getchar()
        if ans == 's':
            skipping = True
        elif ans == "b" or ord(ans) == 127:
            back_one_step = True
        if ans in ['\n', '\r'] or QUIET_FLAG:
            was_task_completed = True
            try:
                output = run_code_snippet(cmd_options_str, code)
                print("Received:", output)
            except Exception as e:
                print("Got exception when trying to run code: ", e)
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
            yn = "                    Enter ✅ | [b]ack ⬆️  | [s]kip ❌ "
            print(f"{step_num} {cmd}\n\n    Run this in {shell} {yn} ")
            ans = getchar()
        if ans == 's':
            skipping = True
        elif ans == "b" or ord(ans) == 127:
            back_one_step = True
        if ans in ['\n', '\r'] or QUIET_FLAG:
            was_task_completed = True
            try:
                child = sp.run(cmd.split(' '), stdout=sp.PIPE, stderr=sp.PIPE)
                output = child.stdout + child.stderr
                print("Received", output)
            except Exception as e:
                print("Got exception when trying to run code: ", e)
    elif loop_matches:
        start = get_dt_now()[11:]
        condition = loop_matches[1]
        task = loop_matches[2]
        resp = ""
        log_data_keys = []
        print(f"{condition}\n    When done hit enter on a newline", end='')
        if loop_matches[3]:
            print(f" and on keys [{loop_matches[3]}]\n")
            log_data_keys = [i.strip() for i in loop_matches[3].split(',')]
        else:
            print("\n")
        loop_resp = "Initial String"
        loop_num = 1
        while loop_resp:
            print(f"    ↪️  {loop_num}. {task}")
            loop_resp = ""
            for key in log_data_keys:
                loop_resp = input(f"        {key}: ")
            if not log_data_keys:
                loop_resp = input(f"        ")
            resp += loop_resp + '\n'
            loop_num += 1
        paragraphs.append(resp)
        print(f"\n    {start}      Started")
        was_task_completed = True
    else:
        ans = ""
        if not QUIET_FLAG:
            step_text = f"""{step}\n    {get_dt_now()[11:]}      Started"""
            print(step_text)
            while ans not in COMMAND_KEYS:
                ans = getchar()
                if ans == 'h':
                    print("Help is on the way...")
                if ans == 'l':
                    paragraphs.append("* [ ] " + input(f"    {get_dt_now()[11:]}      Log a thought\n        "))
                    print(f"""    {get_dt_now()[11:]}      Continuing""")
                if ans == 't':
                    new_tangent = "* [ ] " + input(f"    {get_dt_now()[11:]}      What's distracting?\n        ") + "\n"
                    home = str(Path.home())
                    tangent_file = os.path.join(home, 'log', 'tangent.md')
                    with open(tangent_file, 'a') as f:
                        f.write(new_tangent)
                    print("        >>", tangent_file)
                    print(f"""    {get_dt_now()[11:]}      Continuing""")
        if ans in ['\n', '\r']:
            was_task_completed = True
        elif ans == "b" or ord(ans) == 127:
            back_one_step = True
        elif ans == "s":
            skipping = True
    prev_step = -1
    prev_step_mat = re.search(r"(\d+)", step)
    if prev_step_mat:
        prev_step = int(prev_step_mat[1]) - 1
    time_taken_full = str((datetime.datetime.now() - time_start))
    time_taken = prettify_date_diff(time_taken_full)
    if was_task_completed:
        step_status = f"    {get_dt_now()[11:]}  ✅  Done"
    elif skipping:
        step_status = f"    {get_dt_now()[11:]}  ❌  Skipped"
    elif back_one_step:
        step_status = f"    {get_dt_now()[11:]}  ⬆️   Return to {prev_step}."
    else:
        step_status = "    ??? Unknown status. Please create an issue " + get_dt_now()
    step_status += f"\n     {time_taken}\n"
    print(step_status)
    completed_steps.append(step + '\n' + step_status + "\n\n".join(paragraphs))
    return completed_steps, back_one_step


def main():
    sections = parse_md()
    print("do[\\n]e ✅\t[s]kip ❌\t[b]ack ⬆️ \t[l]og 💡\t[t]angent ✨\n[h]elp  ❔\t[q]uit 🚪\n")

    hasq = '-q' in sys.argv
    heading_time_start = datetime.datetime.now()
    text_to_write = ""
    top_heading = True
    user_vars = {}
    for section in sections:
        section_str = section + '\n' + '=' * len(section)
        print(section_str, end='')
        if top_heading:
            print(f"\n  ⏳ {get_dt_now()}\n")
            top_heading = False
        else:
            print("\n")

        done_steps = []
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
    getchar()  # will quit on q
    with open(output_path, 'a') as f:
        f.write(text_to_write)
    print("💾", output_path)


def cleanup():  # Remove detritus, esp on ^C
    for f in glob.glob("temp*"):
        os.remove(f)


try:
    main()
finally:
    cleanup()
