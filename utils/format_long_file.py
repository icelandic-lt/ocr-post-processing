from tokenizer import split_into_sentences, correct_spaces
from general_token import gen_non_overlapping_ngrams
from glob import glob
from pathlib import Path

all_files = glob('../data/textasafn_arnastofnun/corrected/*')

def read_lines(file):
    with open(file, 'r', encoding='utf-8') as infile:
        for line in infile.read().splitlines():
            for sentence in list(split_into_sentences(line)):
                if len(sentence) < 128:
                    yield correct_spaces(sentence)
                else:
                    sentence_chunks = gen_non_overlapping_ngrams(sentence.split(), 8)
                    for chunk in sentence_chunks:
                        yield correct_spaces(' '.join(chunk))


def write_lines(file, lines):
    for line in lines:
        with open(f'{file}', 'a', encoding='utf-8') as outfile:
            outfile.write(line + '\n')

counter = 0
for file in all_files:
    counter += 1
    print(f'[{counter}/{len(all_files)}]')
    shorter_lines = read_lines(file)
    write_lines(file, shorter_lines)