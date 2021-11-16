"""On enter, complete task."""
from typing import Tuple, List
import sys

from utils import getchar
from interrupts import interrupt_tangent, interrupt_log, interrupt_help


def launch_interrupt() -> Tuple[List[str], str]:
    """Hit enter to complete, s to skip, b to go back, t to tangent, l to log."""
    ans = ""
    log_lines: List[str] = []
    while ans not in ["\n", "\r"]:
        ans = getchar()
        if ans == 'q':
            print("Quitting...")
            sys.exit(1)
        # Skipping/going back preempts this step from finishing
        elif ans in ['s', 'b']:
            return log_lines, ans
        elif ans == 'h':
            interrupt_help()
        elif ans == 'l':
            new_line = interrupt_log()
            log_lines.append(new_line)
        elif ans == 't':
            interrupt_tangent()
    return log_lines, ans
