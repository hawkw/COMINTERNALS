import re
import c

line_comment_re = re.compile(r":.+\n")

def comment(token):
    c_com = c.comment(token)
    if c_com:
        return c_com
    else:
        return line_comment_re.match(token)

asm_name = re.compile(r"""^(?:#define|#ifdef|#ifndef)\s+([a-zA-Z_0-9]+).+$|ENTRY\(([a-zA-Z_0-9]+)\)\s*$|(?:global|extern|\.globl|\.global)\s+([a-zA-Z_0-9]+)\s*$""")
