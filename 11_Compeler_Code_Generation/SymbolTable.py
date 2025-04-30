class SymbolTable:
    def __init__(self):
        self.class_scope = {}
        self.subroutine_scope = {}
        self.counts = {"static": 0, "field": 0, "arg": 0, "var": 0}

    def startSubroutine(self):
        self.subroutine_scope = {}
        self.counts["arg"] = 0
        self.counts["var"] = 0

    def define(self, name, type_, kind):
        table = self.class_scope if kind in ("static", "field") else self.subroutine_scope
        table[name] = (type_, kind, self.counts[kind])
        self.counts[kind] += 1

    def varCount(self, kind):
        return self.counts[kind]

    def kindOf(self, name):
        if name in self.subroutine_scope:
            return self.subroutine_scope[name][1]
        elif name in self.class_scope:
            return self.class_scope[name][1]
        return None

    def typeOf(self, name):
        if name in self.subroutine_scope:
            return self.subroutine_scope[name][0]
        elif name in self.class_scope:
            return self.class_scope[name][0]
        return None

    def indexOf(self, name):
        if name in self.subroutine_scope:
            return self.subroutine_scope[name][2]
        elif name in self.class_scope:
            return self.class_scope[name][2]
        return None