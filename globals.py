from glob import glob
from sys import modules
import pandas
from transformers import BertTokenizer
from pathlib import Path

calling_module = Path(modules['__main__'].__file__).stem

TOKENIZER_INFO = '3000_3'

TOKENIZER = f'ocr_tokenizers/{TOKENIZER_INFO}/'

ORIGINAL_FILES = 'data/1m/training/original'
CORRECTED_FILES = 'data/1m/training/corrected'
ORIGINAL_VAL_FILES = 'data/1m/validation/original'
CORRECTED_VAL_FILES = 'data/1m/validation/corrected'


def get_vocab(vocab_file):
    with open(vocab_file, 'r') as vocab:
        vocabulary = vocab.read().splitlines()
    return vocabulary

def read_lines(file, tokenizer):
    with open(file, 'r', encoding='utf-8') as infile:
        infile = infile.readlines()
        for (index, line) in enumerate(infile):
            if index+1 < len(infile):
                line1 = infile[index].strip()
                line2 = infile[index+1].strip()
                combined = f'{line1}<newline>{line2}'
            else:
                combined = line
            yield tokenizer(combined)


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
                    special_tokens= ['<unk>', '<pad>', '<bos>', '<eos>'],
                    add_special_tokens=True)

bert_tokenizer.add_special_tokens({'additional_special_tokens': ['<newline>']})

def tokenize(sequence):
    tokenized = bert_tokenizer(sequence).input_ids
    tokenized = [0 if id is None else id for id in tokenized]
    if tokenized != []:
        return [wordpiece_vocab[i] for i in tokenized[1:-1]]
    return []

wordpiece_vocab = get_vocab(f'{TOKENIZER}/vocab.txt')
OCR_TOKENIZER = tokenize
