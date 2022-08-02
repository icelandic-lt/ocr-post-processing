from utils.lexicon_lookup import exists_in_bin_or_old_words
from utils.format import clean_token
from tokenizer import correct_spaces, split_into_sentences


def read_file(file):
    with open(file, 'r', encoding='utf-8') as infile:
        return infile.read().replace('. ', '.\n').splitlines()

def merge_sentences(lines):
    last_index = 0
    sents = 0
    for index, line in (enumerate(lines)):
        if line.endswith('.'):
            if sents == 0:
                sent = lines[last_index:index+1]
            else:
                sent = lines[last_index+1:index+1]
            last_index = index
            sents += 1
            if sent:
                yield sent

def merge_words(sents):
    sents = merge_sentences(sents)
    for sent in sents:
        sent_out = ''
        # [(0, 'Leigjandinn: Eruð þér frá vitinu, herra'), (1, 'minn, jeg að flytja undir eins, áður en jeg hefi')
        enumerated_sent_parts = enumerate(sent)
        for sent_part_index, sent_part in enumerated_sent_parts:
            split_sent_part = sent_part.split()
            len_sent_part = len(split_sent_part)
            # [(0, 'Leigjandinn:'), (1, 'Eruð'), (2, 'þér'), (3, 'frá'), (4, 'vitinu,'), (5, 'herra')]
            enumerated_tokens = enumerate(split_sent_part)
            # Iterate over all tokens in split sent
            for token_index, token in enumerated_tokens:
                if not token_index == len_sent_part-1:
                    sent_out += f'{token} '
                else:
                    last_token_exists = exists_in_bin_or_old_words(clean_token(token)) and not token.endswith('-')
                    if not last_token_exists:
                        try:
                            if token.endswith('-'):
                                token = token[:-1]
                            out_cand = token + sent[sent_part_index+1].split()[0]
                            if exists_in_bin_or_old_words(clean_token(out_cand)):
                                sent_out += f'{out_cand} '
                                sent[sent_part_index+1] = ' '.join(sent[sent_part_index+1].split()[1:])
                            else:
                                sent_out += f'{token} '
                        except:
                            pass
                    else:
                        sent_out += f'{token} '
        yield sent_out

def merge_and_format(text):
    sentence_string = ' '.join([sent for sent in merge_words(text)])
    sentences = split_into_sentences(sentence_string)
    for i in sentences:
        yield correct_spaces(i)

if __name__ == '__main__':
    file = read_file('test_data/outputs/937152_512_4_2048_24_5_5_0dot1_40_0_3e-05_3000_3_EPOCH_13_ulfur.txt')
    file = read_file('test_data/original/short_test.txt')
    sents = merge_and_format(file)
    for i in sents:
        print(i)
