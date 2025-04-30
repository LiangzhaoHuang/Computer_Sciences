import re

class JackTokenizer:
    KEYWORDS = {
        "class", "constructor", "function", "method", "field", "static",
        "var", "int", "char", "boolean", "void", "true", "false", "null",
        "this", "let", "do", "if", "else", "while", "return"
    }

    SYMBOLS = '{}()[].,;+-*/&|<>=~'

    def __init__(self, input_str):
        # Remove comments
        input_str = re.sub(r'//.*', '', input_str)
        input_str = re.sub(r'/\*.*?\*/', '', input_str, flags=re.DOTALL)

        # Tokenize
        token_pattern = r'"[^"\n]*"|[\w_]+|[{}()[\].,;+\-*/&|<>=~]'
        self.tokens = re.findall(token_pattern, input_str)
        self.index = 0
        self.current_token = self.tokens[0] if self.tokens else None

    def hasMoreTokens(self):
        return self.index < len(self.tokens)

    def advance(self):
        if self.hasMoreTokens():
            self.current_token = self.tokens[self.index]
            self.index += 1
        else:
            self.current_token = None

    def token(self):
        return self.current_token

    def tokenType(self):
        if self.current_token in self.KEYWORDS:
            return "KEYWORD"
        elif self.current_token in self.SYMBOLS:
            return "SYMBOL"
        elif self.current_token.isdigit():
            return "INT_CONST"
        elif self.current_token.startswith('"'):
            return "STRING_CONST"
        else:
            return "IDENTIFIER"

    def keyword(self):
        return self.current_token

    def symbol(self):
        return self.current_token

    def identifier(self):
        return self.current_token

    def intVal(self):
        return int(self.current_token)

    def stringVal(self):
        return self.current_token.strip('"')

    def peek(self):
        if self.index < len(self.tokens):
            return self.tokens[self.index]
        return None
