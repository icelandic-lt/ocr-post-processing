
from genericpath import exists
from islenska.bincompress import BinCompressed
from islenska import Bin
from string import punctuation
import pickle
from Levenshtein import distance
from substitution_token import get_similar_by_known_subs
from general_token import TextToken, OCRToken
from itertools import chain
import re
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-f', '--file')
args = parser.parse_args()

with open('../bin_tree.pickle', 'rb') as bt:
    tree = pickle.load(bt)


punctuation += "–„”—«»"

bin_conn = BinCompressed()
isl_lookup = Bin()

ocr_junk = ['<unk>', 'alt;', 'quot;', 'aguot;', '139;', 'a39;', '& 39;']


def get_most_similar_from_list(token, similar_tokens):
    """
    Gets the token with the least Levenshtein distance from a given token
    """
    least_distance = 100
    tok_and_dist = [(str(tok), distance(token, str(tok))) for tok in similar_tokens]
    min_dist = min(dist for tok, dist in tok_and_dist)
    possible_similar = [(tok, dist) for tok, dist in tok_and_dist if dist <= (min_dist+1)]
    return possible_similar

def makes_sense(token):
    return isl_lookup.lookup(token)[1] != []

def exists_in_bin(token):
    return bin_conn.lookup(token) != []


def read_lines(file):
    with open(file, 'r', encoding='utf-8') as infile:
        return infile.read().splitlines()

def clean_token(token):
    return token.strip(punctuation)

def n_good_words(line):
    sensemaking_words = [word for word in line.split() if makes_sense(clean_token(word))]
    return (len(sensemaking_words))


def format_line_out(line, junk_list):
    line_out = line
    for junk in junk_list:
        tmp_line_out = line_out.replace(junk, '')
        line_out = tmp_line_out
    return line_out.strip()


def any_exists_in_bin(token):
    return exists_in_bin(token) or exists_in_bin(token.lower()) or exists_in_bin(token.title())

def get_best_first_half_of_compound_line(line1, line2, line3):
    try:
        # line_1_1 = line1.split('<newline>')[0].strip()
        line_1_2 = line1.split('<newline>')[1].strip()
        line_2_1 = line2.split('<newline>')[0].strip()
        line_2_2 = line2.split('<newline>')[1].strip()
        line_3_1 = line3.split('<newline>')[0].strip()
        # line_3_2 = line3.split('<newline>')[1].strip()
        last_token_in_line_1_2 = {'1_2': clean_token(line_1_2.split()[-1])}
        last_token_in_line_2_1 = {'2_1': clean_token(line_2_1.split()[-1])}
        first_token_in_line_2_2 = {'2_2': clean_token(line_2_2.split()[0])}
        first_token_in_line_3_1 = {'3_1': clean_token(line_3_1.split()[0])}
        cand_1 = [line_1_2, last_token_in_line_1_2.get('1_2') + first_token_in_line_2_2.get('2_2')]
        cand_2 = [line_1_2, last_token_in_line_1_2.get('1_2') + first_token_in_line_3_1.get('3_1')]
        cand_3 = [line_2_1, last_token_in_line_2_1.get('2_1') + first_token_in_line_2_2.get('2_2')]
        cand_4 = [line_2_1, last_token_in_line_2_1.get('2_1') + first_token_in_line_3_1.get('3_1')]

        cands = None

        compound_in_bin = [fh[0] for fh in [cand_1, cand_2, cand_3, cand_4] if exists_in_bin(fh[1])]
        if compound_in_bin:
            cands = compound_in_bin[0]
        else:
            compound_makes_sense = [fh[0] for fh in [cand_1, cand_2, cand_3, cand_4] if makes_sense(fh[1])]
            if compound_makes_sense:
                cands = compound_makes_sense[0]
        return cands
    except IndexError:
        return line_1_2


def get_best_second_half_of_compound_line(line1, line2, line3):
    try:
        line_1_1 = line1.split('<newline>')[0].strip()
        line_minus_1_1 = line2.split('<newline>')[0].strip()
        line_minus_1_2 = line2.split('<newline>')[1].strip()
        line_minus_2_2 = line3.split('<newline>')[1].strip()

        first_token_in_line_1_1 = {'1_1': clean_token(line_1_1.split()[0])}
        first_token_in_line_minus_1_2 = {'minus_1_2': clean_token(line_minus_1_2.split()[0])}
        last_token_in_line_minus_1_1 = {'minus_1_1': clean_token(line_minus_1_1.split()[-1])}
        last_token_in_line_minus_2_2 = {'minus_2_2': clean_token(line_minus_2_2.split()[-1])}

        cand_1 = [line_1_1, last_token_in_line_minus_1_1.get('minus_1_1') + first_token_in_line_1_1.get('1_1')]
        cand_2 = [line_1_1, last_token_in_line_minus_2_2.get('minus_2_2') + first_token_in_line_1_1.get('1_1')]
        cand_3 = [line_minus_1_2, last_token_in_line_minus_1_1.get('minus_1_1') + first_token_in_line_minus_1_2.get('minus_1_2')]
        cand_4 = [line_minus_1_2, last_token_in_line_minus_2_2.get('minus_2_2') + first_token_in_line_minus_1_2.get('minus_1_2')]

        cands = None

        compound_in_bin = [sh[0] for sh in [cand_1, cand_2, cand_3, cand_4] if exists_in_bin(sh[1])]

        if compound_in_bin:
            cands = compound_in_bin[0]
        else:
            compound_makes_sense = [sh[0] for sh in [cand_1, cand_2, cand_3, cand_4] if makes_sense(sh[1])]
            if compound_makes_sense:
                cands = compound_makes_sense[0]
        return cands
    except IndexError:
        return line_1_1

def lookup_similar(token):
    lev_dist = 3 if len(token) > 12 else 1
    similar_cands = [tok for dist, tok in tree.find(token, n=lev_dist)]
    if len(similar_cands) == 0:
        similar_cands = [tok for dist, tok in tree.find(token.lower(), n=lev_dist)]
    if len(similar_cands) == 1:
        return similar_cands[0]
    else:
        if similar_cands:      
            most_similar = [token for token, dist in get_most_similar_from_list(token, similar_cands)]
            known_subs = get_similar_by_known_subs(token, most_similar)
            if len(known_subs) > 1:
                filtered_subs = min(get_most_similar_from_list(token, known_subs), key=lambda x: x[1])
                if filtered_subs:
                    return filtered_subs[0]
                return None
            else:
                if known_subs:
                    return known_subs[0]
                else:
                    return None
        else:
            return None


def format_token_out(token, start_punct, end_punct):
    tok_and_punct = ''
    if start_punct:
        tok_and_punct += start_punct
    tok_and_punct += token
    if end_punct:
        tok_and_punct += end_punct
    return tok_and_punct + ' '


def editable(token, index):
    return (len(token) > 3
            and not (index != 0 and len(token) < 4)
            and not token.endswith('-') 
            and not token.endswith('.'))



def sub_tokens_in_line(line):
    line_out = ''
    for (index, token) in enumerate(line.split()):
        token_out = token
        start_punct = None
        end_punct = None
        ocr_token = OCRToken(token)
        if not ocr_token.is_punct:
            if ocr_token.startswith_punct:
                start_punct = ocr_token.original_token[ocr_token.start_punct_index[0]:len(ocr_token.start_punct_index)]
            if ocr_token.endswith_punct:
                end_punct = ocr_token.original_token[ocr_token.end_punct_index[0]:len(ocr_token)]
        if any_exists_in_bin(ocr_token.clean) or not editable(token, index):
            token_out = ocr_token.clean
        else:
            similar_token = lookup_similar(ocr_token.clean)
            if similar_token:
                token_out = str(similar_token)
            else:
                token_out = ocr_token.clean
        if token.islower():
            token_out = token_out.lower()
        elif token.isupper():
            token_out = token_out.upper()
        elif token.istitle():
            token_out = token_out.title()
        line_out += format_token_out(token_out, start_punct=start_punct, end_punct=end_punct)
    return line_out.strip()


def process_lines(lines):
            """
            Iterate over all the lines in a file. The format is as such:
            First part of a sentence <newline> which continues here
            which continues here <newline> and ends here.
            and ends here. <newline> The next sentence
            The model is trained on data like this, because its input (during
            the inference phase) is very often split between lines, and the
            transformer's attention mechanism only works on running sequences.
            This helps it learn between lines.
            """
            n_lines = len(lines)
            current_index = 0
            while current_index < n_lines:
                current_line_out = ''
                curr_line_is_last_in_file = current_index+1 == n_lines

                line_is_split = len(lines[current_index].split('<newline>')) > 1
                curr_first_half = lines[current_index].split('<newline>')[0].strip()



                curr_secnd_half = None
                next_first_half = None
                next_secnd_half = None
                last_first_half = None
                last_secnd_half = None
                last_last_first_half = None
                last_last_secnd_half = None

                if line_is_split:
                    curr_secnd_half = lines[current_index].split('<newline>')[1].strip()
                    # current_line_out set as curr_secnd_half.
                    current_line_out = curr_secnd_half

                if not curr_line_is_last_in_file:
                    next_first_half = lines[current_index+1].split('<newline>')[0].strip()
                    next_line_is_split = len(lines[current_index+1].split('<newline>')) > 1
                    if next_line_is_split:
                        next_secnd_half = lines[current_index+1].split('<newline>')[1]

                try:
                    last_line = lines[current_index-1]
                    last_first_half = last_line.split('<newline>')[0].strip()
                    last_secnd_half = last_line.split('<newline>')[1].strip()
                except IndexError:
                    pass

                try:
                    last_last_line = lines[current_index-2]
                    last_last_first_half = last_last_line.split('<newline>')[0].strip()
                    last_last_secnd_half = last_last_line.split('<newline>')[1].strip()
                except IndexError:
                    pass
                # This is only for the fist line. Special case because of the indexing. Not ideal, I know.
                if current_index == 0:
                    yield curr_first_half

                else:
                    # The two candidates will most of the time be the same.
                    if curr_secnd_half == next_first_half:
                        current_line_out = curr_secnd_half
                    else:
                        if curr_secnd_half:
                            if curr_secnd_half.endswith('-'):
                                best_comp_first_half = get_best_first_half_of_compound_line(lines[current_index],
                                                                                            lines[current_index+1],
                                                                                            lines[current_index+2])
                                if best_comp_first_half:
                                    current_line_out = best_comp_first_half
                            # else:
                            #     n_good_curr = n_good_words(curr_secnd_half)
                            #     n_good_next = n_good_words(next_first_half)
                            #     if n_good_curr > n_good_next:
                            #         current_line_out = curr_secnd_half

                        # if all([last_first_half, last_last_secnd_half]):
                        #     if all([last_first_half.endswith('-'), last_last_secnd_half.endswith('-')]):
                        #         best_comp_second_half = get_best_second_half_of_compound_line(lines[current_index],
                        #                                                                       last_line,
                        #                                                                       last_last_line)
                        #         if best_comp_second_half:
                        #             current_line_out = best_comp_second_half

                        # else:
                        #     current_line_out = next_first_half

                
                if current_line_out is not None and not ((current_index + 1) == n_lines and current_line_out == ''):
                    
                    yield format_line_out(current_line_out, ocr_junk)
                current_index += 1


if __name__ == '__main__':
    out_dir = '../test_data/outputs/'
    test_file = args.file
    for line in process_lines(read_lines(test_file)):
        print(line)
        # edited = sub_tokens_in_line(line)
        # if edited:
        #     print(edited)
        # pass