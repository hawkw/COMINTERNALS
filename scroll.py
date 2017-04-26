import markovify, re, os, textwrap, time
import karl_markov, c
from pygments import highlight
from pygments.lexers import CLexer
from pygments.formatters import Terminal256Formatter
from asm import asm_name
from functools import reduce

def header_names(path):
    """Generates a list of names defined in the header file at `path`."""
    with open(path) as f:
        for line in f:
            match = c.header_name.match(line)
            if match:
                name = match.group(2) if match.group(2) else match.group(1)
                print("found name {} in header {}".format(name, path))
                yield name

def headers_in(dir_path):
    """Generates a list of header files in directory `dir`."""
    for root, _, filenames in os.walk(dir_path):
            for f in filenames:
                if f.endswith(".h"): yield os.path.join(root, f)

def asm_names(path):
    """Generates a list of names defined in the header file at `path`."""
    with open(path) as f:
        for line in f:
            match = asm_name.match(line)
            if match:
                name = match.group(3) if match.group(3) else match.group(2) if match.group(2) else match.group(1)
                print("found name {} in asm {}".format(name, path))
                yield name

def asm_in(dir_path):
    """Generates a list of header files in directory `dir`."""
    for root, _, filenames in os.walk(dir_path):
            for f in filenames:
                if f.endswith(".S") or f.endswith(".asm"):
                    yield os.path.join(root, f)


include = [h for h in headers_in("/usr/include")]
included_headers = []
no_mangle = []

karl_markov = karl_markov.make_karl()
the_peoples_idents = {}

# replace a capitalist identifier with a new, ideologically correct identifier
def replace_ident(old_ident):
    # print("old:" + old_ident)
    if old_ident in the_peoples_idents:
        new = the_peoples_idents[old_ident]
        # print("ident \"{}\" already mapped to \"{}\"".format(old_ident, new))
        return new
    else:
        # new_ident = None
        # for pat, rep in the_peoples_idents.items():
        #     # EXPERIMENTAL:
        #     #   attempt to repace parts of idents with parts of new idents
        #     #   this should make Karl's coding style more coherent?
        #     new, n = re.subn(pat, rep, old_ident)
        #     if n > 0:
        #         new = new[:30]
        #         if new not in the_peoples_idents.values():
        #             new_ident = new
        # while not new_ident:
        #     old_chunks = old_ident.split("_")
        #     new_chunks = { }
        #     for chunk in old_chunks:
        #         new_chunks[chunk] = make_ident(chunk)
        #     new = "_".join(new_chunks.values())[:30]
        #     if new not in the_peoples_idents.values():
        #         for old_ch, new_ch in new_chunks.items():
        #             the_peoples_idents[old_ch] = new_ch
        #         new_ident = new
        new_ident = make_ident(old_ident)
        the_peoples_idents[old_ident] = new_ident
        # print("new ident \"{}\" mapped to \"{}\"".format(old_ident, new_ident))
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
        length = length + 1 if length < 30 else length
        id_try = karl_markov.make_short_sentence(length,
                                                 tries=100,
                                                 max_overlap_ratio=100,
                                                 max_overlap_total=300)
        # ensure the new identifier is valid
        if id_try:
            id_try = c.invalid_id_re.sub("", id_try.replace(' ', '_'))
            id_try = id_try.upper() if old_id.isupper() else id_try.lower()
            if id_try not in the_peoples_idents.values() and not id_try[0].isdigit():
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
    new_comment = "\n{}* ".format(subsequent_indent).join(new_comment) + " */"
    # print(new_comment)
    return new_comment
    # return '\n'.join(map(replace_comment_line, old_comment.split('\n')))


def replace_any(token):
    # print("string is:" + string)
    if c.comment(token):
        return replace_comment(token)
    elif c.include(token) | c.is_preprocessor(token):
        return token
    elif c.ident(token):
        return replace_ident(token)
    else:
        return token

formatter = Terminal256Formatter(style='native')
lexer = CLexer(stripnl=False, ensurenl=False)

def write_code(string):
    for token in c.split_re.split(string):
        if token is not None:
            # print("token is: \"{}\"".format(token))
            code = replace_any(token)
            print(highlight(code, lexer, formatter),
                  end='')

in_dir = "linux"
# for asm in asm_in(in_dir):
#     for name in asm_names(asm):
#         print("found name \"{}\" in {}".format(name, asm))
#         no_mangle.append(name)

while True:
    for root, dirs, filenames in os.walk(in_dir, topdown=True):
        filenames = [f for f in filenames if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        for f in filenames:
            the_peoples_idents = {}
            if f.endswith(".c") or f.endswith(".h"):
                path = os.path.join(root, f)
                print(path + "\n")
                with open(path) as code:
                    write_code(code.read())
