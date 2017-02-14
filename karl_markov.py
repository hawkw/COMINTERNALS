import markovify
import textwrap
import re

cite_re = re.compile(r"""((?:[0-9]+\. c,)?\s*(?:pp?\. [0-9]+\.?))""")

def make_karl():
    """Makes the Karl Markov model"""
    # Get raw text as string.
    with open("communist_manifesto.txt") as f:
        manifesto_text = f.read()
    # skip the Project Gutenberg footer at the end
    gutenberg_footer = 72910
    # make the model
    manifesto = markovify.Text(manifesto_text[:gutenberg_footer])
    with open("kapital_vol_1.txt") as f:
        kapital_text = cite_re.sub("", f.read())
    kapital = markovify.Text(kapital_text)
    return markovify.combine([manifesto, kapital])

com = make_karl()
sentence = None
while not sentence:
    sentence = com.make_sentence()
print("\n\"{}\" \n -- Karl Markov\n".format(textwrap.fill(sentence, 50)))
