"""For getting one line of input.
If "personal" is in the step, then assume it's confidential
and prevent the answer from being visible.
"""
import re

import getpass
from typing import Dict

from interrupts import custom_input


def get_text_line(step: str, var_name: str) -> Dict[str, str]:
    step = re.sub(r'(${(.*?)})', r'\1', step)
    if "personal" in var_name:
        value = getpass.getpass()
    else:
        value = custom_input(False)
    return {var_name: value}
