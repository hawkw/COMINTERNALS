import markovify, re, os, textwrap
import karl_markov, c
from functools import reduce

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
            id_try = c.invalid_id_re.sub("", id_try.replace(' ', '_'))
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
    if c.comment(token):
        return replace_comment(token)
    elif c.include(token):
        header = c.include(token)
        if header in include and header not in included_headers:
            print("found new header {}, with names:".format(header))
            for name in header_names(os.path.join("/usr/include", header)):
                print("\t\"{}\"", name)
                no_mangle.append(name)
            included_headers.append(header)
        return token
    elif c.ident(token):
        return token if token in no_mangle else replace_ident(token)
    else:
        return token


def replace_all(string):
    result = ""
    for s in map(lambda s: replace_any(s), c.tokens(string)):
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
