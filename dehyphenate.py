from utils.lexicon_lookup import exists_in_bin_or_old_words
from utils.format import clean_token
from tokenizer import correct_spaces, split_into_sentences


def read_file(file):
    with open(file, 'r', encoding='utf-8') as infile:
        return infile.read()


def remove_hyphens(sent):
    sent_out = ''
    for token in sent.split():
        if '-' in token:
            tok_no_hyph = token.replace('-', '')
            if exists_in_bin_or_old_words(tok_no_hyph):
                sent_out += f'{tok_no_hyph} '
        else:
            sent_out += f'{token} '
    return sent_out.strip()

if __name__ == '__main__':
    filename = 'test_data/outputs/937152_512_4_2048_24_5_5_0dot1_40_0_3e-05_3000_3_EPOCH_13_test.txt'
    file = read_file(filename)
    for i in split_into_sentences(file):
        cs = correct_spaces(i)
        edit_hyphens = remove_hyphens(cs)
        print(edit_hyphens)