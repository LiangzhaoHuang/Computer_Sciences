import os
import sys
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine
from VMWriter import VMWriter

def compile_file(jack_file):
    with open(jack_file, 'r') as f:
        code = f.read()

    tokenizer = JackTokenizer(code)
    output_path = jack_file.replace('.jack', '.vm')
    with open(output_path, 'w') as vm_file:
        vm_writer = VMWriter(vm_file)
        compiler = CompilationEngine(tokenizer, vm_writer)
        compiler.compileClass()
        vm_file.flush()

def compile_directory(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.jack'):
            compile_file(os.path.join(directory, filename))

def main():
    if len(sys.argv) != 2:
        print("Usage: python JackCompiler.py [file.jack | dir]")
        input_path = './ConvertToBin/'
    else:
        input_path = sys.argv[1]

    if os.path.isdir(input_path):
        compile_directory(input_path)
    elif input_path.endswith('.jack'):
        compile_file(input_path)
    else:
        print("Error: Provide a .jack file or a directory containing .jack files.")

if __name__ == '__main__':
    main()