"""Interrupts that can interrupt the current task
and then return focus back to that task."""
import os
from pathlib import Path
import re
import sys

from utils import get_dt_now

import getch


def interrupt_help():
    """Dummy help while I code this tool."""
    print("Visit https://github.com/pocc/gradualist for more info")


def interrupt_log() -> str:
    log_str = input(f"    {get_dt_now()[11:]}      Log a thought\n        ")
    log_line = get_dt_now()[11:] + log_str
    print(f"""    {get_dt_now()[11:]}      Continuing""")
    return log_line


def interrupt_do() -> str:
    log_str = input(f"    {get_dt_now()[11:]}      What do you want to do?\n        ")
    log_line = "*  [ ] " + get_dt_now()[11:] + " " + log_str
    print(f"""    {get_dt_now()[11:]}      Continuing""")
    return log_line


def interrupt_tangent() -> None:
    distraction = input(f"    {get_dt_now()[11:]}      What's distracting?\n        ")
    new_tangent = f"* [ ] {get_dt_now()} {distraction}\n"
    home = str(Path.home())
    tangent_file = os.path.join(home, 'log', 'tangent.md')
    with open(tangent_file, 'a') as f:
        f.write(new_tangent)
    print("        >>", tangent_file)
    print(f"""    {get_dt_now()[11:]}      Continuing""")


def custom_input(second_newline_required: bool) -> str:
    status_char: str = ""
    prev_char: str = ""
    resp = ""
    """
    Should be false when:
    * both are '\n' and second_newline_required
    * status_char == '\n' and not second_newline_required
    """
    while not ((status_char == '\n' and prev_char == '\n' and second_newline_required) or (status_char == '\n' and not second_newline_required)):
        prev_prev_char = prev_char
        prev_char = status_char
        status_char: str = getch.getch()
        if prev_char == ',':
            print('', flush=True)
            if status_char == 'l':
                interrupt_log()
            elif status_char == 't':
                interrupt_tangent()
            elif status_char == 'd':
                interrupt_do()
            elif status_char in ['b', 's']:
                return status_char
        if ord(status_char) == 127:
            if len(resp) > 0:
                resp = resp[:-1]
            # Make delete work visually (one space back, last char erased)
            sys.stdout.buffer.write(b'\b')
            sys.stdout.buffer.flush()
            sys.stdout.buffer.write(b'\x7f')
            sys.stdout.buffer.flush()
            sys.stdout.buffer.write(b'\b')
            sys.stdout.buffer.flush()
        elif prev_prev_char and ord(prev_prev_char) == 27:
            # <-, ^, V, -> arrow keys, ESC, and more report as \x1b, then [, then a capital letter
            # Getch receives 3 inputs when these keys are pressed which requires a prev_prev_char
            # Not worth fooling with creating a text editor
            pass
        else:
            print(status_char, end='', sep='', flush=True)
            resp += status_char
    # Get rid of trailing newlines
    resp = re.sub(r"\n*$", "", resp)
    print(f"`{resp}`")
    return resp
