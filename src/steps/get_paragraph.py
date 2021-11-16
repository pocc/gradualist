"""Get multiline input"""
import re
from typing import Dict
from interrupts import custom_input


def get_text_paragraph(description: str) -> Dict[str, str]:
    step_text = "        When done hit enter twice\n"
    print(step_text, flush=True)
    multiline_input = custom_input(True)
    desc = description.replace(' ', '_').lower()
    desc = re.sub(r"[^A-Za-z0-9_]*", "", desc)
    return {desc: multiline_input}
