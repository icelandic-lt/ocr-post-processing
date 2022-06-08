import re
from glob import glob
from difflib import SequenceMatcher
from pathlib import Path
from collections import Counter

def read_file(file):
    with open(file, 'r', encoding='utf-8') as infile:
        return infile.read().splitlines()

def create_correct_word_list(correct_files):
    correct_words = set()
    correct_files = glob(f'{correct_files}/*')
    for file in correct_files:
        file = read_file(file)
        for line in file:
            for word in line.split():
                correct_words.add(word)
    return correct_words

def clean_string(string):
    possible_word = re.findall(r'[\w-]+|[^\s\w]', string)
    return max(possible_word, key=len)


class ParallelLines:
    def __init__(self, original, corrected, correct_words):
        self.original = original.split()
        self.corrected = corrected.split()
        self.same_length = len(self.original) == len(self.corrected)
        self.correct_words = correct_words

    def pair_errors_in_line(self, include_punct=False):
        for original, corrected in zip(self.original, self.corrected):
            if original != corrected:
                similarity = SequenceMatcher(None, original, corrected).ratio()
                if similarity > 0.66 and original not in self.correct_words:
                    if not include_punct:
                        yield clean_string(original), clean_string(corrected)
                    else:
                        yield original, corrected

    def get_detailed_errors(self):
        for original, corrected in zip(self.original, self.corrected):
            pair_details = {
                'original': None,
                'corrected': None,
                'replace': [],
                'delete': [],
                'insert': [],
                'equal': []
            }
            if original != corrected:
                similarity = SequenceMatcher(None, original, corrected).ratio()
                pair_details['original'] = original
                pair_details['corrected'] = corrected
                if similarity > 0.66:
                    seq_matcher = SequenceMatcher(None, original, corrected)
                    for tag, src_1, src_2, tgt_1, tgt_2 in seq_matcher.get_opcodes():
                        pair_details[tag].append([original[src_1:src_2], corrected[tgt_1:tgt_2]])
                    yield pair_details

    def __str__(self):
        return ' '.join(self.original) + ' '.join(self.corrected)


def read_file_lines(file):
    with open(file, 'r', encoding='utf-8') as infile:
        return infile.read().splitlines()

def write_replacements_to_single_file(error_filename, correct_word_list, ocr_files_path, corrected_files_path):
    replacements = []
    with open(error_filename, 'w', encoding='utf-8') as outfile:
        original_path = ocr_files_path
        corrected_path = corrected_files_path
        original_files = glob(f'{original_path}/*')
        for file in original_files:
            filename = Path(file).name
            corrected_file = f'{corrected_path}/{filename}'
            original_lines = read_file_lines(file)
            corrected_lines = read_file_lines(corrected_file)
            for i in zip(original_lines, corrected_lines):
                parallel_lines = ParallelLines(original=i[0], corrected=i[1], correct_words=correct_word_list)
                for error in list(parallel_lines.get_detailed_errors()):
                    for repl in error['replace']:
                        replacements.append(tuple(repl))
        counter = Counter(replacements).most_common()
        for repl in counter:
            outfile.write(repl[0][0] + '\t' + repl[0][1] + '\t' + str(repl[1]) + '\n')

if __name__ == '__main__':
    pass
