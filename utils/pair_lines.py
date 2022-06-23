def read_lines(file):
    with open(file, 'r', encoding='utf-8') as infile:
        lines = infile.read().splitlines()
        n_lines = len(lines)
        for (index, line) in enumerate(lines):
            line_is_split = len(lines[index].split('<newline>')) > 1
            last_item = index+1 == len(lines)

            curr_first_half = lines[index].split('<newline>')[0]
            curr_secnd_half = None
            next_first_half = None
            next_secnd_half = None

            if line_is_split:
                curr_secnd_half = lines[index].split('<newline>')[1]

            if not last_item:
                next_first_half = lines[index+1].split('<newline>')[0]
                next_line_is_split = len(lines[index+1].split('<newline>')) > 1
                if next_line_is_split:
                    next_first_half = lines[index+1].split('<newline>')[0]
                    curr_secnd_half = lines[index+1].split('<newline>')[1]

            cand1 = next_first_half + curr_secnd_half
            cand2 = curr_first_half + curr_secnd_half
            cand3 = curr_secnd_half + next_first_half
            cand4 = curr_first_half + next_first_half
            cand5 = curr_secnd_half + next_secnd_half
            cand = cand5
            if index %2 == 0:
                yield cand

out_dir = '../test_data/outputs/'
test_file = f'{out_dir}/line_pairs_1067036_512_4_2048_16_5_5_0_15_0_2e-05_5000_3_EPOCH_12_althydubladid_1949-2-1-bls-4.txt'

for line in read_lines(test_file):
    print(line)
