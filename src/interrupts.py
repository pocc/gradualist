"""Interrupts that can interrupt the current task
and then return focus back to that task."""
import os
from pathlib import Path

from utils import get_dt_now

import getch


def interrupt_help():
    """Dummy help while I code this tool."""
    print("Visit https://github.com/pocc/gradualist for more info")


def interrupt_log() -> str:
    log_str = input(f"    {get_dt_now()[11:]}      Log a thought\n        ")
    log_line = "* [ ] " + log_str
    print(f"""    {get_dt_now()[11:]}      Continuing""")
    return log_line


def interrupt_tangent() -> None:
    distraction = input(f"    {get_dt_now()[11:]}      What's distracting?\n        ")
    new_tangent = f"* [ ] {distraction}\n"
    home = str(Path.home())
    tangent_file = os.path.join(home, 'log', 'tangent.md')
    with open(tangent_file, 'a') as f:
        f.write(new_tangent)
    print("        >>", tangent_file)
    print(f"""    {get_dt_now()[11:]}      Continuing""")


def custom_input(second_newline_required: bool) -> str:
    status_char: str = ""
    last_char: str = ""
    resp = ""
    """
    Should be false when:
    * both are '\n' and second_newline_required
    * status_char == '\n' and not second_newline_required
    """
    while not ((status_char == '\n' and last_char == '\n' and second_newline_required) or (status_char == '\n' and not second_newline_required)):
        last_char = status_char
        status_char: str = getch.getch()
        if last_char == ',':
            print('')
            if status_char == 'l':
                interrupt_log()
            elif status_char == 't':
                interrupt_tangent()
            elif status_char in ['b', 's']:
                return status_char
        resp += status_char
        print(status_char, end='', sep='', flush=True)
    return resp
