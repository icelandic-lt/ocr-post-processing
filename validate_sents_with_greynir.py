from reynir import Greynir

greynir = Greynir()

def read_lines(file):
    with open(file, 'r', encoding='utf-8') as infile:
        return infile.read().splitlines()


lines = read_lines('test_data/outputs/937152_512_4_2048_24_5_5_0dot1_40_0_3e-05_3000_3_EPOCH_13_test.txt')

counter = 0
lines_counter = 0
for i in lines:
    lines_counter += 1
    print(f'[{lines_counter}/{len(lines)}]')
    parsed = greynir.parse_single(i)
    try:
        x = parsed.tree.view
        counter += 1
    except AttributeError:
        pass


print(f'[{counter}/{len(lines)}]')