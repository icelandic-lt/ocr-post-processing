def read_lines(file):
    with open(file, 'r', encoding='utf-8') as infile:
        lines = infile.read().splitlines()
        n_lines = len(lines)
        for (index, line) in enumerate(lines):
            line = line.split('<newline>')
            a1 = lines


            first_half = lines[index].split('<newline>')[0]
            if index != 0:
                first_half_last_line = lines[index-1].split('<newline>')[1]
            if index != n_lines-1:
                second_half = lines[index].split('<newline>')[1]
            if index+2 < n_lines:
                second_half_next_line = lines[index+1].split('<newline>')[1]
            if index % 2 == 1:
                yield f'{line[0].strip()}\n{line[1].strip()}'


out_dir = '../test_data/outputs/'
test_file = f'{out_dir}/line_pairs_1067036_512_4_2048_16_5_5_0_15_0_2e-05_5000_3_EPOCH_12_althydubladid_1949-2-1-bls-4.txt'

for line in read_lines(test_file):
    print(line)
    #print(line)