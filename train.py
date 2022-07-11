from pathlib import Path
from timeit import default_timer as timer
from datetime import datetime
import argparse
from typing import List
import pandas as pd
import torch.nn as nn
from torch import device, cuda
from torch.optim import Adam
from torch.utils.data import DataLoader
import torch
from torch.nn.utils.rnn import pad_sequence
from transformers import BertTokenizer
#from torch.optim.lr_scheduler import StepLR
import params
from ocr_dataset import OCRDataset
from transformer_classes import Seq2SeqTransformer
from glob import glob
from tqdm import tqdm

from globals import (ORIGINAL_FILES,
                     CORRECTED_FILES,
                     OCR_TOKENIZER,
                     wordpiece_vocab,
                     TRAINING_DATA,
                     VALIDATION_DATA,
                     TOKENIZER)


#parser = argparse.ArgumentParser()
#parser.add_argument('--tokenizer')
#args, unknown = parser.parse_known_args()

DEVICE = device('cuda' if cuda.is_available() else 'cpu')
SRC_LANGUAGE = 'original'
TGT_LANGUAGE = 'corrected'
SPECIAL_SYMBOLS = ['<unk>', '<pad>', '<bos>', '<eos>']
UNK_IDX = SPECIAL_SYMBOLS.index('<unk>')
PAD_IDX = SPECIAL_SYMBOLS.index('<pad>')
BOS_IDX = SPECIAL_SYMBOLS.index('<bos>')
EOS_IDX = SPECIAL_SYMBOLS.index('<eos>')

TRAINING_DATASET = OCRDataset(df=TRAINING_DATA, source_column=SRC_LANGUAGE, target_column=TGT_LANGUAGE)
VALIDATION_DATASET = OCRDataset(df=VALIDATION_DATA, source_column=SRC_LANGUAGE, target_column=TGT_LANGUAGE)


token_transform = {}
vocab_transform = {}

# The tokenizer function (the one that returns a string) set to token transform dict
token_transform[SRC_LANGUAGE] = OCR_TOKENIZER
token_transform[TGT_LANGUAGE] = OCR_TOKENIZER

# The training dataset vocabulary set to vocabulary transform dict
vocab_transform[SRC_LANGUAGE] = TRAINING_DATASET.source_vocab
vocab_transform[TGT_LANGUAGE] = TRAINING_DATASET.target_vocab
vocab_transform[SRC_LANGUAGE].set_default_index(UNK_IDX)
vocab_transform[TGT_LANGUAGE].set_default_index(UNK_IDX)

SRC_VOCAB_SIZE = len(vocab_transform[SRC_LANGUAGE])
TGT_VOCAB_SIZE = len(vocab_transform[TGT_LANGUAGE])

# Transforms = token_transform[SRC/TGT_LANGUAGE], vocab_transform[SRC/TGT_LANGUAGE], tensor_transform
def sequential_transforms(*transforms):
    def func(txt_input):
        for transform in transforms:
            txt_input = transform(txt_input)
        return txt_input
    return func

# function to add BOS/EOS and create tensor for input sequence indices
def tensor_transform(token_ids: List[int]):
    return torch.cat((torch.LongTensor([BOS_IDX]),
                      torch.LongTensor(token_ids),
                      torch.LongTensor([EOS_IDX])))

text_transform = {}
text_transform[SRC_LANGUAGE] = sequential_transforms(
                                    token_transform[SRC_LANGUAGE],
                                    vocab_transform[SRC_LANGUAGE],
                                    tensor_transform)
text_transform[TGT_LANGUAGE] = sequential_transforms(
                                    token_transform[TGT_LANGUAGE],
                                    vocab_transform[TGT_LANGUAGE],
                                    tensor_transform)


def create_mask(src, tgt):
    src_seq_len = src.shape[0]
    tgt_seq_len = tgt.shape[0]
    tgt_mask = nn.Transformer.generate_square_subsequent_mask(tgt_seq_len).to(DEVICE)
    src_mask = torch.zeros((src_seq_len, src_seq_len),device=DEVICE).type(torch.bool)
    src_padding_mask = (src == PAD_IDX).transpose(0, 1)
    tgt_padding_mask = (tgt == PAD_IDX).transpose(0, 1)
    return src_mask, tgt_mask, src_padding_mask, tgt_padding_mask

torch.manual_seed(0)

TRANSFORMER = Seq2SeqTransformer(params.NUM_ENCODER_LAYERS,
                                 params.NUM_DECODER_LAYERS,
                                 params.EMB_SIZE,
                                 params.NHEAD,
                                 SRC_VOCAB_SIZE,
                                 TGT_VOCAB_SIZE,
                                 params.FFN_HID_DIM,
                                 params.DROPOUT)

for p in TRANSFORMER.parameters():
    if p.dim() > 1:
        nn.init.xavier_uniform_(p)


TRANSFORMER = TRANSFORMER.to(DEVICE)
loss_fn = nn.CrossEntropyLoss(ignore_index=PAD_IDX)

OPTIMIZER = Adam(TRANSFORMER.parameters(),
                 lr=params.LEARNING_RATE,
                 betas=(0.9, 0.98),
                 eps=1e-9)


def collate_fn(batch):
    src_batch, tgt_batch = [], []
    for src_sample, tgt_sample in batch:
        src_batch.append(text_transform[SRC_LANGUAGE](' '.join(src_sample).rstrip("\n")))
        tgt_batch.append(text_transform[TGT_LANGUAGE](' '.join(tgt_sample).rstrip("\n")))
    src_batch = pad_sequence(src_batch, padding_value=PAD_IDX)
    tgt_batch = pad_sequence(tgt_batch, padding_value=PAD_IDX)
    return src_batch, tgt_batch

VALIDATION_DATALOADER = DataLoader(VALIDATION_DATASET, batch_size=params.BATCH_SIZE, collate_fn=collate_fn)

def train_epoch(model, train_optimizer, training_dataset):
    model.train()
    losses = 0
    train_dataloader = DataLoader(training_dataset,
                                  shuffle=True,
                                  batch_size=params.BATCH_SIZE,
                                  collate_fn=collate_fn)
    for src, tgt in tqdm(train_dataloader, leave=False):
        src = src.to(DEVICE)
        tgt = tgt.to(DEVICE)
        tgt_input = tgt[:-1, :]
        src_mask, tgt_mask, src_padding_mask, tgt_padding_mask = create_mask(src, tgt_input)
        logits = model(src, tgt_input, src_mask, tgt_mask,src_padding_mask, tgt_padding_mask, src_padding_mask)
        train_optimizer.zero_grad()
        tgt_out = tgt[1:, :]
        loss = loss_fn(logits.reshape(-1, logits.shape[-1]), tgt_out.reshape(-1))
        loss.backward()
        train_optimizer.step()
        losses += loss.item()
    #SCHEDULER.step()
    return losses / len(train_dataloader)


def evaluate(model):
    model.eval()
    losses = 0
    for src, tgt in VALIDATION_DATALOADER:
        src = src.to(DEVICE)
        tgt = tgt.to(DEVICE)
        tgt_input = tgt[:-1, :]
        src_mask, tgt_mask, src_padding_mask, tgt_padding_mask = create_mask(src, tgt_input)
        logits = model(src, tgt_input, src_mask, tgt_mask,src_padding_mask, tgt_padding_mask, src_padding_mask)
        tgt_out = tgt[1:, :]
        loss = loss_fn(logits.reshape(-1, logits.shape[-1]), tgt_out.reshape(-1))
        losses += loss.item()
    return losses / len(VALIDATION_DATALOADER)

if __name__ == '__main__':
    tokenizer_vocab_size = len(wordpiece_vocab)
    NUM_EPOCHS = params.NUM_EPOCHS
    for epoch in range(1, NUM_EPOCHS+1):
        name = f'less_errors_line_pairs_{len(TRAINING_DATASET)}_{params.EMB_SIZE}_{params.NHEAD}_{params.FFN_HID_DIM}_{params.BATCH_SIZE}_{params.NUM_ENCODER_LAYERS}_{params.NUM_DECODER_LAYERS}_{str(params.DROPOUT).replace(".", "dot")}_{params.NUM_EPOCHS}_{params.WEIGHT_DECAY}_{params.LEARNING_RATE}_{Path(TOKENIZER).stem}_EPOCH_{epoch}'
        with open(f'val/{name}.txt', 'w', encoding='utf-8') as outfile:
            start_time = timer()
            train_loss = train_epoch(TRANSFORMER, OPTIMIZER, TRAINING_DATASET)
            end_time = timer()
            val_loss = evaluate(TRANSFORMER)
            ep_info = f"Epoch: {epoch}, Train loss: {train_loss:.3f}, Val loss: {val_loss:.3f}, "f"Epoch time = {(end_time - start_time):.3f}s"
            now = datetime.now()
            date = now.date()
            month = date.month
            day = date.day
            time = now.time()
            hours = time.hour
            minute = time.minute
            print(ep_info, f'({day}/{month} {hours}:{minute})')
            outfile.write(ep_info + '\n')
            torch.save(TRANSFORMER.state_dict(), f'models/{name}.model')
            # torch.save({'epoch': epoch,
            #             'model_state_dict': TRANSFORMER.state_dict(),
            #             'optimizer_state_dict': OPTIMIZER.state_dict(),
            #             'loss': train_loss,
            #             }, f'models/{name}.model')
        with open(f'hyperparams/{name}.py', 'w', encoding='utf-8') as outf:
            outf.write('VOCAB_SIZE = ' + str(tokenizer_vocab_size) + '\n')
            outf.write('VOCAB_MIN_FREQ = ' + str(TOKENIZER).split('_')[-1][:-1] + '\n')
            outf.write('EMB_SIZE = ' + str(params.EMB_SIZE) + '\n')
            outf.write('NHEAD = ' + str(params.NHEAD) + '\n')
            outf.write('FFN_HID_DIM = ' + str(params.FFN_HID_DIM) + '\n')
            outf.write('BATCH_SIZE = ' + str(params.BATCH_SIZE) + '\n')
            outf.write('NUM_ENCODER_LAYERS = ' + str(params.NUM_ENCODER_LAYERS) + '\n')
            outf.write('NUM_DECODER_LAYERS = ' + str(params.NUM_DECODER_LAYERS) + '\n')
            outf.write('DROPOUT = ' + str(params.DROPOUT) + '\n')
            outf.write('NUM_EPOCHS = ' + str(params.NUM_EPOCHS) + '\n')
            outf.write('LEARNING_RATE = ' + str(params.LEARNING_RATE) + '\n')
            outf.write('SRC_VOCAB_SIZE = ' + str(SRC_VOCAB_SIZE) + '\n')
            outf.write('TGT_VOCAB_SIZE = ' + str(TGT_VOCAB_SIZE) + '\n')
            outf.write('ORIGINAL_FILES = ' + "'" + str(ORIGINAL_FILES) + "'" + '\n')
            outf.write('CORRECTED_FILES = ' + "'" + str(CORRECTED_FILES) + "'" + '\n')
