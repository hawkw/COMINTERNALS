import markovify
import os
import re
from functools import reduce

types = ["short", "int", "long", "float", "double", "char", "void", "bool", "FILE"]
containers = ["enum", "struct", "union", "typedef"]
preprocessor = ["define", "ifdef", "ifndef", "include", "endif", "defined"]
libs = [ "_WIN32", "NULL", "fprintf", "stderr", "memset", "caddr_t", "size_t"]
modifiers = [ "const", "volatile", "extern", "static", "register", "signed", "unsigned"]
flow = [ "if", "else",
         "goto",
         "case", "default",
         "continue", "break"  ]
loops = ["for", "do", "while" "switch" ]
keywords = types + containers + modifiers + flow + loops + [ "return", "sizeof", "sbrk" ] + preprocessor + libs


# Get raw text as string.
with open("communist_manifesto.txt") as f:
    text = f.read()

in_dir = "Malloc-Implementations/allocators/kmalloc"
out_dir = "out"
# Build the model.
karl_markov = markovify.Text(text)
print("\"" + karl_markov.make_short_sentence(100) + "\" -- Karl Markov")

the_peoples_idents = {}

def make_ident(length):
    ident = None
    while not ident:
        ident = karl_markov.make_short_sentence(length,
                    tries=100,
                    max_overlap_ratio=100,
                    max_overlap_total=300)
        if ident in the_peoples_idents:
            ident = None
    # print("new:" + ident)
    return ident.replace(' ', '_')

comment = r"\/\*(\*(?!\/)|[^*])*\*\/"
comment_re = re.compile(comment, re.DOTALL)
ident = r"[_a-zA-Z][_a-zA-Z0-9]{0,30}"
ident_re = re.compile(ident)
invalid_ident_re = re.compile(r"[^_a-zA-Z]")
string_lit = "\"[^\"]*\""
hex_lit = r"0x[a-fA-F0-9]+"
split_re = re.compile("({}|{}|{}|{}|<[^>]+>)"
                        .format(comment, hex_lit, ident, string_lit),
                      re.DOTALL)

# replace a capitalist identifier with a new, ideologically correct identifier
def replace_ident(old_ident):
    print("old:" + old_ident)
    if old_ident in the_peoples_idents:
        return the_peoples_idents[old_ident]
    else:
        length = len(old_ident)
        length = length if length > 15 else length + 15
        new_ident = invalid_ident_re.sub("", make_ident(length))
        the_peoples_idents[old_ident] = new_ident
        return new_ident

def replace_comment_line(old_line):
    if old_line.startswith("/*"):
        begin = "/* "
    elif old_line.startswith(" *"):
        begin = " * "
    else:
        begin = ""
    end = " */" if old_line.endswith("*/") else ""
    new_line = None
    length = 30 if len(old_line) < 30 else len(old_line)
    while not new_line:
        new_line = karl_markov.make_short_sentence(length,
                        tries=100,
                        max_overlap_ratio=100,
                        max_overlap_total=600)
    return begin + new_line  + end

def replace_comment(old_comment):
    return '\n'.join(map(replace_comment_line, old_comment.split('\n')))

def replace_any(token):
    # print("string is:" + string)
    if comment_re.match(token):
        return replace_comment(token)
    elif ident_re.match(token) and not (token in keywords):
        return replace_ident(token)
    else:
        return token

def replace_all(string):
    result = ""
    split = filter(lambda n: n != None, split_re.split(string))
    for s in map(lambda s: replace_any(s), split):
        print("\"" + s + "\"")
        result = result + s
    # print(split)
    return result

for root, dirs, filenames in os.walk(in_dir):
    for f in filenames:
        if f.endswith(".c"):
            with open(os.path.join(root, f)) as code:
                out_path = os.path.join(out_dir, root)
                if not os.path.exists(out_path):
                    os.makedirs(out_path)
                with open(os.path.join(out_path, f), "w") as out:
                    out.write(replace_all(code.read()))
