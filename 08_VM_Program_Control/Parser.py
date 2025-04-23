class Parser:
    def __init__(self, input_file):
        with open(input_file, 'r') as f:
            self.lines = [line.split('//')[0].strip() for line in f if line.strip() and not line.startswith('//')]
        self.current_command = None
        self.index = 0

    def has_more_commands(self):
        return self.index < len(self.lines)

    def advance(self):
        self.current_command = self.lines[self.index]
        self.index += 1

    def command_type(self):
        if self.current_command.startswith('push'):
            return 'C_PUSH'
        elif self.current_command.startswith('pop'):
            return 'C_POP'
        elif self.current_command.startswith('label'):
            return 'C_LABEL'
        elif self.current_command.startswith('goto'):
            return 'C_GOTO'
        elif self.current_command.startswith('if-goto'):
            return 'C_IF'
        elif self.current_command.startswith('function'):
            return 'C_FUNCTION'
        elif self.current_command.startswith('call'):
            return 'C_CALL'
        elif self.current_command.startswith('return'):
            return 'C_RETURN'
        else:
            return 'C_ARITHMETIC'

    def arg1(self):
        if self.command_type() == 'C_ARITHMETIC':
            return self.current_command
        return self.current_command.split()[1]

    def arg2(self):
        return int(self.current_command.split()[2])
