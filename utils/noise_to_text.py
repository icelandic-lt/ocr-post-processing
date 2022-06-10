from string import punctuation
from random import randrange, sample, choices
from math import log
from format import format_token_out
from general_token import TextToken, get_char_errors, gen_non_overlapping_ngrams
punctuation += "–„”—«»"


def read_file(file):
    with open(file, 'r', encoding='utf8') as infile:
        for file_line in infile.readlines():
            yield file_line.rstrip()



def noise_file(file):
    for line in file:
        line_out = ''
        for tok in line.split():
            token = TextToken(tok)
            start_punct = None
            end_punct = None
            if not token.is_punct:
                if token.startswith_punct:
                    start_punct = token.original_token[token.start_punct_index[0]:len(token.start_punct_index)]
                if token.endswith_punct:
                    end_punct = token.original_token[token.end_punct_index[0]:len(token.original_token)]
            ngr = [1, 1, 1, 2, 2, 3]
            curr_ngr = sample(ngr, 1)[0]
            swap = randrange(10) < 3
            out_tok = ''
            for ngr in gen_non_overlapping_ngrams(token.clean, curr_ngr):
                out_ngr = ngr
                if swap:
                    possible_replacements = get_char_errors(ngr, freq=3)
                    if possible_replacements:
                        if randrange(10) < 5:
                            #out_ngr = sample(possible_replacements, 1)[0][0]
                            out_ngr = choices([i for i, j in possible_replacements], [log(j, 2) for i, j in possible_replacements], k=1)[0]
                            swap = False
                        else:
                            out_ngr = ngr
                out_tok += out_ngr
            out_tok = format_token_out(out_tok, start_punct, end_punct)
            line_out += out_tok
        yield line_out

if __name__ == '__main__':
    for i in noise_file(read_file('test_file.txt')):
        print(i)