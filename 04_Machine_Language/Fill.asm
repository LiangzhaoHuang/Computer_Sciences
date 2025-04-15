// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

//// Replace this comment with your code.

(LOOP1)

@KBD
D=M
@LOOP1
D;JEQ

//LOOP fill
@8192
D=A
@pix
M=D

(LOOP2)
@pix
D=M
@SCREEN
A=D+A
M=-1
@pix
M=M-1

@pix
D=M
@END2
D;JLT

@LOOP2
0;JMP

(END2)
@KBD
D=M
@CLEAN
D;JEQ

@END2
0;JMP

//LOOP clean
(CLEAN)
@8192
D=A
@pix
M=D

(LOOP3)
@pix
D=M
@SCREEN
A=D+A
M=0
@pix
M=M-1

@pix
D=M
@LOOP1
D;JLT

@LOOP3
0;JMP

