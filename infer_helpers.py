from sys import path
path.append('..')
from islenska.bincompress import BinCompressed
from islenska import Bin
from utils.general_token import TextToken
from itertools import zip_longest
from globals import OCR_TOKENIZER
bin_conn = BinCompressed()
compound_lookup = Bin()


def acceptable_as_icelandic(token):
    return compound_lookup.lookup(token)[1] != []


def exists_in_bin(token=None):
    """
    Looks up whether a word exists in BÍN
    """
    return bin_conn.lookup(token) != []

def compare_tokens(sentence1, sentence2):
    ocred_tokens = sentence1.split()
    transformer_tokens = sentence2.split()
    same_length = len(ocred_tokens) == len(transformer_tokens)
    longer_sent = len(max(ocred_tokens, transformer_tokens, key=len))
    template = [0] * longer_sent
    unchanged_tokens = [(index, TextToken(word)) for index, word in enumerate(transformer_tokens) if word in ocred_tokens]
    changed_tokens = [(index, TextToken(word)) for index, word in enumerate(transformer_tokens) if word not in ocred_tokens]
    test = zip_longest(ocred_tokens, transformer_tokens)
    return [w for w in test]

if __name__ == '__main__':
    print(compare_tokens('sögn með 3. mán. fyrirvara.', 'Bögn nieð 3. iníin. i\' jrirvava.'))