import pickle
from Levenshtein import distance
from tokens import OCRToken
from argparse import ArgumentParser
from lookup import (get_similar_by_known_subs, 
                    exists_in_old_words, 
                    get_most_similar_from_list, 
                    makes_sense, exists_in_bin, 
                    n_good_words, 
                    exists_in_bin_or_old_words,
                    old_tree,
                    bin_tree,
                    lookup_similar,
                    spelling_modernized)
from format import (clean_token, 
                    format_line_out, 
                    format_token_out, 
                    is_editable)

parser = ArgumentParser()
parser.add_argument('-f', '--file')
args = parser.parse_args()



ocr_junk = ['<unk>', 'alt;', 'quot;', 'aguot;', '139;', 'a39;', '& 39;']




def read_lines(file):
    with open(file, 'r', encoding='utf-8') as infile:
        return infile.read().splitlines()



def get_best_first_half_of_compound_line(line1, line2, line3):
    """
    Returns a line ending with a hyphen whose last token can be combined
    with following line's first token.
    """
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
    """
    Return a line whose first token can be combined with the preceding line's
    last token, given that the preceding line ends with a hyphen.
    """
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



def sub_tokens_in_line(line):
    """
    Substitute tokens that are most likely erroneous and have a
    similar candidate in BÍN to which the Levenshtein distance
    is short.
    """
    line_out = ''
    line = ' '.join(line.split('—'))
    for (index, token) in enumerate(line.split()):
        token_out = token
        # Declare variables to keep track of the punctuation surrounding the token
        # A proper tokenizer doesn't work on OCRed files, because of the text's 
        # unpredictability.
        start_punct = None
        end_punct = None
        ocr_token = OCRToken(token)
        
        # Assign the punctuation to variables
        if not ocr_token.is_punct:
            if ocr_token.startswith_punct:
                start_punct = ocr_token.start_punct
            if ocr_token.endswith_punct:
                end_punct = ocr_token.end_punct

        # If the token exists in BÍN or OLD_WORDS or shouldn't be edited (see is_editable) it is simply returned as is
        if exists_in_bin_or_old_words(ocr_token.clean) or not is_editable(token, index) or ocr_token.is_punct:
            token_out = ocr_token.clean
        
        # If the token does not exist in BÍN or OLD_WORDS or should be edited (see is_editable), look for a similar
        # token, whose edit operations against the current token are known and appear more than 10 times.
        else:
            similar_token = lookup_similar(ocr_token.clean, error_frequency=10)
            if similar_token:
                if spelling_modernized(ocr_token.clean, str(similar_token)):
                    token_out = ocr_token.clean
                else:
                    token_out = str(similar_token)
            else:
                token_out = ocr_token
        
        # Restore the capitalization of token_out (inferred from the original token)
        if token.islower():
            token_out = str(token_out).lower()
        elif token.isupper():
            token_out = str(token_out).upper()
        elif token.istitle():
            token_out = str(token_out).title()
        if token_out == token:
            line_out += format_token_out(str(token_out), start_punct=None, end_punct=None)
        else:
            line_out += format_token_out(str(token_out), start_punct=start_punct, end_punct=end_punct)
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
                # This is only for the fist line. Special case because of the indexing.
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
                            else:
                                n_good_curr = n_good_words(curr_secnd_half)
                                n_good_next = n_good_words(next_first_half)
                                if n_good_curr > n_good_next:
                                    current_line_out = curr_secnd_half

                        # if all([last_first_half, last_last_secnd_half]):
                        #     if all([last_first_half.endswith('-'), last_last_secnd_half.endswith('-')]):
                        #         best_comp_second_half = get_best_second_half_of_compound_line(lines[current_index],
                        #                                                                       last_line,
                        #                                                                       last_last_line)
                        #         if best_comp_second_half:
                        #             try:
                        #                 if not last_secnd_half.split()[0] == curr_first_half.split()[0]:
                        #                     current_line_out = best_comp_second_half
                        #             except:
                        #                 pass

                        # else:
                        #     current_line_out = next_first_half

                
                if current_line_out is not None and not ((current_index + 1) == n_lines and current_line_out == ''):
                    yield format_line_out(current_line_out, ocr_junk)
                current_index += 1


if __name__ == '__main__':
    test_file = args.file
    for line in process_lines(read_lines(test_file)):
        #print(line)
        print(sub_tokens_in_line(line))
        #if edited:
        #print(edited)
        pass
