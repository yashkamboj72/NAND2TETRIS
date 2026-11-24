#!/usr/bin/env python3
"""Regenerate Box.asm for a given K:  python gen_box.py 41"""
import sys

k = int(sys.argv[1]) if len(sys.argv) > 1 else 41
rows = 20
words = (k % 4) + 1            # width = 16 * words pixels
offset = 32 * k                # row K starts at SCREEN + 32*K

asm = f"""// Box.asm  --  K = {k}
// Box: starts at row {k}, {rows} rows tall, {16*words} pixels wide ({words} word(s)) from left edge.
// While any key is pressed the box is black; when released it is cleared.
// Row r starts at SCREEN + 32*r, so the first word is SCREEN + {offset}.

(LOOP)
    @KBD
    D=M
    @PRESSED
    D;JNE           // key pressed -> paint black
    @value
    M=0             // no key -> paint white (clear)
    @DRAW
    0;JMP
(PRESSED)
    @value
    M=-1            // -1 = 1111111111111111 = 16 black pixels
(DRAW)
    @SCREEN
    D=A
    @{offset}
    D=D+A           // D = address of first word of the box
    @addr
    M=D
    @{rows}
    D=A
    @rowsleft
    M=D             // rows left to draw
(ROWLOOP)
    @{words}
    D=A
    @colsleft
    M=D             // words left in this row
    @addr
    D=M
    @p
    M=D             // p = pointer to current word
(COLLOOP)
    @value
    D=M
    @p
    A=M
    M=D             // RAM[p] = value
    @p
    M=M+1           // next word to the right
    @colsleft
    MD=M-1
    @COLLOOP
    D;JGT           // more words in this row?
    @32
    D=A
    @addr
    M=D+M           // move down one screen row (+32 words)
    @rowsleft
    MD=M-1
    @ROWLOOP
    D;JGT           // more rows?
    @LOOP
    0;JMP           // go check the keyboard again
"""
with open("Box.asm", "w") as f:
    f.write(asm)
print(f"Box.asm written for K={k}: row {k}, {rows} rows, {16*words}px wide")
