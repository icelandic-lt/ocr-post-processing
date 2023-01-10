from string import punctuation
from importlib import import_module
import argparse
from pathlib import Path
import torch
from tokenizer import correct_spaces
from transformer_classes import Seq2SeqTransformer
from train import (text_transform,
                   vocab_transform,
                   SRC_LANGUAGE,
                   TGT_LANGUAGE)
from globals import OCR_TOKENIZER, wordpiece_vocab, read_lines
from utils.pair_lines import process_torch_lines
from utils.lexicon_lookup import n_good_words, sub_tokens_in_line, makes_sense, exists_in_bin_or_old_words
from utils.format import clean_token, clean_token, extended_punctuation
from tqdm import tqdm
from fairseq.models.transformer import TransformerModel
from dehyphenate import merge_and_format
from transformers import pipeline
from transformers.pipelines.pt_utils import KeyDataset
from datasets import load_dataset
punctuation += "–„”—«»"



def read_file(file):
    with open(file, 'r', encoding='utf-8') as infile:
        for line in infile.read().splitlines():
            yield line

parser = argparse.ArgumentParser()
parser.add_argument('--model')
parser.add_argument('--infile')
parser.add_argument('-l', '--include-lexicon-lookup', action='store_true')
parser.add_argument('-f', '--fairseq-only', action='store_true')
parser.add_argument('-t', '--torch-only', action='store_true')
parser.add_argument('-m', '--merge-lines', action='store_true')
parser.add_argument('-b', '--byt5-only', action='store_true')
args, unknown = parser.parse_known_args()


BYT5_MODEL_PATH = f'best_byt5_models/byt5-is-ocr-post-processing-old-texts'
BYT5_CORRECTION = pipeline('text2text-generation', model=BYT5_MODEL_PATH, tokenizer=BYT5_MODEL_PATH, num_return_sequences=1, device=0)

params = import_module(f'hyperparams.{Path(args.model).stem}')


DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
CHECKPOINT = torch.load(args.model, map_location=torch.device('cuda'))
MODEL = Seq2SeqTransformer(params.NUM_ENCODER_LAYERS,
                           params.NUM_DECODER_LAYERS,
                           params.EMB_SIZE,
                           params.NHEAD,
                           params.SRC_VOCAB_SIZE,
                           params.TGT_VOCAB_SIZE,
                           params.FFN_HID_DIM,
                           params.DROPOUT)


try:
    MODEL.load_state_dict(CHECKPOINT['model_state_dict'])
except KeyError:
    MODEL.load_state_dict(torch.load(args.model, map_location=torch.device('cpu')))
MODEL.to(DEVICE)


special_symbols = ['<unk>', '<pad>', '<bos>', '<eos>']
UNK_IDX = special_symbols.index('<unk>')
PAD_IDX = special_symbols.index('<pad>')
BOS_IDX = special_symbols.index('<bos>')
EOS_IDX = special_symbols.index('<eos>')



# This function comes from PyTorch: https://github.com/pytorch/tutorials/blob/master/beginner_source/translation_transformer.py
def greedy_decode(model, src, src_mask, max_len, start_symbol):
    src = src.to(DEVICE)
    src_mask = src_mask.to(DEVICE)
    memory = model.encode(src, src_mask)
    ys = torch.ones(1, 1).fill_(start_symbol).type(torch.long).to(DEVICE)
    for _ in range(max_len-1):
        memory = memory.to(DEVICE)
        tgt_mask = (torch.nn.Transformer.generate_square_subsequent_mask(ys.size(0))
                    .type(torch.bool)).to(DEVICE)
        out = model.decode(ys, memory, tgt_mask)
        out = out.transpose(0, 1)
        prob = model.generator(out[:, -1])
        _, next_word = torch.max(prob, dim=1)
        next_word = next_word.item()
        ys = torch.cat([ys,
                        torch.ones(1, 1).type_as(src.data).fill_(next_word)], dim=0)
        if next_word == EOS_IDX:
            break
    return ys


def detokenize(line):
    line = ' '.join(line).replace(' <unk> <unk> ', '')
    line = line.replace(' ##', '')
    line = line.replace(' # # ', '')
    line = line.replace('<bos>', '').replace('<eos>', '')
    line = correct_spaces(line)
    return line


# This function is a modified version of the translate function found here:
# https://github.com/pytorch/tutorials/blob/master/beginner_source/translation_transformer.py
def translate(model: torch.nn.Module, src_sentence: str):
    model.eval()
    src = text_transform[SRC_LANGUAGE](src_sentence).view(-1, 1)
    num_tokens = src.shape[0]
    src_mask = (torch.zeros(num_tokens, num_tokens)).type(torch.bool)
    tgt_tokens = greedy_decode(model, src, src_mask,
                               max_len=num_tokens + 5,
                               start_symbol=BOS_IDX).flatten()
    outp = vocab_transform[TGT_LANGUAGE].lookup_tokens(list(tgt_tokens.cpu().numpy()))
    return outp


def transform_file(file):
    sents = list(read_lines(inp_file, OCR_TOKENIZER))
    for sent in tqdm(sents, desc='[1/3]'):
        str_sent = ' '.join(sent)
        transformed_sent = detokenize(translate(MODEL, str_sent))
        yield transformed_sent


def fairseq_transform_file(file):
    model = TransformerModel.from_pretrained('frsq/models/',
                                             checkpoint_file='checkpoint_best.pt',
                                             data_name_or_path='frsq/data/data-bin.3000',
                                             bpe='sentencepiece',
                                             sentencepiece_model='frsq/data/sentencepiece/data/sentencepiece_3000.bpe.model')
    lines = list(read_file(file))
    transformed = tqdm(model.translate(lines))
    for transformed_sent in transformed:
    #for line in tqdm(list(read_file(file)), desc='[2/3]'):
        #transformed_sent = model.translate(line)
        yield transformed_sent

def byt5_transform_file(file):
    path = f'{Path(args.infile).parents[0]}/'
    filename = Path(args.infile).name
    dataset = load_dataset(path, data_files=filename)
    lines = dataset['train']
    file_length = len(lines)
    for line in tqdm(BYT5_CORRECTION(KeyDataset(lines, 'text'), max_length=512, batch_size=32), total=file_length):
        yield line[0]['generated_text']


if __name__ == '__main__':
    out_lines = []
    tokenizer_vocab_size = len(wordpiece_vocab)
    inp_file = args.infile
    inp_filename = Path(inp_file).name
    model_name = Path(args.model).stem
    outfile = f'test_data/outputs/{model_name}_{inp_filename}'
    one_model = None
    if args.torch_only:
        one_model = 'torch_only'
    elif args.fairseq_only:
        one_model = 'fairseq_only'
    elif args.byt5_only:
        one_model = 'byt5_only'
    outfile = f'test_data/outputs/{model_name}_{inp_filename}'
    if one_model:
        outfile = f'test_data/outputs/{model_name}_{one_model}_{inp_filename}'
    if args.include_lexicon_lookup:
        outfile = f'test_data/outputs/{model_name}_{one_model}_lexicon_lookup_{inp_filename}'
    #outfile = 'all_models.txt'
    sents = list(read_lines(inp_file, OCR_TOKENIZER))
    COUNTER = 0
    N_LINES = len(sents)
    original_file = read_file(inp_file)

    if args.torch_only:
        torch_file = list(transform_file(inp_file))
        torch_file = process_torch_lines(torch_file)
        for line in torch_file:
            out_lines.append(line)
    elif args.fairseq_only:
        frsq_file = list(fairseq_transform_file(inp_file))
        for line in frsq_file:
            out_lines.append(line)
    elif args.byt5_only:
        byt5_file = list(byt5_transform_file(args.infile))
        for line in byt5_file:
            out_lines.append(line)
    else:
        torch_file = list(transform_file(inp_file))
        frsq_file = list(fairseq_transform_file(inp_file))
        byt5_file = list (byt5_transform_file(args.infile))
        for original_line, torch_line, frsq_line, byt5_line in tqdm(zip(original_file, process_torch_lines(torch_file), frsq_file, byt5_file), desc='[3/3]'):
            line_out = ''
            torch_tokens = torch_line.split()
            frsq_tokens = frsq_line.split()
            byt5_tokens = byt5_line.split()
            if len(torch_tokens) == len(frsq_tokens) == len(byt5_tokens) and torch_tokens[-1] == frsq_tokens[-1] == byt5_tokens[-1]:
                tmp_line_out = ''
                for (index, (torch_tok, frqs_tok, byt5_tok)) in enumerate(zip(torch_tokens, frsq_tokens, byt5_tokens)):
                    if index in [0, len(torch_tokens)]:
                        tmp_line_out += f'{torch_tok} '
                    else:
                        if exists_in_bin_or_old_words(clean_token(torch_tok)):
                            tmp_line_out += f'{torch_tok} '
                        elif exists_in_bin_or_old_words(clean_token(frqs_tok)):
                            tmp_line_out += f'{frqs_tok} '
                        else:
                            tmp_line_out += f'{byt5_tok}'
                try:
                    transformed_n_good_words = n_good_words(torch_line)
                except ZeroDivisionError:
                    transformed_n_good_words = 0

                try:
                    frsq_n_good_words = n_good_words(frsq_line)
                except ZeroDivisionError:
                    frsq_n_good_words = 0

                try:
                    byt5_n_good_words = n_good_words(byt5_line)
                except ZeroDivisionError:
                    byt5_n_good_words = 0

                try:
                    modified_n_good_words = n_good_words(tmp_line_out)
                except ZeroDivisionError:
                    modified_n_good_words = 0

                best_line = max([(tmp_line_out, modified_n_good_words), (torch_line, transformed_n_good_words), (frsq_line, frsq_n_good_words), (byt5_line, byt5_n_good_words)], key=lambda x: x[1])
                line_out = best_line[0]
            else:
                line_out = torch_line
            out_lines.append(line_out.rstrip())
    if args.merge_lines:
        out_lines_string = '\n'.join([l for l in out_lines]).replace('. ', '.\n').splitlines()
        out_lines = merge_and_format(out_lines_string)
    with open(outfile, 'w', encoding='utf-8') as outf:
        for line_out in out_lines:
            if args.include_lexicon_lookup:
                line_out = sub_tokens_in_line(line_out).rstrip()
            else:
                line_out = line_out.rstrip()
            outf.write(line_out + '\n')
