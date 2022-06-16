import argparse
from nltk.translate import chrf

parser = argparse.ArgumentParser()
parser.add_argument('--original')
parser.add_argument('--corrected')
parser.add_argument('--transformed')
args = parser.parse_args()

def read_file(file):
    with open(file, 'r', encoding='utf-8') as infile:
        return infile.read()


def evaluate(file1, file2):
    return chrf(read_file(file1), read_file(file2))

if __name__=='__main__':
    print(evaluate(args.file1, args.file2))
