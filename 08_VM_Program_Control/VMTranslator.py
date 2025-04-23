import sys
import os
from Parser import Parser
from CodeWriter import CodeWriter

def main():
    input_path = sys.argv[1]
    is_directory = os.path.isdir(input_path)

    if is_directory:
        files = [f for f in os.listdir(input_path) if f.endswith('.vm')]
        output_path = os.path.join(input_path, os.path.basename(input_path) + '.asm')
    else:
        files = [os.path.basename(input_path)]
        input_path = os.path.dirname(input_path)
        output_path = os.path.join(input_path, files[0].replace('.vm', '.asm'))

    writer = CodeWriter(output_path)
    # Only call Sys.init if it's present
    if 'Sys.vm' in files:
        writer.write_init()

    for file in files:
        full_path = os.path.join(input_path, file)
        parser = Parser(full_path)
        writer.set_file_name(file.replace('.vm', ''))

        while parser.has_more_commands():
            parser.advance()
            cmd_type = parser.command_type()
            if cmd_type == 'C_ARITHMETIC':
                writer.write_arithmetic(parser.arg1())
            elif cmd_type in ('C_PUSH', 'C_POP'):
                writer.write_push_pop(cmd_type, parser.arg1(), parser.arg2())
            elif cmd_type == 'C_LABEL':
                writer.write_label(parser.arg1())
            elif cmd_type == 'C_GOTO':
                writer.write_goto(parser.arg1())
            elif cmd_type == 'C_IF':
                writer.write_if(parser.arg1())
            elif cmd_type == 'C_FUNCTION':
                writer.write_function(parser.arg1(), parser.arg2())
            elif cmd_type == 'C_CALL':
                writer.write_call(parser.arg1(), parser.arg2())
            elif cmd_type == 'C_RETURN':
                writer.write_return()

    writer.close()

if __name__ == "__main__":
    main()
