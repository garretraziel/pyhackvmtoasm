import sys
from os import path, listdir

from pyhackvmtoasm.codewriter import CodeWriter
from pyhackvmtoasm.parser import Parser, ParserError


def main(input_filename, output_filename):
    if path.isfile(input_filename):
        files_to_parse = [input_filename]
    elif path.isdir(input_filename):
        files_to_parse = [f for f in listdir(input_filename) if
                          path.isfile(path.join(input_filename, f)) and path.splitext(f)[1] == ".vm"]
    else:
        raise ParserError("Unknown input file:", input_filename)

    c = CodeWriter()
    c.write_init()

    for one_file in files_to_parse:
        with open(one_file) as f:
            vmcode = f.read()
        p = Parser(vmcode)
        c.set_file_name(one_file)

        while p.has_more_commands():
            p.advance()
            if p.command_type in ("C_PUSH", "C_POP"):
                c.write_push_pop(p.command_type, p.arg1, p.arg2)
            elif p.command_type == "C_ARITHMETIC":
                c.write_arithmetic(p.arg1)
            elif p.command_type == "C_LABEL":
                c.write_label(p.arg1)
            elif p.command_type == "C_GOTO":
                c.write_goto(p.arg1)
            elif p.command_type == "C_IF":
                c.write_if(p.arg1)

    with open(output_filename, "w") as f:
        f.write(c.output)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"{sys.argv[0]} (<program.vm>|<program directory>)")
        exit(1)
    main(sys.argv[1], path.splitext(sys.argv[1])[0] + '.asm')
