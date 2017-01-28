import markovify
import os
import re
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


# Get raw text as string.
with open("communist_manifesto.txt") as f:
    text = f.read()

in_dir = "Malloc-Implementations/allocators/kmalloc"
out_dir = "out"

# Build the model.
# skip the Project Gutenberg footer at the end
gutenberg_footer = 72910
karl_markov = markovify.Text(text[:gutenberg_footer])
print("\"" + karl_markov.make_short_sentence(100, tries=100) + "\" -- Karl Markov")

the_peoples_idents = {}


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

comment = r"\s*\/\*(\*(?!\/)|[^*]|\n)*\*\/"
comment_re = re.compile(comment, re.DOTALL)
ident = r"[_a-zA-Z][_a-zA-Z0-9]{0,30}"
ident_re = re.compile(ident)
invalid_id_re = re.compile(r"[^_a-zA-Z]")
string_lit = "\"[^\"]*\""
hex_lit = r"0x[a-fA-F0-9]+"
include = r"#include\s*<[a-zA-Z/]+\.h>"
split_re = re.compile("({}|{}|{}|{}|{})"
                      .format(comment, include, hex_lit, ident, string_lit),
                      re.DOTALL)


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
    elif ident_re.match(token) and not (token.strip() in keywords):
        return replace_ident(token)
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


for root, dirs, filenames in os.walk(in_dir):
    for f in filenames:
        if f.endswith(".c"):
            with open(os.path.join(root, f)) as code:
                out_path = os.path.join(out_dir, root)
                if not os.path.exists(out_path):
                    os.makedirs(out_path)
                with open(os.path.join(out_path, f), "w") as out:
                    out.write(replace_all(code.read()))
        # else:
        #     with open(os.path.join(root, f)) as code:
        #         out_path = os.path.join(out_dir, root)
        #         if not os.path.exists(out_path):
        #             os.makedirs(out_path)
        #         with open(os.path.join(out_path, f), "w") as out:
        #             out.write(code.read())
