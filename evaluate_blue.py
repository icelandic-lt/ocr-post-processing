from ast import arg
from nltk.translate import bleu_score
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--original')
parser.add_argument('--corrected')
parser.add_argument('--transformed')
args = parser.parse_args()

def read_file(file):
    with open(file, 'r', encoding='utf-8') as infile:
        for line in infile:
            yield line.rstrip().split()


def evaluate(original_file, corrected_file, transformed_file):
    scores = {

    }
    original_file = list([sent] for sent in original_file)
    corrected_file = list(corrected_file)
    original_corrected_score = bleu_score.corpus_bleu(original_file, corrected_file)
    
    corrected_file = [[sent] for sent in corrected_file]
    transformed_file = list(transformed_file)
    corrected_transformed_score = bleu_score.corpus_bleu(corrected_file, transformed_file)
    
    scores['Original/Corrected'] = round(original_corrected_score, 7)
    scores['Corrected/Transformed'] = round(corrected_transformed_score, 7)
    scores['Improvement:'] = round((corrected_transformed_score - original_corrected_score), 7)
    scores['Prop improv:'] = round((corrected_transformed_score - original_corrected_score)/(1 - original_corrected_score), 7)
    return scores


if __name__ == '__main__':
    for i in evaluate(read_file(args.original), read_file(args.corrected), read_file(args.transformed)).items():
        print(i)