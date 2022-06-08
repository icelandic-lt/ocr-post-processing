from glob import glob
import pandas
from transformers import BertTokenizer


TEST_RUN = False

TOKENIZER = 'ocr_tokenizers/3000_3/'

if TEST_RUN:
    ORIGINAL_FILES = 'data/toy_corpus/training/original'
    CORRECTED_FILES = 'data/toy_corpus/training/corrected'
    ORIGINAL_VAL_FILES = 'data/toy_corpus/validation/original'
    CORRECTED_VAL_FILES = 'data/toy_corpus/validation/corrected'

else:
    # ORIGINAL_FILES = 'data/igc_books/original'
    # CORRECTED_FILES = 'data/igc_books/corrected'
    # ORIGINAL_VAL_FILES = 'data/parallel/50k_gold/original/'
    # CORRECTED_VAL_FILES = 'data/parallel/50k_gold/corrected/'
    ORIGINAL_FILES = 'data/combined/original'
    CORRECTED_FILES = 'data/combined/corrected'
    ORIGINAL_VAL_FILES = 'data/mid_val_data/original'
    CORRECTED_VAL_FILES = 'data/mid_val_data/corrected'


TRAINING_DATA = pandas.read_pickle('dataframes/training_data.pickle')
VALIDATION_DATA = pandas.read_pickle('dataframes/validation_data.pickle')

def get_vocab(vocab_file):
    with open(vocab_file, 'r') as vocab:
        vocabulary = vocab.read().splitlines()
    return vocabulary

def read_lines(file, tokenizer):
    with open(file, 'r', encoding='utf-8') as infile:
        for line in infile:
            yield tokenizer(line)

def read_files(path, tokenizer):
    all_files = glob(f'{path}/*')
    for file in all_files:
        for line in read_lines(file, tokenizer=tokenizer):
            yield line

bert_tokenizer = BertTokenizer.from_pretrained(
                    TOKENIZER,
                    strip_accents=False,
                    do_lower_case=False,
                    clean_text=False,
                    special_tokens= ['<unk>', '<pad>', '<bos>', '<eos>'])

def tokenize(sequence):
    tokenized = bert_tokenizer(sequence).input_ids
    tokenized = [0 if id is None else id for id in tokenized]
    if tokenized != []:
        return [wordpiece_vocab[i] for i in tokenized[1:-1]]
    return []

wordpiece_vocab = get_vocab(f'{TOKENIZER}/vocab.txt')
OCR_TOKENIZER = tokenize
