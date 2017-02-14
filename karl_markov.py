import markovify
import textwrap
import re

cite_re = re.compile(r"""((?:[0-9]+\. c,)?\s*(?:pp?\. [0-9]+\.?))""")

def make_karl():
    """Makes the Karl Markov model"""
    # Get raw text as string.
    with open("communist_manifesto.txt") as f:
        manifesto_text = f.read()

    with open("kapital_vol_1.txt") as f:
        kapital_text = cite_re.sub("", f.read())

    # skip the Project Gutenberg footer at the end
    gutenberg_footer = 72910
    manifesto_text = manifesto_text[:gutenberg_footer]

    # make the models for each input corpus
    manifesto = markovify.Text(manifesto_text)
    kapital = markovify.Text(kapital_text)

    # combine the models
    manifesto_weight = 1
    kapital_weight = kapital_text.len() / manifesto_text.len()
    print("Das Kapital weight: {}".format(kapital_weight))

    return markovify.combine([manifesto, kapital],
                             [manifesto_weight, kapital_weight])

com = make_karl()
sentence = None
while not sentence:
    sentence = com.make_sentence()
print("\n\"{}\" \n -- Karl Markov\n".format(textwrap.fill(sentence, 50)))
