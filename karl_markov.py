import markovify
import textwrap
import re

cite_re = re.compile(r"""((?:[0-9]+\. c,)?\s*(?:pp?\. [0-9]+\.?))""")
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

if __name__ == "__main__":
    com = make_karl()
    sentence = None
    while not sentence:
        sentence = com.make_sentence()
    print("\n\"{}\" \n -- Karl Markov\n".format(textwrap.fill(sentence, 50)))
