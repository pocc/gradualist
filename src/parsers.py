"""Various functions to parse procedural documents.

Currently supports markdown. With pandoc, it could support
an arbitrary numbuer of formats. That requires a dependency tho,
so it might make sense to add HTML parsing.
"""
import os
import re
from typing import Dict, List
import sys


def parse_md(files: List[str]) -> Dict[str, List[str]]:
    for f in files:
        if not os.path.exists(sys.argv[1]):
            print(f"Markdown file, {sys.argv[1]}, not found")
            sys.exit(1)

    text = ""
    for source_md in files:
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
    scripts: Dict[str, List[str]] = {}
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
