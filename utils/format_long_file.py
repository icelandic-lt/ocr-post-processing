from tokenizer import split_into_sentences, correct_spaces
from general_token import gen_non_overlapping_ngrams
from glob import glob
from pathlib import Path

all_files = glob('../data/textasafn_arnastofnun/*')

def read_lines(file):
    with open(file, 'r', encoding='utf-8') as infile:
        for line in infile.read().splitlines():
            for sentence in list(split_into_sentences(line)):
                sentence = correct_spaces(sentence)
                if len(sentence) < 128:
                    yield sentence
                else:
                    sentence_chunks = gen_non_overlapping_ngrams(sentence.split(), 8)
                    for chunk in sentence_chunks:
                        yield correct_spaces(' '.join(chunk))


def write_lines(file, lines):
    lines_to_write = list(lines)
    with open(f'{file}', 'w', encoding='utf-8') as outfile:
        for line in lines_to_write:
            outfile.write(line + '\n')

counter = 0
for file in all_files:
    counter += 1
    print(f'[{counter}/{len(all_files)}]')
    shorter_lines = list(read_lines(file))
    write_lines(file, shorter_lines)