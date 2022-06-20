import argparse
from nltk.translate import chrf

parser = argparse.ArgumentParser()
parser.add_argument('--original')
parser.add_argument('--corrected')
parser.add_argument('--transformed')
args = parser.parse_args()

def read_file(file):
    with open(file, 'r', encoding='utf-8') as infile:
        for (index, line) in enumerate(infile):
            yield (index, line.rstrip())


def evaluate(original_file, corrected_file, transformed_file):
    original = list(read_file(original_file))
    corrected = list(read_file(corrected_file))
    original_corrected_set = set(original) & set(corrected)
    original_comp_base = [line for (index, line) in original if (index, line) not in original_corrected_set]
    corrected_comp_base = [line for (index, line) in corrected if (index, line) not in original_corrected_set]
    #transformed = list(read_file(transformed_file))
    #return chrf(read_file(file1), read_file(file2))

if __name__=='__main__':
    print(evaluate(args.original, args.corrected, None))
