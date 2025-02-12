#!/usr/bin/env python3
import consts as K
import subprocess
import random
import time
import os

MAX_LEN = 1000
MAX_LOOPS = 100000
MAX_TRIES = 10000

L_INS = len(K.INSTRUCTIONS)

template = """
def f():
    a=1
    b=1
    c=1
    d=1
    e=1
    f=1
    g=1
    h=1
    i=1
    j=1
    k=1
    l=1
    m=1
    n=1
    o=1
    p=1
    q=1
    r=1
    s=1
    t=1
    u=1
    v=1
    w=1
    x=1
    y=1
    z=1
    print('end')
k = bytes([%s])
v = f.__code__.replace(co_code=bytes(k))
exec(v)
"""
# import marshal
# marshal.dump(f.__code__, open('f.dump', 'wb+'))
# code = marshal.load(open('test.dump'))
# f.__code__ == code

python_p = 'compiled.p'


def create_python_binary(instruction_seq):
    instructions = [str(i) for i in (K.PREFIX +
                                     (instruction_seq + K.PRINT + K.SUFFIX))]
    with open(python_p, 'w+') as file:
        file.write(template % ','.join(instructions))


def execute_binary():
    try:
        result = subprocess.run(['python3', python_p], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1)
    except subprocess.TimeoutExpired:
        return 'tmeout'
    stderr = result.stderr.decode("utf-8")
    stdout = result.stdout.decode("utf-8")
    if stdout[-3:] == 'end':
        return 'incomplete'
    elif stdout == '':
        if result.returncode == -11:  # segfault
            return 'error'
        elif result.returncode == -10:  # segfault
            return 'error'
        elif result.returncode < 0:  # segfault
            return 'error'
        else:
            # if it returns without end but without signal, then it is complete
            print(result.returncode, "complete")
            return 'complete'
    else:
        return stderr


def validate_python(input_str, log_level):
    """ return:
        rv: "complete", "incomplete" or "wrong",
        n: the index of the character -1 if not applicable
        c: the character where error happened  "" if not applicable
    """
    try:
        instruction_seq = input_str
        create_python_binary(instruction_seq)
        output = execute_binary()
        print(repr(output))
        if output == "complete":
            return "complete", -1, ""
        elif output == "incomplete":
            return "incomplete", -1, ""
        else:
            return "wrong", len(input_str), "input_str[-1]"
    except Exception as e:
        msg = str(e)
        print("Can't parse: " + msg)
        n = len(msg)
        return "wrong", n, ""


def get_next_char(log_level, pool):
    if L_INS - len(pool) > MAX_TRIES:
        return None
    print(len(pool), end=' ')
    input_char = pool.pop()
    return input_char


def generate(log_level, misbehaving_ins):
    """
    Feed it one character at a time, and see if the parser rejects it.
    If it does not, then append one more character and continue.
    If it rejects, replace with another character in the set.
    :returns completed string
    """
    prev_str = []
    i = 0
    pool = list(K.INSTRUCTIONS)
    random.shuffle(pool)
    while i < MAX_LOOPS:
        i += 1
        char = get_next_char(log_level, pool)
        if not char:
            misbehaving_ins.append(prev_str)
            return prev_str
        curr_str = prev_str + char
        rv, n, c = validate_python(curr_str, log_level)

        if log_level:
            print("%s n=%d, c=%s. Input string is %s" % (rv, n, c, curr_str))
        if rv == "complete":
            if random.randrange(5) == 0:
                return curr_str
            else:
                pool = list(K.INSTRUCTIONS)
                random.shuffle(pool)
                prev_str = curr_str
                continue
        elif rv == "incomplete":  # go ahead...
            print('.', end='')
            if len(curr_str) >= MAX_LEN:
                return curr_str
            pool = list(K.INSTRUCTIONS)
            random.shuffle(pool)
            prev_str = curr_str
            continue
        elif rv == "wrong":  # try again with a new random character do not save current character
            continue
        else:
            print("ERROR What is this I dont know !!!")
            break
    return None


def create_valid_strings(n, log_level):
    os.remove("valid_inputs.txt") if os.path.exists('valid_inputs.txt') else None
    os.remove("misbehaving_instructions.txt") if os.path.exists('misbehaving_instructions.txt') else None
    tic = time.time()
    i = 0
    while True:  # i < 10
        i += 1
        misbehaving_ins = []
        created_string = generate(log_level, misbehaving_ins)
        toc = time.time()
        if created_string is not None:
            with open("valid_inputs.txt", "a") as myfile, open("misbehaving_instructions.txt", "a") as file:
                var = f"Time used until input was generated: {toc - tic:f}\n" + repr(created_string) + "\n\n"
                myfile.write(var)
                [file.write(str(char) + "\n") for char in misbehaving_ins]


create_valid_strings(10, 0)
