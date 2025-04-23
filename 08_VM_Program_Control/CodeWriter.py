class CodeWriter:
    def __init__(self, output_file):
        self.file = open(output_file, 'w')
        self.filename = ''
        self.label_counter = 0

        self.segment_map = {
            'local': 'LCL',
            'argument': 'ARG',
            'this': 'THIS',
            'that': 'THAT'
        }

        self.base_addr = {
            'temp': 5,
            'pointer': 3,
            'static': 16
        }

    def set_file_name(self, filename):
        self.filename = filename

    def write_arithmetic(self, command):
        asm = f'// {command}\n'
        if command in ['add', 'sub', 'and', 'or']:
            op = {'add': '+', 'sub': '-', 'and': '&', 'or': '|'}[command]
            if op in ['+', '&', '|']:
                asm += ('@SP\nAM=M-1\nD=M\nA=A-1\nM=D' + op + 'M\n')
            else:
                asm += ('@SP\nAM=M-1\nD=M\nA=A-1\nM=M' + op + 'D\n')
        elif command in ['neg', 'not']:
            op = {'neg': '-', 'not': '!'}[command]
            asm += ('@SP\nA=M-1\nM=' + op + 'M\n')
        elif command in ['eq', 'lt', 'gt']:
            jump = {'eq': 'JEQ', 'lt': 'JLT', 'gt': 'JGT'}[command]
            label_true = f'{command.upper()}_TRUE{self.label_counter}'
            label_end = f'{command.upper()}_END{self.label_counter}'
            self.label_counter += 1
            asm += (f'@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\n'
                    f'@{label_true}\nD;{jump}\n'
                    '@SP\nA=M-1\nM=0\n'
                    f'@{label_end}\n0;JMP\n'
                    f'({label_true})\n'
                    '@SP\nA=M-1\nM=-1\n'
                    f'({label_end})\n')
        self.file.write(asm)

    def write_push_pop(self, command_type, segment, index):
        asm = f'// {command_type} {segment} {index}\n'

        if command_type == 'C_PUSH':
            if segment == 'constant':
                asm += f'@{index}\nD=A\n'
            elif segment == 'static':
                symbol = f'{self.filename}.{index}'
                asm += f'@{symbol}\nD=M\n'
            elif segment in self.segment_map:
                asm += (f'@{index}\nD=A\n@{self.segment_map[segment]}\nD=D+M\nA=D\nD=M\n')
            elif segment in ['temp', 'pointer']:
                addr = self.base_addr[segment] + int(index)
                asm += f'@{addr}\nD=M\n'

            asm += '@SP\nA=M\nM=D\n@SP\nM=M+1\n'

        elif command_type == 'C_POP':
            if segment == 'static':
                symbol = f'{self.filename}.{index}'
                asm += ('@SP\nAM=M-1\nD=M\n'
                        f'@{symbol}\nM=D\n')
            elif segment in self.segment_map:
                asm += (f'@{index}\nD=A\n@{self.segment_map[segment]}\nD=D+M\n@R13\nM=D\n')
                asm += '@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n'
            elif segment in ['temp', 'pointer']:
                addr = self.base_addr[segment] + int(index)
                asm += f'@SP\nAM=M-1\nD=M\n@{addr}\nM=D\n'

        self.file.write(asm)

    def write_label(self, label):
        self.file.write(f'({label})\n')

    def write_goto(self, label):
        self.file.write(f'@{label}\n0;JMP\n')

    def write_if(self, label):
        self.file.write('@SP\nAM=M-1\nD=M\n')
        self.file.write(f'@{label}\nD;JNE\n')

    def write_function(self, function_name, num_locals):
        self.file.write(f'({function_name})\n')
        for _ in range(num_locals):
            self.file.write('@0\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n')

    def write_call(self, function_name, num_args):
        return_label = f'{function_name}$ret.{self.label_counter}'
        self.label_counter += 1
        asm = (f'@{return_label}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
               '@LCL\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
               '@ARG\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
               '@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
               '@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
               f'@{5 + num_args}\nD=A\n@SP\nD=M-D\n@ARG\nM=D\n'
               '@SP\nD=M\n@LCL\nM=D\n'
               f'@{function_name}\n0;JMP\n'
               f'({return_label})\n')
        self.file.write(asm)

    def write_return(self):
        asm = ('@LCL\nD=M\n@R13\nM=D\n'  # FRAME = LCL
               '@5\nA=D-A\nD=M\n@R14\nM=D\n'  # RET = *(FRAME - 5)
               '@SP\nAM=M-1\nD=M\n@ARG\nA=M\nM=D\n'  # *ARG = pop()
               '@ARG\nD=M+1\n@SP\nM=D\n'  # SP = ARG + 1
               '@R13\nAM=M-1\nD=M\n@THAT\nM=D\n'  # THAT = *(FRAME-1)
               '@R13\nAM=M-1\nD=M\n@THIS\nM=D\n'  # THIS = *(FRAME-2)
               '@R13\nAM=M-1\nD=M\n@ARG\nM=D\n'  # ARG = *(FRAME-3)
               '@R13\nAM=M-1\nD=M\n@LCL\nM=D\n'  # LCL = *(FRAME-4)
               '@R14\nA=M\n0;JMP\n')  # goto RET
        self.file.write(asm)

    def write_init(self):
        asm = ('@256\nD=A\n@SP\nM=D\n')  # SP = 256
        self.file.write(asm)
        self.write_call('Sys.init', 0)  # call Sys.init

    def close(self):
        self.file.close()
