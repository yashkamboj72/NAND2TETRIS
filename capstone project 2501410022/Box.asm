// Box.asm  --  K = 22
// Box: starts at row 22, 20 rows tall, 48 pixels wide (3 word(s)) from left edge.
// While any key is pressed the box is black; when released it is cleared.
// Row r starts at SCREEN + 32*r, so the first word is SCREEN + 704.

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
    @704
    D=D+A           // D = address of first word of the box
    @addr
    M=D
    @20
    D=A
    @rowsleft
    M=D             // rows left to draw
(ROWLOOP)
    @3
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
