import markovify
import textwrap
import re

cite_re = re.compile(
r"""([0-9IVXMivx]*[\.\s,;]*(?:[0-9IVXMivx]+[\.\s;,]*c[\.\s;,]*)?[\.\s;,]*(?:(?:(?:t)|(?:Vol)|(?:Book)|(?:Ch))[\.\s,;]+[0-9IVXMivx]+[\.\s;,]*)*[\.\s,]*[p]+(?:[\.\s;,]+[0-9IVXMivx]+[\.\s,;]*)+)""",
 re.MULTILINE)
hyphen_newline_re = re.compile(r"""(-$)""", re.MULTILINE)

def dehyphenate(string):
    """Remove hyphenated linebreaks from 'string'."""
    return hyphen_newline_re.sub("", string)

def preprocess(string):
    """Remove hyphenated linebreaks and citations from 'string'."""
    string = cite_re.sub("", string)
    string = dehyphenate(string)
    return string

def load_file(path):
    """Load a text file for making a model."""
    with open(path) as f:
        return preprocess(f.read())

def make_karl():
    """Makes the Karl Markov model"""
    # Get raw text as string.
    manifesto_text = load_file("communist_manifesto.txt")
    kapital_text = load_file("kapital_vol_1.txt")

    # skip the Project Gutenberg footer at the end
    gutenberg_footer = 72910
    manifesto_text = manifesto_text[:gutenberg_footer]

    # make the models for each input corpus
    manifesto = markovify.Text(manifesto_text)
    kapital = markovify.Text(kapital_text)

    # combine the models
    manifesto_weight = 1
    kapital_weight = len(manifesto_text) / len(kapital_text)
    print("Das Kapital weight: {}".format(kapital_weight))

    return markovify.combine([manifesto, kapital],
                             [manifesto_weight, kapital_weight])

class KarlMarkov(object):

    def __init__(self):
        self.model = make_karl()
        self.the_peoples_idents = {}

    def make_ident(old_ident):
        length = len(old_id)
        ident = self.idents[old_ident]
        while not ident:
            length = length + 1 if length <= 30 else length
            id_try = self.model.make_short_sentence(length,
                                                    tries=100,
                                                    max_overlap_ratio=100,
                                                    max_overlap_total=300)
            # ensure the new identifier is valid
            if id_try:
                id_try = c.invalid_id_re.sub("", id_try.replace(' ', '_'))
                id_try = id_try.upper() if old_id.isupper() else id_try.lower()
                if not id_try[0].isalpha():
                    id_try = id_try[1:]
                if id_try not in self.idents.values():
                    ident = id_try
                    self.idents[old_ident] = idents
        return ident

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
            new_line = self.model.make_short_sentence(length,
                                                 tries=100,
                                                 max_overlap_ratio=100,
                                                 max_overlap_total=600)
        return begin + new_line + end


if __name__ == "__main__":
    com = make_karl()
    sentence = None
    while not sentence:
        sentence = com.make_sentence()
    print("\n\"{}\" \n -- Karl Markov\n".format(textwrap.fill(sentence, 50)))
