import argparse
from tokenizer import split_into_sentences, correct_spaces

parser = argparse.ArgumentParser()
parser.add_argument('--infile')
args, unknown = parser.parse_known_args()

def read_file(file):
    with open(file, 'r', encoding='utf-8') as infile:
        return split_into_sentences(infile.read())


if __name__ == '__main__':
    for sent in read_file(args.infile):
        print((correct_spaces(sent)))