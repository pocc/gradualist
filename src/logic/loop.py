"""While loop starts with the word `while`
And allows iteration on the same task
"""
from interrupts import custom_input


def while_loop(_: str, task: str, logvars: str) -> str:
    resp = ""
    log_data_keys = []
    print('\n')
    if logvars:
        log_data_keys = [i.strip() for i in logvars.split(',')]
    loop_resp = "Initial String"
    loop_num = 1
    while loop_resp:  # While the user doesn't press enter on a newline
        print(f"    ↪️  {loop_num}. {task}")
        loop_resp = ""
        for key in log_data_keys:
            print(f"        {key}: ", end='', sep='', flush=True)
            loop_resp = custom_input(False)
        if not log_data_keys:
            print("        ", sep='', end='', flush=True)
            loop_resp = custom_input(False)
        if loop_resp:
            resp += '    ' + str(loop_num) + '. ' + loop_resp + '\n'
        print()
        loop_num += 1
    return resp
