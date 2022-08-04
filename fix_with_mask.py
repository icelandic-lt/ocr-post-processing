from transformers import pipeline
from utils.lexicon_lookup import exists_in_bin_or_old_words
from utils.format import clean_token, is_editable, extended_punctuation
from Levenshtein import distance

MODEL_PATH = '/home/steinunn/Desktop/atli/transformer_tests/IceBERT-igc'

unmasker = pipeline(
    task='fill-mask',
    model=MODEL_PATH,
    tokenizer=MODEL_PATH
)

mask_tok = unmasker.tokenizer.mask_token


def read_file(file):
    with open(file, 'r', encoding='utf-8') as infile:
        return infile.read().splitlines()


test_file = read_file('dehyphenated.txt')
for line in test_file:
    split_sent = line.split()
    for index, token in enumerate(split_sent):
        if not exists_in_bin_or_old_words(clean_token(token)) and is_editable(token, index, len(split_sent)):
            sent_without_wrong = ' '.join(split_sent[:index]) + f' {mask_tok} ' + ' '.join(split_sent[index+1:])
            unmasked = unmasker(sent_without_wrong, top_k=30)
            cands = [w['token_str'].strip() for w in unmasked if w['token_str'] not in extended_punctuation and distance(w['token_str'], token) < 3]
            print(token)
            print(cands)
            # for i in unmasked:
            #     print('ORIGINAL:', line)
            #     print('CHANGED:', i['sequence'])
            #     print('SCORE:', i['score'])
            #     print('ORIGINAL TOKEN:', word)
            #     print('CHANGED TOKEN:', i['token_str'])
            print()