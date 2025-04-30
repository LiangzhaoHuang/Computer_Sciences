
from SymbolTable import SymbolTable

class CompilationEngine:
    def __init__(self, tokenizer, vm_writer):
        self.tokenizer = tokenizer
        self.vm_writer = vm_writer
        self.symbol_table = SymbolTable()
        self.class_name = ""
        self.label_counter = 0

    def advance(self):
        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()

    def compileClass(self):
        self.advance()  # should now be 'class'
        print("Token after advance (expect 'class'):", self.tokenizer.token())
        self.advance()  # should now be class name
        self.class_name = self.tokenizer.identifier()
        print("Class name:", self.class_name)
        self.advance()  # should be '{'
        print("Token before class body (should be '{'):", self.tokenizer.token())
        self.advance()  # move to next token after '{'
        print("Token at class body start:", self.tokenizer.token())

        while self.tokenizer.token() in ('static', 'field'):
            print("Compiling class var dec")
            self.compileClassVarDec()

        while self.tokenizer.token() in ('constructor', 'function', 'method'):
            print("Compiling subroutine:", self.tokenizer.token())
            self.compileSubroutine()

        print("End of class:", self.tokenizer.token())
        self.advance()  # should be '}'

    def compileClassVarDec(self):
        kind = self.tokenizer.token()
        self.advance()
        var_type = self.tokenizer.token()
        self.advance()
        name = self.tokenizer.identifier()
        self.symbol_table.define(name, var_type, kind)
        self.advance()
        while self.tokenizer.token() == ',':
            self.advance()
            name = self.tokenizer.identifier()
            self.symbol_table.define(name, var_type, kind)
            self.advance()
        self.advance()  # ';'

    def compileSubroutine(self):
        self.symbol_table.startSubroutine()
        subroutine_type = self.tokenizer.token()
        self.advance()
        self.advance()  # return type
        name = self.tokenizer.identifier()
        full_name = f"{self.class_name}.{name}"
        self.advance()
        self.advance()  # '('

        if subroutine_type == "method":
            self.symbol_table.define("this", self.class_name, "arg")

        self.compileParameterList()
        self.advance()  # ')'
        self.advance()  # '{'

        n_locals = 0
        while self.tokenizer.token() == "var":
            n_locals += self.compileVarDec()

        self.vm_writer.writeFunction(full_name, n_locals)

        if subroutine_type == "constructor":
            field_count = self.symbol_table.varCount("field")
            self.vm_writer.writePush("constant", field_count)
            self.vm_writer.writeCall("Memory.alloc", 1)
            self.vm_writer.writePop("pointer", 0)
        elif subroutine_type == "method":
            self.vm_writer.writePush("argument", 0)
            self.vm_writer.writePop("pointer", 0)

        self.compileStatements()
        self.advance()  # '}'


    def compileParameterList(self):
        if self.tokenizer.token() == ')':
            return
        while True:
            type_ = self.tokenizer.token()
            self.advance()
            name = self.tokenizer.identifier()
            self.symbol_table.define(name, type_, "arg")
            self.advance()
            if self.tokenizer.token() != ',':
                break
            self.advance()

    def compileVarDec(self):
        self.advance()  # 'var'
        type_ = self.tokenizer.token()
        self.advance()
        name = self.tokenizer.identifier()
        self.symbol_table.define(name, type_, "var")
        count = 1
        self.advance()
        while self.tokenizer.token() == ',':
            self.advance()
            name = self.tokenizer.identifier()
            self.symbol_table.define(name, type_, "var")
            self.advance()
            count += 1
        self.advance()  # ';'
        return count

    def compileStatements(self):
        while self.tokenizer.token() in ['let', 'do', 'return', 'if', 'while']:
            if self.tokenizer.token() == 'do':
                self.compileDo()
            elif self.tokenizer.token() == 'return':
                self.compileReturn()
            elif self.tokenizer.token() == 'let':
                self.compileLet()
            elif self.tokenizer.token() == 'while':
                self.compileWhile()
            elif self.tokenizer.token() == 'if':
                self.compileIf()

    def compileLet(self):
        self.advance()  # 'let'
        var_name = self.tokenizer.identifier()
        self.advance()

        is_array = False
        if self.tokenizer.token() == '[':
            # Array assignment
            is_array = True
            kind = self.symbol_table.kindOf(var_name)
            index = self.symbol_table.indexOf(var_name)
            self.vm_writer.writePush(self.segmentOf(kind), index)

            self.advance()  # [
            self.compileExpression()
            self.advance()  # ]
            self.vm_writer.writeArithmetic("add")  # base + offset

        self.advance()  # '='
        self.compileExpression()
        self.advance()  # ';'

        if is_array:
            self.vm_writer.writePop("temp", 0)
            self.vm_writer.writePop("pointer", 1)
            self.vm_writer.writePush("temp", 0)
            self.vm_writer.writePop("that", 0)
        else:
            kind = self.symbol_table.kindOf(var_name)
            index = self.symbol_table.indexOf(var_name)
            self.vm_writer.writePop(self.segmentOf(kind), index)

    def compileWhile(self):
        self.advance()  # 'while'
        label_exp = self.uniqueLabel("WHILE_EXP")
        label_end = self.uniqueLabel("WHILE_END")
        self.vm_writer.writeLabel(label_exp)

        self.advance()  # '('
        self.compileExpression()
        self.advance()  # ')'

        self.vm_writer.writeArithmetic("not")
        self.vm_writer.writeIf(label_end)

        self.advance()  # '{'
        self.compileStatements()
        self.advance()  # '}'

        self.vm_writer.writeGoto(label_exp)
        self.vm_writer.writeLabel(label_end)

    def compileIf(self):
        self.advance()  # 'if'
        label_else = self.uniqueLabel("IF_ELSE")
        label_end = self.uniqueLabel("IF_END")

        self.advance()  # '('
        self.compileExpression()
        self.advance()  # ')'

        self.vm_writer.writeArithmetic("not")
        self.vm_writer.writeIf(label_else)

        self.advance()  # '{'
        self.compileStatements()
        self.advance()  # '}'

        self.vm_writer.writeGoto(label_end)
        self.vm_writer.writeLabel(label_else)

        if self.tokenizer.token() == 'else':
            self.advance()  # 'else'
            self.advance()  # '{'
            self.compileStatements()
            self.advance()  # '}'

        self.vm_writer.writeLabel(label_end)

    def compileDo(self):
        self.advance()  # 'do'
        name = self.tokenizer.identifier()
        self.advance()
        self.compileSubroutineCall(identifier=name)
        self.advance()  # ;
        self.vm_writer.writePop("temp", 0)

    def compileReturn(self):
        self.advance()
        if self.tokenizer.token() != ';':
            self.compileExpression()
        else:
            self.vm_writer.writePush("constant", 0)
        self.advance()
        self.vm_writer.writeReturn()

    def compileExpression(self):
        self.compileTerm()
        while self.tokenizer.token() in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            op = self.tokenizer.token()
            self.advance()
            self.compileTerm()
            self.writeOperator(op)

    def compileTerm(self):
        if self.tokenizer.tokenType() == 'INT_CONST':
            self.vm_writer.writePush("constant", self.tokenizer.intVal())
            self.advance()
        elif self.tokenizer.tokenType() == 'STRING_CONST':
            s = self.tokenizer.stringVal()
            self.vm_writer.writePush("constant", len(s))
            self.vm_writer.writeCall("String.new", 1)
            for c in s:
                self.vm_writer.writePush("constant", ord(c))
                self.vm_writer.writeCall("String.appendChar", 2)
            self.advance()
        elif self.tokenizer.tokenType() == 'KEYWORD':
            kw = self.tokenizer.keyword()
            if kw == 'true':
                self.vm_writer.writePush('constant', 0)
                self.vm_writer.writeArithmetic('not')
            elif kw in ('false', 'null'):
                self.vm_writer.writePush('constant', 0)
            elif kw == 'this':
                self.vm_writer.writePush('pointer', 0)
            else:
                raise ValueError(f"Unexpected keyword in term: {kw}")
            self.advance()
        elif self.tokenizer.tokenType() == 'IDENTIFIER':
            name = self.tokenizer.identifier()
            self.advance()

            if self.tokenizer.token() == '[':  # array access
                kind = self.symbol_table.kindOf(name)
                index = self.symbol_table.indexOf(name)
                self.vm_writer.writePush(self.segmentOf(kind), index)
                self.advance()
                self.compileExpression()
                self.advance()
                self.vm_writer.writeArithmetic("add")
                self.vm_writer.writePop("pointer", 1)
                self.vm_writer.writePush("that", 0)

            elif self.tokenizer.token() in ('(', '.'):  # subroutine call
                self.compileSubroutineCall(identifier=name)

            else:  # variable
                kind = self.symbol_table.kindOf(name)
                if kind is None:
                    raise ValueError(f"Undeclared identifier: {name}")
                index = self.symbol_table.indexOf(name)
                self.vm_writer.writePush(self.segmentOf(kind), index)

        elif self.tokenizer.token() == '(':
            self.advance()
            self.compileExpression()
            self.advance()
        elif self.tokenizer.token() in ['-', '~']:
            unary_op = self.tokenizer.token()
            self.advance()
            self.compileTerm()
            if unary_op == '-':
                self.vm_writer.writeArithmetic("neg")
            else:
                self.vm_writer.writeArithmetic("not")


    def compileSubroutineCall(self, identifier=None):
        """
        Assumes the current token is the start of a subroutine call.
        If identifier is None, it will use the current token as the subroutine/class/var name.
        """
        if identifier is None:
            identifier = self.tokenizer.identifier()
            self.advance()

        n_args = 0

        if self.tokenizer.token() == '.':
            self.advance()
            sub_name = self.tokenizer.identifier()
            self.advance()

            if self.symbol_table.kindOf(identifier) is not None:
                type_ = self.symbol_table.typeOf(identifier)
                kind = self.symbol_table.kindOf(identifier)
                index = self.symbol_table.indexOf(identifier)
                self.vm_writer.writePush(self.segmentOf(kind), index)
                identifier = f"{type_}.{sub_name}"
                n_args += 1
            else:
                identifier = f"{identifier}.{sub_name}"
        else:
            self.vm_writer.writePush("pointer", 0)
            identifier = f"{self.class_name}.{identifier}"
            n_args += 1

        self.advance()  # (
        n_args += self.compileExpressionList()
        self.advance()  # )

        self.vm_writer.writeCall(identifier, n_args)
        return n_args

    def writeOperator(self, op):
        ops = {
            '+': 'add', '-': 'sub',
            '*': ('call', 'Math.multiply', 2),
            '/': ('call', 'Math.divide', 2),
            '&': 'and', '|': 'or',
            '<': 'lt', '>': 'gt', '=': 'eq'
        }
        if isinstance(ops[op], tuple):
            _, name, n = ops[op]
            self.vm_writer.writeCall(name, n)
        else:
            self.vm_writer.writeArithmetic(ops[op])

    def compileExpressionList(self):
        count = 0
        if self.tokenizer.token() == ')':
            return count
        self.compileExpression()
        count += 1
        while self.tokenizer.token() == ',':
            self.advance()
            self.compileExpression()
            count += 1
        return count

    def segmentOf(self, kind):
        if kind not in ('static', 'field', 'arg', 'var'):
            raise ValueError(f"Invalid segment kind: {kind}")
        return {
            'static': 'static',
            'field': 'this',
            'arg': 'argument',
            'var': 'local'
        }[kind]

    def uniqueLabel(self, base):
        self.label_counter += 1
        return f"{base}_{self.label_counter}"
