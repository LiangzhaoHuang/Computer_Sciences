
class VMWriter:
    def __init__(self, output):
        self.output = output

    def writePush(self, segment, index):
        self.output.write(f"push {segment} {index}\n")

    def writePop(self, segment, index):
        self.output.write(f"pop {segment} {index}\n")

    def writeArithmetic(self, command):
        self.output.write(f"{command}\n")

    def writeLabel(self, label):
        self.output.write(f"label {label}\n")

    def writeGoto(self, label):
        self.output.write(f"goto {label}\n")

    def writeIf(self, label):
        self.output.write(f"if-goto {label}\n")

    def writeCall(self, name, n_args):
        self.output.write(f"call {name} {n_args}\n")

    def writeFunction(self, name, n_locals):
        self.output.write(f"function {name} {n_locals}\n")

    def writeReturn(self):
        self.output.write("return\n")

    def close(self):
        self.output.close()