#!/usr/bin/env python3
"""
Hack assembler (Nand to Tetris, Part B) -- two-pass.

Usage:   python assembler.py Prog.asm [--k 41]
Output:  Prog.hack  (one 16-bit binary string per line)

Extra feature depends on K (K = last two digits of roll number):
    K mod 3 == 0 -> write symbols.txt (all labels + variables with addresses)
    K mod 3 == 1 -> clear "Line N: message" errors instead of crashing
    K mod 3 == 2 -> warn when the same label is defined twice
"""
import sys

K = 22  # <-- CHANGE THIS to the last two digits of your roll number

# ---------------------------------------------------------------- tables
COMP = {
    # a = 0
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "!D": "0001101", "!A": "0110001",
    "-D": "0001111", "-A": "0110011", "D+1": "0011111", "A+1": "0110111",
    "D-1": "0001110", "A-1": "0110010", "D+A": "0000010", "D-A": "0010011",
    "A-D": "0000111", "D&A": "0000000", "D|A": "0010101",
    # a = 1
    "M": "1110000", "!M": "1110001", "-M": "1110011", "M+1": "1110111",
    "M-1": "1110010", "D+M": "1000010", "D-M": "1010011", "M-D": "1000111",
    "D&M": "1000000", "D|M": "1010101",
}
DEST = {"": "000", "M": "001", "D": "010", "MD": "011",
        "A": "100", "AM": "101", "AD": "110", "AMD": "111"}
JUMP = {"": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
        "JLT": "100", "JLE": "110", "JNE": "101", "JMP": "111"}

PREDEFINED = {"SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
              "SCREEN": 16384, "KBD": 24576}
for i in range(16):
    PREDEFINED["R%d" % i] = i


class AsmError(Exception):
    def __init__(self, line_no, msg):
        super().__init__("Line %d: %s" % (line_no, msg))
        self.line_no, self.msg = line_no, msg


# ---------------------------------------------------------------- helpers
def clean(line):
    """Remove comments and ALL whitespace."""
    return "".join(line.split("//")[0].split())


def is_symbol(s):
    if not s or s[0].isdigit():
        return False
    return all(c.isalnum() or c in "_.$:" for c in s)


# ---------------------------------------------------------------- pass 1
def first_pass(lines, symbols, warn_dup):
    """Remove comments/blanks, record label -> ROM address.
    Returns list of (source_line_no, instruction_text)."""
    code, rom = [], 0
    label_line = {}
    for n, raw in enumerate(lines, 1):
        s = clean(raw)
        if not s:
            continue
        if s.startswith("("):
            if not s.endswith(")") or not is_symbol(s[1:-1]):
                raise AsmError(n, "invalid label '%s'" % raw.strip())
            name = s[1:-1]
            if name in label_line:
                if warn_dup:
                    print("Warning: label '%s' on line %d already defined on "
                          "line %d (keeping the first)" % (name, n, label_line[name]))
                continue
            label_line[name] = n
            symbols[name] = rom
        else:
            code.append((n, s))
            rom += 1
    return code


# ---------------------------------------------------------------- pass 2
def translate_a(n, s, symbols, state):
    name = s[1:]
    if name.isdigit():
        value = int(name)
        if value > 32767:
            raise AsmError(n, "A-instruction value %d too large (max 32767)" % value)
    elif is_symbol(name):
        if name not in symbols:
            symbols[name] = state["next_var"]
            state["variables"].append(name)
            state["next_var"] += 1
        value = symbols[name]
    else:
        raise AsmError(n, "invalid A-instruction '%s'" % s)
    return "0" + format(value, "015b")


def translate_c(n, s):
    dest, comp, jump = "", s, ""
    if "=" in comp:
        dest, comp = comp.split("=", 1)
    if ";" in comp:
        comp, jump = comp.split(";", 1)
    if dest not in DEST:
        raise AsmError(n, "invalid destination '%s'" % dest)
    if comp not in COMP:
        raise AsmError(n, "invalid instruction (bad computation '%s')" % comp)
    if jump not in JUMP:
        raise AsmError(n, "invalid jump '%s'" % jump)
    return "111" + COMP[comp] + DEST[dest] + JUMP[jump]


def assemble(lines, k=K):
    symbols = dict(PREDEFINED)
    state = {"next_var": 16, "variables": []}
    code = first_pass(lines, symbols, warn_dup=(k % 3 == 2))
    labels = {n: a for n, a in symbols.items() if n not in PREDEFINED}

    out, errors = [], []
    for n, s in code:
        try:
            out.append(translate_a(n, s, symbols, state) if s[0] == "@"
                       else translate_c(n, s))
        except AsmError as e:
            if k % 3 != 1:
                raise                      # crash (no friendly handling)
            errors.append(str(e))
            print(e)
    return out, labels, state["variables"], symbols, errors


def main():
    args = sys.argv[1:]
    k = K
    if "--k" in args:
        i = args.index("--k")
        k = int(args[i + 1])
        del args[i:i + 2]
    if len(args) != 1 or not args[0].endswith(".asm"):
        print("Usage: python assembler.py Prog.asm [--k NN]")
        sys.exit(1)
    path = args[0]
    with open(path) as f:
        lines = f.read().splitlines()

    out, labels, variables, symbols, errors = assemble(lines, k)
    if errors:
        print("%d error(s). No .hack file written." % len(errors))
        sys.exit(1)

    hack = path[:-4] + ".hack"
    with open(hack, "w") as f:
        f.write("\n".join(out) + "\n")
    print("Wrote %s (%d instructions)" % (hack, len(out)))

    if k % 3 == 0:                          # extra feature for K mod 3 == 0
        with open("symbols.txt", "w") as f:
            f.write("# Labels (ROM addresses)\n")
            for name, addr in labels.items():
                f.write("%s\t%d\n" % (name, addr))
            f.write("# Variables (RAM addresses)\n")
            for name in variables:
                f.write("%s\t%d\n" % (name, symbols[name]))
        print("Wrote symbols.txt")


if __name__ == "__main__":
    main()
