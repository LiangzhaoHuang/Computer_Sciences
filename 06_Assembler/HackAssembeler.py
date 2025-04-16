
def to_15bit_binary(n):
    if 0 <= n < 2**15:
        return format(n, '015b')
    else:
        raise ValueError("Number out of 15-bit range (0–32767)")

def to_A_instruction(num):
    return '0{:15s}'.format(to_15bit_binary(num))

comp_table = {
    '0'   : '0101010',
    '1'   : '0111111',
    '-1'  : '0111010',
    'D'   : '0001100',
    'A'   : '0110000',
    'M'   : '1110000',
    '!D'  : '0001101',
    '!A'  : '0110001',
    '!M'  : '1110001',
    '-D'  : '0001111',
    '-A'  : '0110011',
    '-M'  : '1110011',
    'D+1' : '0011111',
    'A+1' : '0110111',
    'M+1' : '1110111',
    'D-1' : '0001110',
    'A-1' : '0110010',
    'M-1' : '1110010',
    'D+A' : '0000010',
    'D+M' : '1000010',
    'D-A' : '0010011',
    'D-M' : '1010011',
    'A-D' : '0000111',
    'M-D' : '1000111',
    'D&A' : '0000000',
    'D&M' : '1000000',
    'D|A' : '0010101',
    'D|M' : '1010101'
}

dest_table = {
    'null' : '000',  # null dest
    'M'    : '001',
    'D'    : '010',
    'MD'   : '011',
    'A'    : '100',
    'AM'   : '101',
    'AD'   : '110',
    'AMD'  : '111'
}

jump_table = {
    'null' : '000',  # null jump
    'JGT'  : '001',
    'JEQ'  : '010',
    'JGE'  : '011',
    'JLT'  : '100',
    'JNE'  : '101',
    'JLE'  : '110',
    'JMP'  : '111'
}

sym_tab = {
    'SP': 0,
    'LCL': 1,
    'ARG': 2,
    'THIS': 3,
    'THAT': 4,
    'SCREEN': 16384,
    'KBD': 24576,
}

asm_file = './asm_files/Pong.asm'
asm_data = open(asm_file, 'r').readlines()
asm_data_clean = []
out_instructions = []
sym_address = []


for line in asm_data:
    line_nc = line.split('//')[0] # remove comment
    line_clean = line_nc.replace(' ', '').strip() # remove spaces and \n
    if line_clean != '': asm_data_clean.append(line_clean)

nline = 0
for line in asm_data_clean:
    if line[0] == '(':
        sym_tab[line[1:-1]] = nline
    else:
        nline += 1

nsym = 16 #if not
for line in asm_data_clean:
    if line[0] == '@' and line[1] != 'R' and (not line[1:].isdigit()):
        if not (line[1:] in sym_tab):
            sym_tab[line[1:]] = nsym
            nsym += 1

for instruction in asm_data_clean:
    if instruction[0]=='@':
        if instruction[1] == 'R' and instruction[2:].isdigit():
            instruction = instruction.replace('R', '')
        if instruction[1:].isdigit():
            out_instructions.append(to_A_instruction(int(instruction[1:])))
        else:
            out_instructions.append(to_A_instruction(sym_tab[instruction[1:]]))
    elif instruction[0]!='(':
        if '=' in instruction:
            dest = instruction.split('=')[0]
            comp = instruction.split('=')[1].split(';')[0]
            if len(instruction.split('=')[1].split(';')) > 1:
                jump = instruction.split('=')[1].split(';')[1]
            else:
                jump = 'null'
        else:
            dest = 'null'
            comp = instruction.split(';')[0]
            jump = instruction.split(';')[1]
        out_instructions.append('111{:s}{:s}{:s}'.format(comp_table[comp], dest_table[dest], jump_table[jump]))

output = ('\n'.join(out_instructions)) + '\n'
out = open('./hack' + asm_file[5:-3] + 'hack', 'w')
out.writelines(output)