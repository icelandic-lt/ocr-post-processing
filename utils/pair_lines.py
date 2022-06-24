def read_lines(file):
    with open(file, 'r', encoding='utf-8') as infile:
        lines = infile.read().splitlines()
        n_lines = len(lines)
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
        for (index, line) in enumerate(lines):
            # Checks whether the current line has two parts (which it should do
            # unless something has gone wrong).
            line_is_split = len(lines[index].split('<newline>')) > 1
            last_item = index+1 == len(lines)

            curr_first_half = lines[index].split('<newline>')[0]
            curr_secnd_half = None
            next_first_half = None
            next_secnd_half = None

            if line_is_split:
                curr_secnd_half = lines[index].split('<newline>')[1]

            # After this block has been executed, a quadruple of lines is produced
            if not last_item:
                next_first_half = lines[index+1].split('<newline>')[0]
                next_line_is_split = len(lines[index+1].split('<newline>')) > 1
                if next_line_is_split:
                    next_first_half = lines[index+1].split('<newline>')[0]
                    next_secnd_half = lines[index+1].split('<newline>')[1]

            # cand1 = next_first_half + curr_secnd_half
            # cand2 = curr_first_half + curr_secnd_half
            # cand3 = curr_secnd_half + next_first_half
            # cand4 = curr_first_half + next_first_half
            # cand5 = curr_secnd_half + next_secnd_half
            # cand = cand2
            #if index %2 == 0:
            #    yield curr_first_half
            # if not curr_secnd_half.strip() == next_first_half.strip():
            #     print(curr_first_half)
            #     print(curr_secnd_half, next_first_half)
            #     print()
            """
            Lines following a line ending with a hyphen often benefit from a longer
            preceding sequence. Not always, though. Checks which token, following
            one ending in a hyphen, works better as the last part of a hyphenated word.
            """
            if curr_first_half.endswith('-'):
                # print(curr_first_half)
                last_word_in_curr_first_half = curr_first_half.split()[-1][0:-1]
                first_word_in_curr_secnd_half = ''
                first_word_in_next_first_half = ''
                try:
                    first_word_in_curr_secnd_half = curr_secnd_half.split()[0]
                except IndexError:
                    pass
                try:
                    first_word_in_next_first_half = next_first_half.split()[0]
                except IndexError:
                    pass
                curr_secnd_cand = last_word_in_curr_first_half + first_word_in_curr_secnd_half
                next_first_cand = last_word_in_curr_first_half + first_word_in_next_first_half
                # if curr_secnd_cand != next_first_cand:
                #     print(curr_secnd_cand)
                #     print(next_first_cand)
                #print(last_word_in_curr_first_half + first_word_in_next_first_half)
                #print(last_word_in_curr_first_half)
            #print(curr_secnd_half.strip() == next_first_half.strip())
            yield curr_first_half
out_dir = '../test_data/outputs/'
test_file = f'{out_dir}/less_errors_line_pairs_937152_512_4_2048_16_6_6_0dot1_20_0_3e-05_3000_3_EPOCH_11_althydubladid_1949-2-1-bls-4.txt'

for line in read_lines(test_file):
    print(line)
    #pass
