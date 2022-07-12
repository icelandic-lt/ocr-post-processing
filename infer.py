from string import punctuation
from importlib import import_module
import argparse
from pathlib import Path
import torch
from tokenizer import correct_spaces
from transformer_classes import Seq2SeqTransformer
from train import (text_transform,
                   SRC_LANGUAGE,
                   TGT_LANGUAGE,
                   vocab_transform)
from globals import OCR_TOKENIZER, wordpiece_vocab, read_lines
punctuation += "–„”—«»"



def read_file(file):
    with open(file, 'r', encoding='utf-8') as infile:
        for line in infile.read().splitlines():
            yield line

parser = argparse.ArgumentParser()
parser.add_argument('--model')
parser.add_argument('--infile')
args, unknown = parser.parse_known_args()


params = import_module(f'hyperparams.{Path(args.model).stem}')


DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

#CHECKPOINT = torch.load(args.model)

MODEL = Seq2SeqTransformer(params.NUM_ENCODER_LAYERS,
                           params.NUM_DECODER_LAYERS,
                           params.EMB_SIZE,
                           params.NHEAD,
                           params.SRC_VOCAB_SIZE,
                           params.TGT_VOCAB_SIZE,
                           params.FFN_HID_DIM,
                           params.DROPOUT)



#MODEL.load_state_dict(CHECKPOINT['model_state_dict'])
MODEL.load_state_dict(torch.load(args.model, map_location=torch.device('cpu')))
MODEL.to(DEVICE)
special_symbols = ['<unk>', '<pad>', '<bos>', '<eos>']
UNK_IDX = special_symbols.index('<unk>')
PAD_IDX = special_symbols.index('<pad>')
BOS_IDX = special_symbols.index('<bos>')
EOS_IDX = special_symbols.index('<eos>')



def generate_square_subsequent_mask(sz):
    mask = (torch.triu(torch.ones((sz, sz), device=DEVICE)) == 1).transpose(0, 1)
    mask = mask.float().masked_fill(mask == 0, float('-inf')).masked_fill(mask == 1, float(0.0))
    return mask


def greedy_decode(model, src, src_mask, max_len, start_symbol):
    src = src.to(DEVICE)
    src_mask = src_mask.to(DEVICE)
    memory = model.encode(src, src_mask)
    ys = torch.ones(1, 1).fill_(start_symbol).type(torch.long).to(DEVICE)
    for _ in range(max_len-1):
        memory = memory.to(DEVICE)
        tgt_mask = (generate_square_subsequent_mask(ys.size(0))
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


def translate(model: torch.nn.Module, src_sentence: str):
    model.eval()
    src = text_transform[SRC_LANGUAGE](src_sentence).view(-1, 1)
    num_tokens = src.shape[0]
    src_mask = (torch.zeros(num_tokens, num_tokens)).type(torch.bool)
    tgt_tokens = greedy_decode(model, src, src_mask,
                               max_len=num_tokens + 5,
                               start_symbol=BOS_IDX).flatten()
    outp = (vocab_transform[TGT_LANGUAGE].lookup_tokens(list(tgt_tokens.cpu().numpy())))
    outp = ' '.join(outp).replace(' <unk> <unk> ', '')
    outp = outp.replace(' ##', '')
    outp = outp.replace(' # # ', '')
    outp = outp.replace('<bos>', '').replace('<eos>', '')
    outp = correct_spaces(outp)
    if outp.endswith(' '):
        outp = outp[:-1]
    return outp

if __name__ == '__main__':
    tokenizer_vocab_size = len(wordpiece_vocab)
    inp_file = args.infile
    inp_filename = Path(inp_file).name
    model_name = Path(args.model).stem
    outfile = f'test_data/outputs/{model_name}_{inp_filename}'
    sents = list(read_lines(inp_file, OCR_TOKENIZER))
    COUNTER = 0
    N_LINES = len(sents)
    with open(outfile, 'w', encoding='utf-8') as outf:
        for sent in sents:
            encoded_sent = ' '.join(sent)
            COUNTER += 1
            #encoded_sent = ' '.join(OCR_TOKENIZER(sent))
            print(f'[{COUNTER}/{N_LINES}]')
            #outf.write(sent + '\n')
            outf.write(str(translate(MODEL, encoded_sent)) + '\n')
