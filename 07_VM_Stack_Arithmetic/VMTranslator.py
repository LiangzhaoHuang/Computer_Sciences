#Parser
import sys
import os

# Check if a filename is provided
if len(sys.argv) != 2:
    print("Usage: python VMTranslator.py file.vm")
    sys.exit(1)

# Get the input filename
input_path = sys.argv[1]

# Check the extension
if not input_path.endswith('.vm'):
    print("Error: Input file must have a .vm extension.")
    sys.exit(1)

# Derive output filename
base_name = os.path.splitext(os.path.basename(input_path))[0]
output_path = os.path.join(os.path.dirname(input_path), base_name + '.asm')

# Read lines from input .vm file
with open(input_path, 'r') as f:
    vm_lines = f.readlines()

# Clean the lines (optional step)
vm_lines = [line.split('//')[0].strip() for line in vm_lines if line.strip() and not line.strip().startswith('//')]

label = {'local': 'LCL',
         'argument': 'ARG',
         'this': 'THIS',
         'that': 'THAT',
         }

addr0 = {'temp': 5,
         'static': 16,
         'pointer': 3}

label_counter = 0
asm_lines = []
# Translate vm_lines to Hack assembly and write to output_path
for line in vm_lines:
    to_print = '//' + line + '\n'
    line_data = line.split()
    if line_data[0] == 'push':
        if line_data[1] == 'constant':
            to_print += ('@{:s}\n'
                         'D=A\n'
                         '@SP\n'
                         'A=M\n'
                         'M=D\n').format(line_data[2]) #*SP = value
        elif line_data[1] in ['local', 'argument', 'this', 'that']:
            to_print += ('@{:s}\n'
                         'D=A\n'
                         '@{:s}\n'
                         'D=D+M\n'
                         '@R13\n'
                         'M=D\n'
                         '@R13\n'
                         'A=M\n'
                         'D=M\n'
                         '@SP\n'
                         'A=M\n'
                         'M=D\n').format(line_data[2], label[line_data[1]]) #*SP = *(segment + value)
        elif line_data[1] in ['temp', 'static', 'pointer']:
            to_print += ('@R{:d}\n'
                         'D=M\n'
                         '@SP\n'
                         'A=M\n'
                         'M=D\n').format(addr0[line_data[1]] + int(line_data[2])) #*SP = *(Rn + value)
        to_print += '@SP\nM=M+1\n'  # SP++
    elif line_data[0] == 'pop':
        if line_data[1] in ['local', 'argument', 'this', 'that']:
            to_print += ('@{:s}\n'
                         'D=A\n'
                         '@{:s}\n'
                         'D=D+M\n'
                         '@R14\n'
                         'M=D\n'
                         '@SP\n'
                         'AM=M-1\n'
                         'D=M\n'
                         '@R14\n'
                         'A=M\n'
                         'M=D\n').format(line_data[2], label[line_data[1]]) #*(segment + value) = *(SP - 1); SP--
        elif line_data[1] in ['temp', 'static', 'pointer']:
            to_print += ('@SP\n'
                         'AM=M-1\n'
                         'D=M\n'
                         '@R{:d}\n'
                         'M=D\n').format(addr0[line_data[1]] + int(line_data[2])) #*(Rn + value) = *(SP - 1); SP--
    elif line_data[0] == 'add':
        to_print += ('@SP\n'
                     'AM=M-1\n'
                     'D=M\n'
                     '@SP\n'
                     'A=M-1\n'
                     'M=D+M\n')
    elif line_data[0] == 'sub':
        to_print += ('@SP\n'
                     'AM=M-1\n'
                     'D=M\n'
                     '@SP\n'
                     'A=M-1\n'
                     'M=M-D\n')
    elif line_data[0] == 'neg':
        to_print += ('@SP\n'
                     'A=M-1\n'
                     'M=-M\n')
    elif line_data[0] == 'not':
        to_print += ('@SP\n'
                     'A=M-1\n'
                     'M=!M\n')
    elif line_data[0] == 'or':
        to_print += ('@SP\n'
                     'AM=M-1\n'
                     'D=M\n'
                     'A=A-1\n'
                     'M=D|M\n')
    elif line_data[0] == 'and':
        to_print += ('@SP\n'
                     'AM=M-1\n'
                     'D=M\n'
                     'A=A-1\n'
                     'M=D&M\n')
    elif line_data[0] in ['eq', 'lt', 'gt']:
        jump = {'eq': 'JEQ', 'lt': 'JLT', 'gt': 'JGT'}[line_data[0]]
        label_true = f"{line_data[0].upper()}_TRUE{label_counter}"
        label_end = f"{line_data[0].upper()}_END{label_counter}"
        to_print += (f'@SP\n'
                     f'AM=M-1\n'
                     f'D=M\n'
                     f'A=A-1\n'
                     f'D=M-D\n'
                     f'@{label_true}\n'
                     f'D;{jump}\n'
                     f'@SP\n'
                     f'A=M-1\n'
                     f'M=0\n'
                     f'@{label_end}\n'
                     f'0;JMP\n'
                     f'({label_true})\n'
                     f'@SP\n'
                     f'A=M-1\n'
                     f'M=-1\n'
                     f'({label_end})\n')
        label_counter += 1
    asm_lines.append(to_print)

out = open(output_path, 'w')
out.writelines(asm_lines)
out.close()


