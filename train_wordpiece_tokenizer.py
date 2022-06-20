import os
from glob import glob
from pathlib import Path
from shutil import rmtree
import argparse
from tokenizers import BertWordPieceTokenizer

parser = argparse.ArgumentParser()
parser.add_argument('--vocab-size')
parser.add_argument('--min-freq')
parser.add_argument('--corpus')
args = parser.parse_args()

paths = glob(f'{args.corpus}/*/**')

tokenizer = BertWordPieceTokenizer(
    clean_text=False,
    handle_chinese_chars=False,
    strip_accents=None,
    lowercase=False
)

tokenizer.train(files=paths, vocab_size=int(args.vocab_size), min_frequency=int(args.min_freq),
                limit_alphabet=1000, wordpieces_prefix='##',
                special_tokens= ['<unk>', '<pad>', '<bos>', '<eos>', '__LINE_BREAK__'])



tokenizer_name = f'{args.vocab_size}_{args.min_freq}'
full_path = f'ocr_tokenizers/{tokenizer_name}'

if not Path('ocr_tokenizers').exists():
    os.mkdir('ocr_tokenizers')

if Path(full_path).exists():
    rmtree(full_path)
os.mkdir(full_path)
tokenizer.save_model(full_path)
