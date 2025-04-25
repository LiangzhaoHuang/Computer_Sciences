from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine
import sys
import os

def jack2xml(input_path):
    # Read source code
    with open(input_path, 'r') as f:
        code = f.read()

    # Tokenize and write T.xml for debugging
    tokenizer = JackTokenizer(code)
    token_output_path = input_path.replace('.jack', 'T.xml')
    with open(token_output_path, 'w') as out:
        out.write('<tokens>\n')
        while tokenizer.hasMoreTokens():
            tokenizer.advance()
            type_ = tokenizer.tokenType()
            value = ''
            if type_ == 'KEYWORD':
                value = tokenizer.keyword()
            elif type_ == 'SYMBOL':
                val = tokenizer.symbol()
                if val == '<': value = '&lt;'
                elif val == '>': value = '&gt;'
                elif val == '&': value = '&amp;'
                else: value = val
            elif type_ == 'IDENTIFIER':
                value = tokenizer.identifier()
            elif type_ == 'INT_CONST':
                value = str(tokenizer.intVal())
            elif type_ == 'STRING_CONST':
                value = tokenizer.stringVal()
            out.write(f'<{type_.lower()}> {value} </{type_.lower()}>\n')
        out.write('</tokens>\n')

    # Re-tokenize and parse using CompilationEngine
    tokenizer2 = JackTokenizer(code)
    output_file = open(input_path.replace('.jack', '.xml'), 'w')
    parser = CompilationEngine(tokenizer2, output_file)
    parser.compileClass()
    output_file.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: python tokenize.py input.jack")
    else:
        jack2xml(sys.argv[1])

if __name__ == '__main__':
    main()
