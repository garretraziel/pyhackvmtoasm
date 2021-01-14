import re

COMMAND_REGEX = re.compile(r"^(?P<command>\S+)(\s+(?P<arg1>\S+)(\s+(?P<arg2>\d+))?)?(\s*//.*)?$")


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, vmcode):
        self.vmcode = vmcode.splitlines()
        self.current_line = -1
        self.arg1 = None
        self.arg2 = None
        self.command_type = None

    def has_more_commands(self):
        next_line = self.current_line + 1
        while next_line < len(self.vmcode):
            if self.vmcode[next_line].strip() and not self.vmcode[next_line].strip().startswith("//"):
                return True
            next_line += 1
        return False

    def advance(self):
        self.current_line += 1
        current_line = self.vmcode[self.current_line].strip()
        while not current_line or current_line.startswith("//"):
            self.current_line += 1
            current_line = self.vmcode[self.current_line].strip()

        m = COMMAND_REGEX.match(current_line)
        if m is not None:
            cmd = m.group("command")
            self.arg1 = m.group("arg1")
            self.arg2 = int(m.group("arg2")) if m.group("arg2") is not None else None
            command_to_type = {
                "push": ("C_PUSH", 2),
                "pop": ("C_POP", 2),
                "label": ("C_LABEL", 1),
                "goto": ("C_GOTO", 1),
                "if-goto": ("C_IF", 1),
                "function": ("C_FUNCTION", 2),
                "return": ("C_RETURN", 0),
                "call": ("C_CALL", 2)
            }
            if cmd in ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]:
                self.command_type = "C_ARITHMETIC"
                self.arg1 = cmd
            elif cmd in command_to_type.keys():
                self.command_type, cnt = command_to_type[cmd]
                if (cnt == 0 and (self.arg1 is not None or self.arg2 is not None)) or \
                        (cnt == 1 and (self.arg1 is None or self.arg2 is not None)) or \
                        (cnt == 2 and (self.arg1 is None or self.arg2 is None)):
                    raise ParserError("Encountered bad arguments:", current_line)
            else:
                raise ParserError("Encountered non-assembly command:", cmd)
        else:
            raise ParserError("Encountered non-assembly command:", current_line)
