import re

class JackTokenizer:
    KEYWORDS = {"class", "constructor", "function", "method", "field", "static",
                "var", "int", "char", "boolean", "void", "true", "false", "null",
                "this", "let", "do", "if", "else", "while", "return"}

    SYMBOLS = "{}()[].,;+-*/&|<>=~"

    def __init__(self, input_str):
        self.tokens = self.tokenize(input_str)
        self.current = 0

    def tokenize(self, code):
        # Remove comments
        code = re.sub(r"//.*", "", code)
        code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)

        # Tokenize using regex
        pattern = r'(".*?"|\b\w+\b|[' + re.escape(self.SYMBOLS) + r'])'
        return [token for token in re.findall(pattern, code) if token.strip() != ""]

    def hasMoreTokens(self):
        return self.current < len(self.tokens)

    def advance(self):
        if self.hasMoreTokens():
            self.current_token = self.tokens[self.current]
            self.current += 1

    def tokenType(self):
        if self.current_token in self.KEYWORDS:
            return "KEYWORD"
        elif self.current_token in self.SYMBOLS:
            return "SYMBOL"
        elif self.current_token.startswith('"'):
            return "STRING_CONST"
        elif self.current_token.isdigit():
            return "INT_CONST"
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
        return self.current_token[1:-1]
