from string import punctuation
from random import randrange, sample, choices
from math import log
from format import format_token_out
from tokens import TextToken, get_char_errors, gen_non_overlapping_ngrams
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
            # The noise added to a token can be based on a uni-, bi- or trigram
            # These weights (1 being the most likely and 3 least so) are not based
            # on real data. Should probably be researched further.
            ngr = [1, 1, 1, 2, 2, 3]
            # A random noise ngram picked.
            curr_ngr = sample(ngr, 1)[0]
            # Random noise is added if swap is less than 1, i.e. in 10% of all tokens.
            swap = randrange(100) < 15
            out_tok = ''
            for ngr in gen_non_overlapping_ngrams(token.original_token, curr_ngr):
                # out_ngr is initialized as an ngram from the (correct) token
                out_ngr = ngr
                if swap:
                    # Known errors (that appear more than 3 times) are fetched from the error database
                    possible_replacements = get_char_errors(ngr, freq=3)
                    # If there are any known errors for the current ngram
                    if possible_replacements:
                        edit = randrange(10)
                        if edit < 5:
                            # A known ngram error is inserted into a correct token, based on their log(frequency)
                            # in the error database. The training files are very homogeneous, so log(frequency) is
                            # used to give a more balanced distribution and prevent overfitting.
                            out_ngr = choices([i for i, j in possible_replacements], [log(j, 2) for i, j in possible_replacements], k=1)[0]
                            swap = False
                        elif edit == 6:
                            # Used to add some \s noise into the data, as that's a very common error type.
                            # This block could be simplified.
                            if randrange(100) < 30:
                                out_ngr = f' {out_ngr} '
                        else:
                            out_ngr = ngr
                out_tok += out_ngr
            out_tok = format_token_out(out_tok, start_punct, end_punct)
            # Add spaces between all characters of a word in 1% of all tokens.
            # The frequency (1%) is not based on real data analysis.
            # The number 66 is random and doesn't matter.
            add_spaces_between_all_chars = randrange(100) == 66
            if add_spaces_between_all_chars:
                out_tok = ' '.join(out_tok)
            line_out += out_tok
        delete_space = randrange(33)
        # Delete a space between two tokens in 3% of all lines.
        # The frequency (3%) is not based on real data analysis.
        # The number 19 is random and doesn't matter.
        if delete_space == 19:
            space_indexes = [index for index in range(len(line_out)) if line_out.startswith(' ', index)]
            if space_indexes:
                random_index = sample(space_indexes, 1)[0]
                line_out = line_out[:random_index] + line_out[random_index+1:]
        yield line_out

if __name__ == '__main__':
    for i in noise_file(read_file('test_file.txt')):
        print(i)
