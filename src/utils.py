import datetime
import os
import re
import sys
import tty
import termios
from typing import List


def get_dt_now():
    return str(datetime.datetime.now())[:19]


def prettify_date_diff(date_str: str) -> str:
    """replace 0 in date diff with ' ', strip mantissa"""
    time_taken = date_str.split('.')[0]
    time_taken_mat = re.match(r"^[0:]+", time_taken)
    if time_taken_mat:
        zeros = time_taken_mat[0]
        time_taken = time_taken.replace(zeros, len(zeros) * " ")
        if time_taken[-1] == " ":
            time_taken = time_taken[:-1] + "0"
    return time_taken


def get_multiline_input():
    """Get multiple lines. Quits on "\n\n" """
    lines: List[str] = []
    while True:  # Add lines until \n\n
        print("        ", end='')
        line = input()
        if line:
            lines.append(line)
        else:
            break
    return '\n'.join(lines)


# https://gist.github.com/jasonrdsouza/1901709
def getchar() -> str:
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
    return ch


# https://www.geeksforgeeks.org/viewing-all-defined-variables-in-python/
def debug_dump_vars():
    for name in dir():
        # Print the item if it doesn't start with '__'
        if not name.startswith('__'):
            myvalue = eval(name)
            print(name, "is", type(myvalue), "and is equal to ", myvalue)
