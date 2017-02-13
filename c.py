import re

types = ["short", "int", "long", "float", "double", "char", "void", "bool",
         "FILE"]
containers = ["enum", "struct", "union", "typedef"]
preprocessor = ["define", "ifdef", "ifndef", "include", "endif", "defined"]
# libs = ["_WIN32", "NULL", "fprintf", "stderr", "memset", "size_t", "fflush", "abort", "u_char", "u_long", "caddr_t"]
modifiers = ["const", "volatile", "extern", "static", "register", "signed",
             "unsigned"]
flow = ["if", "else", "goto",  "case", "default", "continue", "break"]
loops = ["for", "do", "while" "switch"]
keywords = types + containers + modifiers + flow + loops + ["return", "sizeof", "sbrk", "__asm__", "__volatile__"] + preprocessor + libs
comm = r"\s*\/\*(\*(?!\/)|[^*]|\n)*\*\/"
comment_re = re.compile(comm, re.DOTALL)
ident = r"[_a-zA-Z][_a-zA-Z0-9]{0,30}"
ident_re = re.compile(ident)
invalid_id_re = re.compile(r"[^_a-zA-Z]")
string_lit = "\"[^\"]*\""
hex_lit = r"0x[a-fA-F0-9]+"
include = r"#include\s*<[a-zA-Z\/]+\.(?:h|asm|S)>"
include_re = re.compile( r"#include\s*<([a-zA-Z\/]+\.(?:h|asm|S))>")

split_re = re.compile("({}|{}|{}|{}|{})"
                      .format(comm, include, hex_lit, ident, string_lit),
                      re.DOTALL)

modifier = r"""const|volatile|extern|static|register|signed|unsigned|__inline__|__asm__|__volatile__|inline"""

header_name = re.compile(r"""^(?:(?:""" + modifier +
                         r""")\s+)*[a-zA-Z_0-9]+[\s\*]+([a-zA-Z_0-9]+).+$|""" +
                         r"""#define\s+([a-zA-Z_0-9]+).+$""")

def tokens(string):
    return filter(lambda n: n is not None, split_re.split(string))


def comment(string):
    return comment_re.match(string)

def ident(string):
    return ident_re.match(string) if string.strip() not in keywords else None

def is_keyword(string):
    return True if string.strip() in keywords else False

def include(string):
    return include_re.match(string)
