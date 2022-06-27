from islenska.bincompress import BinCompressed
from islenska import Bin
from string import punctuation
punctuation += "–„”—«»"

bin_conn = BinCompressed()
isl_lookup = Bin()

def makes_sense(token):
    return isl_lookup.lookup(token)[1] != []


def format_newline_line(line):
    first_half = line.split('<newline>')[0].strip()
    second_half = line.split('<newline>')[1].strip()
    return f'{first_half}\n{second_half}'


def read_lines(file):
    with open(file, 'r', encoding='utf-8') as infile:
        return infile.read().splitlines()

def clean_token(token):
    return token.strip(punctuation)

def n_good_words(line):
    sensemaking_words = [word for word in line.split() if makes_sense(clean_token(word))]
    return (len(sensemaking_words))

def fix_guillemets(line):
    return line.replace('» ', ' »').replace(' «', '« ').strip()


def get_best_first_half_of_compound_line(line1, line2, line3):
    line_1_1 = line1.split('<newline>')[0].strip()
    line_1_2 = line1.split('<newline>')[1].strip()
    line_2_1 = line2.split('<newline>')[0].strip()
    line_2_2 = line2.split('<newline>')[1].strip()
    line_3_1 = line3.split('<newline>')[0].strip()
    line_3_2 = line3.split('<newline>')[1].strip()

    last_token_in_line_1_2 = {'1_2': clean_token(line_1_2.split()[-1])}
    last_token_in_line_2_1 = {'2_1': clean_token(line_2_1.split()[-1])}
    first_token_in_line_2_2 = {'2_2': clean_token(line_2_2.split()[0])}
    first_token_in_line_3_1 = {'3_1': clean_token(line_3_1.split()[0])}

    cand_1 = [line_1_2, last_token_in_line_1_2.get('1_2') + first_token_in_line_2_2.get('2_2')]
    cand_2 = [line_1_2, last_token_in_line_1_2.get('1_2') + first_token_in_line_3_1.get('3_1')]
    cand_3 = [line_2_1, last_token_in_line_2_1.get('2_1') + first_token_in_line_2_2.get('2_2')]
    cand_4 = [line_2_1, last_token_in_line_2_1.get('2_1') + first_token_in_line_3_1.get('3_1')]

    good_first_half = [fh[0] for fh in [cand_1, cand_2, cand_3, cand_4] if makes_sense(fh[1])][0]
    return good_first_half


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


                if line_is_split:
                    curr_secnd_half = lines[current_index].split('<newline>')[1].strip()
                    # current_line_out set as curr_secnd_half.
                    current_line_out = curr_secnd_half

                if not curr_line_is_last_in_file:
                    next_first_half = lines[current_index+1].split('<newline>')[0].strip()
                    next_line_is_split = len(lines[current_index+1].split('<newline>')) > 1
                    if next_line_is_split:
                        next_secnd_half = lines[current_index+1].split('<newline>')[1]

                # This is only for the fist line. Special case because of my indexing. Not ideal, I know.
                if current_index == 0:
                    yield curr_first_half

                else:
                    # The two candidates will most of the time be the same.
                    if curr_secnd_half == next_first_half:
                        current_line_out = curr_secnd_half
                    else:
                        if curr_secnd_half.endswith('-'):
                            current_line_out = get_best_first_half_of_compound_line(lines[current_index],
                                                                                    lines[current_index+1],
                                                                                    lines[current_index+2])
                        else:
                            n_good_curr = n_good_words(curr_secnd_half)
                            n_good_next = n_good_words(next_first_half)
                            if n_good_curr > n_good_next:
                                # print(curr_secnd_half.split(), next_first_half.split())
                                current_line_out = curr_secnd_half
                            else:
                                current_line_out = next_first_half


                if current_line_out is not None and not ((current_index + 1) == n_lines and current_line_out == ''):
                    yield current_line_out
                current_index += 1



















                    # If they're not the same:
                    # else:
                        # if curr_secnd_half:
                        #     if curr_secnd_half.endswith('-'):
                                # Remove trailing hyphen from the last word in current line
                                # curr_secnd_half_last_token = curr_secnd_half.split()[-1].rstrip('-')
                                # first_word_in_curr_secnd_half = ''
                                # first_word_in_next_first_half = ''
                    #
                    #         try:
                    #             first_word_in_curr_secnd_half = curr_secnd_half.split()[0]
                    #         except IndexError:
                    #             pass
                    #         try:
                    #             first_word_in_next_first_half = next_first_half.split()[0]
                    #         except IndexError:
                    #             pass
                    #
                    #         curr_hyphen_cand = last_word_in_curr_first_half + first_word_in_curr_secnd_half
                    #         next_hyphen_cand = last_word_in_curr_first_half + first_word_in_next_first_half
                    #
                    #         curr_hyphen_cand_good = makes_sense(curr_hyphen_cand.strip(punctuation))
                    #         next_hyphen_cand_good = makes_sense(next_hyphen_cand.strip(punctuation))










            # for index in range(n_lines):
            #     current_line_out = ''
            #     # Checks whether the current line has two parts (which it should do
            #     # unless something has gone terribly wrong).
            #     line_is_split = len(lines[index].split('<newline>')) > 1
            #     last_line_in_file = index+1 == len(lines)
            #
            #     curr_first_half = lines[index].split('<newline>')[0]
            #     curr_secnd_half = None
            #     next_first_half = None
            #     next_secnd_half = None
            #
            #     which_lines = None
            #
            #     if line_is_split:
            #         curr_secnd_half = lines[index].split('<newline>')[1]
            #
            #     # After this block has been executed, a quadruple of lines is produced
            #     if not last_line_in_file:
            #         next_first_half = lines[index+1].split('<newline>')[0]
            #         next_line_is_split = len(lines[index+1].split('<newline>')) > 1
            #         if next_line_is_split:
            #             next_first_half = lines[index+1].split('<newline>')[0]
            #             next_secnd_half = lines[index+1].split('<newline>')[1]
            #
            #
            #     # default_lines_case = all([curr_first_half, curr_secnd_half])
            #     # alternate_lines_case = all([curr_secnd_half, next_first_half])
            #     #
            #     # cand1 = curr_first_half + curr_secnd_half if default_lines_case else None
            #     # cand2 = curr_first_half + curr_secnd_half if alternate_lines_case else None
            #
            #     """
            #     Lines following a line ending with a hyphen often benefit from a longer
            #     preceding sequence. Not always, though. Checks which token, following
            #     one ending in a hyphen, works better as the last part of a hyphenated word.
            #     """
            #     if curr_first_half.endswith('-'):
            #         # Remove trailing hyphen from the last word in current line
            #         last_word_in_curr_first_half = curr_first_half.split()[-1].rstrip('-')
            #         first_word_in_curr_secnd_half = ''
            #         first_word_in_next_first_half = ''
            #
            #         try:
            #             first_word_in_curr_secnd_half = curr_secnd_half.split()[0]
            #         except IndexError:
            #             pass
            #         try:
            #             first_word_in_next_first_half = next_first_half.split()[0]
            #         except IndexError:
            #             pass
            #
            #         curr_hyphen_cand = last_word_in_curr_first_half + first_word_in_curr_secnd_half
            #         next_hyphen_cand = last_word_in_curr_first_half + first_word_in_next_first_half
            #
            #         curr_hyphen_cand_good = makes_sense(curr_hyphen_cand.strip(punctuation))
            #         next_hyphen_cand_good = makes_sense(next_hyphen_cand.strip(punctuation))
            #     if index % 2 == 0:
            #         if not last_line_in_file:
            #             yield format_newline_line(lines[index])
            #         else:
            #             yield lines[index].strip()
            #     current_line_out = curr_first_half


if __name__ == '__main__':
    out_dir = '../test_data/outputs/'
    test_file = f'{out_dir}less_errors_line_pairs_937152_256_4_1024_16_6_6_0dot1_40_0_3e-05_3000_3_EPOCH_36_althydubladid_1949-2-1-bls-4.txt'
    #test_file = f'{out_dir}less_errors_line_pairs_937152_256_4_1024_16_6_6_0dot1_40_0_3e-05_3000_3_EPOCH_36_ulfur.txt'
    for line in process_lines(read_lines(test_file)):
        print(line)
        #print(count_sensemaking_words(current_line_out))
        pass
