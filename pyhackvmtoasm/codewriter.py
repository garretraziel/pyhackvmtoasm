from os import path
from .parser import ParserError


class CodeWriter:
    def __init__(self):
        self.current_filename = None
        self.output = ""
        self.id = 0
        self.function = None

    def set_file_name(self, filename):
        self.current_filename = path.splitext(path.basename(filename))[0]

    def write_init(self):
        pass

    def write_goto(self, label):
        self._write_command(f"@{label}")
        self._write_command("0;JMP")

    def write_label(self, label):
        self._write_command(f"({label})")

    def write_if(self, label):
        self._write_command("@SP")
        self._write_command("M=M-1")
        self._write_command("A=M")
        self._write_command("D=M")
        self._write_command(f"@{label}")
        self._write_command("D;JNE")

    def _write_command(self, command):
        self.output += f"{command}\n"

    def _write_comparison(self, direction):
        self._write_command("@SP")
        self._write_command("M=M-1")
        self._write_command("A=M")
        self._write_command("D=M")
        self._write_command("A=A-1")
        self._write_command("D=M-D")
        self._write_command(f"@true.{self.id}")
        self._write_command(f"D;{direction}")
        self._write_command("@SP")
        self._write_command("A=M-1")
        self._write_command("M=0")
        self._write_command(f"@end.{self.id}")
        self._write_command("0;JMP")
        self._write_command(f"(true.{self.id})")
        self._write_command("@SP")
        self._write_command("A=M-1")
        self._write_command("M=-1")
        self._write_command(f"(end.{self.id})")
        self.id += 1

    def _write_push_pop(self, command, index, register, usemem="M"):
        if command == "C_PUSH":
            self._write_command(f"@{index}")
            self._write_command("D=A")
            self._write_command(f"@{register}")
            self._write_command(f"A=D+{usemem}")
            self._write_command("D=M")
            self._write_command("@SP")
            self._write_command("M=M+1")
            self._write_command("A=M-1")
            self._write_command("M=D")
        elif command == "C_POP":
            self._write_command(f"@{index}")
            self._write_command("D=A")
            self._write_command(f"@{register}")
            self._write_command(f"D=D+{usemem}")
            self._write_command("@R13")
            self._write_command("M=D")
            self._write_command("@SP")
            self._write_command("M=M-1")
            self._write_command("A=M")
            self._write_command("D=M")
            self._write_command("@R13")
            self._write_command("A=M")
            self._write_command("M=D")
        else:
            raise ParserError("Encountered unknown push/pop command:", command)

    def write_arithmetic(self, command):
        if command == "add":
            self._write_command("@SP")
            self._write_command("M=M-1")
            self._write_command("A=M")
            self._write_command("D=M")
            self._write_command("A=A-1")
            self._write_command("M=D+M")
        elif command == "sub":
            self._write_command("@SP")
            self._write_command("M=M-1")
            self._write_command("A=M")
            self._write_command("D=M")
            self._write_command("A=A-1")
            self._write_command("M=M-D")
        elif command == "neg":
            self._write_command("@SP")
            self._write_command("A=M-1")
            self._write_command("M=-M")
        elif command == "eq":
            self._write_comparison("JEQ")
        elif command == "gt":
            self._write_comparison("JGT")
        elif command == "lt":
            self._write_comparison("JLT")
        elif command == "and":
            self._write_command("@SP")
            self._write_command("M=M-1")
            self._write_command("A=M")
            self._write_command("D=M")
            self._write_command("A=A-1")
            self._write_command("M=D&M")
        elif command == "or":
            self._write_command("@SP")
            self._write_command("M=M-1")
            self._write_command("A=M")
            self._write_command("D=M")
            self._write_command("A=A-1")
            self._write_command("M=D|M")
        elif command == "not":
            self._write_command("@SP")
            self._write_command("A=M-1")
            self._write_command("M=!M")
        else:
            raise ParserError("Unknown arithmetic command:", command)

    def write_push_pop(self, command, segment, index):
        if segment == "constant":
            if command == "C_PUSH":
                self._write_command(f"@{index}")
                self._write_command("D=A")
                self._write_command("@SP")
                self._write_command("M=M+1")
                self._write_command("A=M-1")
                self._write_command("M=D")
            else:
                raise ParserError("Encountered pop command does not make sense with constant segment.")
        elif segment == "local":
            self._write_push_pop(command, index, "LCL")
        elif segment == "argument":
            self._write_push_pop(command, index, "ARG")
        elif segment == "this":
            self._write_push_pop(command, index, "THIS")
        elif segment == "that":
            self._write_push_pop(command, index, "THAT")
        elif segment == "pointer":
            self._write_push_pop(command, index, "THIS", usemem="A")
        elif segment == "static":
            static_name = f"{self.current_filename}.{index}"
            if command == "C_PUSH":
                self._write_command(f"@{static_name}")
                self._write_command("D=M")
                self._write_command("@SP")
                self._write_command("M=M+1")
                self._write_command("A=M-1")
                self._write_command("M=D")
            elif command == "C_POP":
                self._write_command("@SP")
                self._write_command("M=M-1")
                self._write_command("A=M")
                self._write_command("D=M")
                self._write_command(f"@{static_name}")
                self._write_command("M=D")
            else:
                raise ParserError("Encountered unknown push/pop command:", command)
        elif segment == "temp":
            self._write_push_pop(command, index, "R5", usemem="A")
        else:
            raise ParserError("Encountered unknown segment:", segment)
