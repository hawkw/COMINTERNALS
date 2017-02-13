import markovify, re, os
import textwrap
from functools import reduce

types = ["short", "int", "long", "float", "double", "char", "void", "bool",
         "FILE"]
containers = ["enum", "struct", "union", "typedef"]
preprocessor = ["define", "ifdef", "ifndef", "include", "endif", "defined"]
libs = ["_WIN32", "NULL", "fprintf", "stderr", "memset", "size_t", "fflush", "abort", "u_char", "u_long", "caddr_t"]
modifiers = ["const", "volatile", "extern", "static", "register", "signed",
             "unsigned"]
flow = ["if", "else", "goto",  "case", "default", "continue", "break"]
loops = ["for", "do", "while" "switch"]
keywords = types + containers + modifiers + flow + loops + ["return", "sizeof", "sbrk"] + preprocessor + libs
comment = r"\s*\/\*(\*(?!\/)|[^*]|\n)*\*\/"
comment_re = re.compile(comment, re.DOTALL)
ident = r"[_a-zA-Z][_a-zA-Z0-9]{0,30}"
ident_re = re.compile(ident)
invalid_id_re = re.compile(r"[^_a-zA-Z]")
string_lit = "\"[^\"]*\""
hex_lit = r"0x[a-fA-F0-9]+"
include = r"#include\s*<[a-zA-Z/]+\.h>"
include_re = re.compile( r"#include\s*<([a-zA-Z/]+\.h)>")
split_re = re.compile("({}|{}|{}|{}|{})"
                      .format(comment, include, hex_lit, ident, string_lit),
                      re.DOTALL)

modifier = r"""const|volatile|extern|static|register|signed|unsigned|__inline__|inline"""

header_name = re.compile(r"""^(?:(?:""" + modifier +
                         r""")\s+)*[a-zA-Z_0-9]+[\s\*]+([a-zA-Z_0-9]+).+$|""" +
                         r"""#define\s+([a-zA-Z_0-9]+).+$""")

def header_names(path):
    """Generates a list of names defined in the header file at `path`."""
    with open(path) as f:
        for line in f:
            match = header_name.match(line)
            if match:
                name = match.group(2) if match.group(2) else match.group(1)
                print("found name {} in header {}".format(name, path))
                yield name

def headers_in(dir_path):
    """Generates a list of header files in directory `dir`."""
    for root, _, filenames in os.walk(dir_path):
            for f in filenames:
                if f.endswith(".h"): yield os.path.join(root, f)

def make_karl():
    """Makes the Karl Markov model"""
    # Get raw text as string.
    with open("communist_manifesto.txt") as f:
        text = f.read()
    # skip the Project Gutenberg footer at the end
    gutenberg_footer = 72910
    # make the model
    return markovify.Text(text[:gutenberg_footer])

include = [h for h in headers_in("/usr/include")]
included_headers = []
no_mangle = []

karl_markov = make_karl()
the_peoples_idents = {}


# replace a capitalist identifier with a new, ideologically correct identifier
def replace_ident(old_ident):
    # print("old:" + old_ident)
    if old_ident in the_peoples_idents:
        new = the_peoples_idents[old_ident]
        print("ident \"{}\" already mapped to \"{}\"".format(old_ident, new))
        return new
    else:
        new_ident = make_ident(old_ident)
        the_peoples_idents[old_ident] = new_ident
        print("new ident \"{}\" mapped to \"{}\"".format(old_ident, new_ident))
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
    return begin + new_line + end

def make_ident(old_id):
    length = len(old_id)
    ident = None
    while not ident:
        length = length + 1 if length <= 30 else length
        id_try = karl_markov.make_short_sentence(length,
                                                 tries=100,
                                                 max_overlap_ratio=100,
                                                 max_overlap_total=300)
        # ensure the new identifier is valid
        if id_try:
            id_try = invalid_id_re.sub("", id_try.replace(' ', '_'))
            id_try = id_try.upper() if old_id.isupper() else id_try.lower()
            if id_try not in the_peoples_idents.values():
                ident = id_try
    return ident

def make_comment(length):
    comment = None
    length = 50 if length < 50 else length
    # print("length: {}".format(length))
    while not comment:
        comment = karl_markov.make_short_sentence(length,
                                                  tries=100,
                                                  max_overlap_ratio=10,
                                                  max_overlap_total=600)
    return comment


def replace_comment(old_comment):
    # indent amounts for the comment block
    first_indent = re.match("(\s+)*", old_comment).group(0)
    subsequent_indent = first_indent.replace('\n', "")

    old_sentences = re.sub(r"[\*\/\\]", "", old_comment).split('.')
    # print(old_sentences)

    # generate a new comment
    new_sentences = map(lambda s: make_comment(len(s)), old_sentences)

    new_comment = textwrap.wrap(" ".join(new_sentences),
                                75 - len(subsequent_indent))

    new_comment[0] = "{}/* {}".format(first_indent, new_comment[0])
    nlines = len(new_comment)
    new_comment = "\n{} * ".format(subsequent_indent).join(new_comment) + " */"
    # print(new_comment)
    return new_comment
    # return '\n'.join(map(replace_comment_line, old_comment.split('\n')))


def replace_any(token):
    # print("string is:" + string)
    if comment_re.match(token):
        return replace_comment(token)
    elif include_re.match(token):
        header = include_re.match(token).group(0)
        if header in include and header not in included_headers:
            print("found new header {}, with names:".format(header))
            for name in header_names(os.path.join("/usr/include", header)):
                print("\t\"{}\"", name)
                no_mangle.append(name)
            included_headers.append(header)
        return token
    elif token.strip() in keywords:
        return token
    elif ident_re.match(token):
        return token if token in no_mangle else replace_ident(token)
    else:
        return token


def replace_all(string):
    result = ""
    split = filter(lambda n: n is not None, split_re.split(string))
    for s in map(lambda s: replace_any(s), split):
        # print("\"" + s + "\"")
        result = result + s
    # print(split)
    return result

in_dir = "linux"
out_dir = "out"

for root, dirs, filenames in os.walk(in_dir):
    for f in filenames:
        if f.endswith(".c") or f.endswith(".h"):
            path = os.path.join(root, f)
            with open(path) as code:
                out_path = os.path.join(out_dir, root)
                if not os.path.exists(out_path):
                    os.makedirs(out_path)
                with open(os.path.join(out_path, f), "w") as out:
                    print("making: " + os.path.join(out_path, f))
                    out.write(replace_all(code.read()))
