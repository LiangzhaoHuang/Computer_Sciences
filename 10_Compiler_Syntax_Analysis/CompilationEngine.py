class CompilationEngine:
    def __init__(self, tokenizer, output):
        self.tokenizer = tokenizer
        self.output = output
        self.indent_level = 0  # NEW: track the current indentation

    def write(self, line):
        indentation = '  ' * self.indent_level
        self.output.write(indentation + line + '\n')

    def compileClass(self):
        self.write("<class>")
        self.indent_level += 1
        self.tokenizer.advance()  # 'class'
        self.write(f"<keyword> {self.tokenizer.keyword()} </keyword>")
        self.tokenizer.advance()  # className
        self.write(f"<identifier> {self.tokenizer.identifier()} </identifier>")
        self.tokenizer.advance()  # '{'
        self.write(f"<symbol> {self.tokenizer.symbol()} </symbol>")
        self.tokenizer.advance()

        while self.tokenizer.tokenType() == 'KEYWORD' and self.tokenizer.keyword() in ('static', 'field'):
            self.compileClassVarDec()

        while self.tokenizer.tokenType() == 'KEYWORD' and self.tokenizer.keyword() in ('constructor', 'function', 'method'):
            self.compileSubroutine()

        self.write(f"<symbol> {self.tokenizer.symbol()} </symbol>")  # '}'
        self.tokenizer.advance()
        self.indent_level -= 1
        self.write("</class>")

    def compileClassVarDec(self):
        self.write("<classVarDec>")
        self.indent_level += 1
        while not (self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == ';'):
            self.writeToken()
            self.tokenizer.advance()
        self.write(f"<symbol> {self.tokenizer.symbol()} </symbol>")
        self.tokenizer.advance()
        self.indent_level -= 1
        self.write("</classVarDec>")

    def compileSubroutine(self):
        self.write("<subroutineDec>")
        self.indent_level += 1
        while not (self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == '('):
            self.writeToken()
            self.tokenizer.advance()
        self.write(f"<symbol> {self.tokenizer.symbol()} </symbol>")
        self.tokenizer.advance()
        self.compileParameterList()
        self.write(f"<symbol> {self.tokenizer.symbol()} </symbol>")
        self.tokenizer.advance()

        self.write("<subroutineBody>")
        self.indent_level += 1
        self.write(f"<symbol> {self.tokenizer.symbol()} </symbol>")  # '{'
        self.tokenizer.advance()

        while self.tokenizer.tokenType() == 'KEYWORD' and self.tokenizer.keyword() == 'var':
            self.compileVarDec()

        self.compileStatements()

        self.write(f"<symbol> {self.tokenizer.symbol()} </symbol>")  # '}'
        self.tokenizer.advance()
        self.indent_level -= 1
        self.write("</subroutineBody>")
        self.indent_level -= 1
        self.write("</subroutineDec>")

    def compileParameterList(self):
        self.write("<parameterList>")
        self.indent_level += 1
        while not (self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == ')'):
            self.writeToken()
            self.tokenizer.advance()
        self.indent_level -= 1
        self.write("</parameterList>")

    def compileVarDec(self):
        self.write("<varDec>")
        self.indent_level += 1
        while not (self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == ';'):
            self.writeToken()
            self.tokenizer.advance()
        self.write(f"<symbol> {self.tokenizer.symbol()} </symbol>")
        self.tokenizer.advance()
        self.indent_level -= 1
        self.write("</varDec>")

    def compileStatements(self):
        self.write("<statements>")
        self.indent_level += 1
        while self.tokenizer.tokenType() == 'KEYWORD' and self.tokenizer.keyword() in ('let', 'if', 'while', 'do', 'return'):
            if self.tokenizer.keyword() == 'let':
                self.compileLet()
            elif self.tokenizer.keyword() == 'if':
                self.compileIf()
            elif self.tokenizer.keyword() == 'while':
                self.compileWhile()
            elif self.tokenizer.keyword() == 'do':
                self.compileDo()
            elif self.tokenizer.keyword() == 'return':
                self.compileReturn()
        self.indent_level -= 1
        self.write("</statements>")

    def compileLet(self):
        self.write("<letStatement>")
        self.indent_level += 1
        self.writeToken(); self.tokenizer.advance()  # let
        self.writeToken(); self.tokenizer.advance()  # varName
        if self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == '[':
            self.writeToken(); self.tokenizer.advance()
            self.compileExpression()
            self.writeToken(); self.tokenizer.advance()
        self.writeToken(); self.tokenizer.advance()  # '='
        self.compileExpression()
        self.writeToken(); self.tokenizer.advance()  # ';'
        self.indent_level -= 1
        self.write("</letStatement>")

    def compileIf(self):
        self.write("<ifStatement>")
        self.indent_level += 1
        self.writeToken(); self.tokenizer.advance()  # if
        self.writeToken(); self.tokenizer.advance()  # (
        self.compileExpression()
        self.writeToken(); self.tokenizer.advance()  # )
        self.writeToken(); self.tokenizer.advance()  # {
        self.compileStatements()
        self.writeToken(); self.tokenizer.advance()  # }
        if self.tokenizer.tokenType() == 'KEYWORD' and self.tokenizer.keyword() == 'else':
            self.writeToken(); self.tokenizer.advance()
            self.writeToken(); self.tokenizer.advance()  # {
            self.compileStatements()
            self.writeToken(); self.tokenizer.advance()  # }
        self.indent_level -= 1
        self.write("</ifStatement>")

    def compileWhile(self):
        self.write("<whileStatement>")
        self.indent_level += 1
        self.writeToken(); self.tokenizer.advance()  # while
        self.writeToken(); self.tokenizer.advance()  # (
        self.compileExpression()
        self.writeToken(); self.tokenizer.advance()  # )
        self.writeToken(); self.tokenizer.advance()  # {
        self.compileStatements()
        self.writeToken(); self.tokenizer.advance()  # }
        self.indent_level -= 1
        self.write("</whileStatement>")

    def compileDo(self):
        self.write("<doStatement>")
        self.indent_level += 1
        self.writeToken(); self.tokenizer.advance()  # do
        while not (self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == '('):
            self.writeToken(); self.tokenizer.advance()
        self.writeToken(); self.tokenizer.advance()
        self.compileExpressionList()
        self.writeToken(); self.tokenizer.advance()
        self.writeToken(); self.tokenizer.advance()
        self.indent_level -= 1
        self.write("</doStatement>")

    def compileReturn(self):
        self.write("<returnStatement>")
        self.indent_level += 1
        self.writeToken(); self.tokenizer.advance()
        if not (self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == ';'):
            self.compileExpression()
        self.writeToken(); self.tokenizer.advance()
        self.indent_level -= 1
        self.write("</returnStatement>")

    def compileExpression(self):
        self.write("<expression>")
        self.indent_level += 1
        self.compileTerm()
        while self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() in '+-*/&|<>=':
            self.writeToken(); self.tokenizer.advance()
            self.compileTerm()
        self.indent_level -= 1
        self.write("</expression>")

    def compileTerm(self):
        self.write("<term>")
        self.indent_level += 1
        if self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == '(':
            self.writeToken(); self.tokenizer.advance()
            self.compileExpression()
            self.writeToken(); self.tokenizer.advance()
        else:
            self.writeToken(); self.tokenizer.advance()
        self.indent_level -= 1
        self.write("</term>")

    def compileExpressionList(self):
        self.write("<expressionList>")
        self.indent_level += 1
        if not (self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == ')'):
            self.compileExpression()
            while self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol() == ',':
                self.writeToken(); self.tokenizer.advance()
                self.compileExpression()
        self.indent_level -= 1
        self.write("</expressionList>")

    def writeToken(self):
        type_ = self.tokenizer.tokenType()
        if type_ == 'KEYWORD':
            self.write(f"<keyword> {self.tokenizer.keyword()} </keyword>")
        elif type_ == 'SYMBOL':
            symbol = self.tokenizer.symbol()
            if symbol == '<':
                symbol = '&lt;'
            elif symbol == '>':
                symbol = '&gt;'
            elif symbol == '&':
                symbol = '&amp;'
            self.write(f"<symbol> {symbol} </symbol>")
        elif type_ == 'IDENTIFIER':
            self.write(f"<identifier> {self.tokenizer.identifier()} </identifier>")
        elif type_ == 'INT_CONST':
            self.write(f"<integerConstant> {self.tokenizer.intVal()} </integerConstant>")
        elif type_ == 'STRING_CONST':
            self.write(f"<stringConstant> {self.tokenizer.stringVal()} </stringConstant>")