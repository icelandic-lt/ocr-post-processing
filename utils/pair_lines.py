from argparse import ArgumentParser
from tokenizer import correct_spaces
from lookup import (makes_sense, exists_in_bin, exists_in_bin_or_old_words, 
                    n_good_words,
                    sub_tokens_in_line)
from format import (clean_token, 
                    format_line_out)

parser = ArgumentParser()
parser.add_argument('-f', '--file')
parser.add_argument('-l', '--include-lexicon-lookup', action='store_true')
args = parser.parse_args()



ocr_junk = ['<unk>', 'alt;', 'quot;', 'aguot;', '139;', 'a39;', '& 39;', 'a 39;']




def read_lines(file):
    with open(file, 'r', encoding='utf-8') as infile:
        return infile.read().splitlines()



# def get_best_first_half_of_compound_line(line1, line2, line3):
#     """
#     Returns a line ending with a hyphen whose last token can be combined
#     with following line's first token.
#     """
#     try:
#         # line_1_1 = line1.split('<newline>')[0].strip()
#         line_1_2 = line1.split('<newline>')[1].strip()
#         line_2_1 = line2.split('<newline>')[0].strip()
#         line_2_2 = line2.split('<newline>')[1].strip()
#         line_3_1 = line3.split('<newline>')[0].strip()
#         # line_3_2 = line3.split('<newline>')[1].strip()
#         last_token_in_line_1_2 = {'1_2': clean_token(line_1_2.split()[-1])}
#         last_token_in_line_2_1 = {'2_1': clean_token(line_2_1.split()[-1])}
#         first_token_in_line_2_2 = {'2_2': clean_token(line_2_2.split()[0])}
#         first_token_in_line_3_1 = {'3_1': clean_token(line_3_1.split()[0])}
#         cand_1 = [line_1_2, last_token_in_line_1_2.get('1_2') + first_token_in_line_2_2.get('2_2')]
#         cand_2 = [line_1_2, last_token_in_line_1_2.get('1_2') + first_token_in_line_3_1.get('3_1')]
#         cand_3 = [line_2_1, last_token_in_line_2_1.get('2_1') + first_token_in_line_2_2.get('2_2')]
#         cand_4 = [line_2_1, last_token_in_line_2_1.get('2_1') + first_token_in_line_3_1.get('3_1')]

#         cands = None

#         compound_in_bin = [fh[0] for fh in [cand_1, cand_2, cand_3, cand_4] if exists_in_bin(fh[1])]
#         if compound_in_bin:
#             cands = compound_in_bin[0]
#         else:
#             compound_makes_sense = [fh[0] for fh in [cand_1, cand_2, cand_3, cand_4] if makes_sense(fh[1])]
#             if compound_makes_sense:
#                 cands = compound_makes_sense[0]
#         return cands
#     except IndexError:
#         return line_1_2


# def get_best_second_half_of_compound_line(line1, line2, line3):
#     """
#     Return a line whose first token can be combined with the preceding line's
#     last token, given that the preceding line ends with a hyphen.
#     """
#     try:
#         line_1_1 = line1.split('<newline>')[0].strip()
#         line_minus_1_1 = line2.split('<newline>')[0].strip()
#         line_minus_1_2 = line2.split('<newline>')[1].strip()
#         line_minus_2_2 = line3.split('<newline>')[1].strip()

#         first_token_in_line_1_1 = {'1_1': clean_token(line_1_1.split()[0])}
#         first_token_in_line_minus_1_2 = {'minus_1_2': clean_token(line_minus_1_2.split()[0])}
#         last_token_in_line_minus_1_1 = {'minus_1_1': clean_token(line_minus_1_1.split()[-1])}
#         last_token_in_line_minus_2_2 = {'minus_2_2': clean_token(line_minus_2_2.split()[-1])}

#         cand_1 = [line_1_1, last_token_in_line_minus_1_1.get('minus_1_1') + first_token_in_line_1_1.get('1_1')]
#         cand_2 = [line_1_1, last_token_in_line_minus_2_2.get('minus_2_2') + first_token_in_line_1_1.get('1_1')]
#         cand_3 = [line_minus_1_2, last_token_in_line_minus_1_1.get('minus_1_1') + first_token_in_line_minus_1_2.get('minus_1_2')]
#         cand_4 = [line_minus_1_2, last_token_in_line_minus_2_2.get('minus_2_2') + first_token_in_line_minus_1_2.get('minus_1_2')]

#         cands = None

#         compound_in_bin = [sh[0] for sh in [cand_1, cand_2, cand_3, cand_4] if exists_in_bin(sh[1])]

#         if compound_in_bin:
#             cands = compound_in_bin[0]
#         else:
#             compound_makes_sense = [sh[0] for sh in [cand_1, cand_2, cand_3, cand_4] if makes_sense(sh[1])]
#             if compound_makes_sense:
#                 cands = compound_makes_sense[0]
#         return cands
#     except IndexError:
#         return line_1_1


def process_lines(original_lines, corrected_lines):
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
            n_lines = len(corrected_lines)
            current_index = 0
            while current_index < n_lines:
                current_line_out = ''
                curr_line_is_last_in_file = current_index+1 == n_lines

                line_is_split = len(corrected_lines[current_index].split('<newline>')) > 1
                curr_first_half = corrected_lines[current_index].split('<newline>')[0].strip()


                curr_secnd_half = None
                next_first_half = None
                
                next_secnd_half = None
                last_first_half = None
                last_secnd_half = None
                last_last_first_half = None
                last_last_secnd_half = None
                next_next_first_half = None
                next_next_secnd_half = None

                if line_is_split:
                    curr_secnd_half = corrected_lines[current_index].split('<newline>')[1].strip()
                    # current_line_out set as curr_secnd_half.
                    current_line_out = curr_secnd_half
                else:
                    current_Line_out = curr_first_half
                if not curr_line_is_last_in_file:
                    next_first_half = corrected_lines[current_index+1].split('<newline>')[0].strip()
                    next_line_is_split = len(corrected_lines[current_index+1].split('<newline>')) > 1
                    if next_line_is_split:
                        next_secnd_half = corrected_lines[current_index+1].split('<newline>')[1]
                try:
                    last_line = corrected_lines[current_index-1]
                    last_first_half = last_line.split('<newline>')[0].strip()
                    last_secnd_half = last_line.split('<newline>')[1].strip()
                except IndexError:
                    pass
                try:
                    last_last_line = corrected_lines[current_index-2]
                    last_last_first_half = last_last_line.split('<newline>')[0].strip()
                    last_last_secnd_half = last_last_line.split('<newline>')[1].strip()
                except IndexError:
                    pass
                try: 
                    next_next_line = corrected_lines[current_index+2]
                    next_next_first_half = next_next_line.split('<newline>')[0].strip()
                    next_next_secnd_half = next_next_line.split('<newline>')[1].strip()
                except IndexError:
                    pass
                # This is only for the fist line. Special case because of the indexing.
                if current_index == 0:
                    yield curr_first_half

                else:
                    if all([curr_secnd_half, next_first_half, last_secnd_half]):
                        first_word_in_current_second_half = curr_secnd_half.split()[0]
                        first_word_in_next_first_half = next_first_half.split()[0]
                        last_word_in_last_second_half = last_secnd_half.split()[-1]
                        if last_word_in_last_second_half.endswith('-'):
                            last_word_in_last_second_half = last_word_in_last_second_half[:-1]
                        combined_curr_secnd_last_secnd = last_word_in_last_second_half + first_word_in_current_second_half
                        combined_next_first_last_secnd = last_word_in_last_second_half + first_word_in_next_first_half
                        if combined_curr_secnd_last_secnd != combined_next_first_last_secnd:
                            if exists_in_bin_or_old_words(combined_next_first_last_secnd):
                                current_line_out = next_first_half
                            else:
                                current_line_out = curr_secnd_half
                    if all([curr_secnd_half, next_first_half, next_secnd_half]):
                        last_word_in_curr_secnd_half = curr_secnd_half.split()[-1]
                        last_word_in_next_first_half = next_first_half.split()[-1] 
                        first_word_in_next_secnd_half = next_secnd_half.split()[0]                    
                        if last_word_in_curr_secnd_half.endswith('-'):
                            last_word_in_curr_secnd_half = last_word_in_curr_secnd_half[:-1]
                        if last_word_in_next_first_half.endswith('-'):
                            last_word_in_next_first_half = last_word_in_next_first_half[:-1]
                        combined_curr_secnd_next_secnd = last_word_in_curr_secnd_half + first_word_in_next_secnd_half
                        combined_next_first_next_secnd = last_word_in_next_first_half + first_word_in_next_secnd_half
                        if combined_curr_secnd_next_secnd != combined_next_first_next_secnd:
                            if exists_in_bin_or_old_words(combined_next_first_next_secnd):
                                current_line_out = next_first_half
                            else:
                                current_line_out = curr_secnd_half                            
                if current_line_out is not None and not ((current_index + 1) == n_lines and current_line_out == ''):
                    yield format_line_out(current_line_out, ocr_junk)
                current_index += 1  
                    
                



if __name__ == '__main__':
    test_file = args.file
    for line in process_lines(None, read_lines(test_file)):
        if args.include_lexicon_lookup:
            print(sub_tokens_in_line(line))
        else:
            print(line)
            pass
