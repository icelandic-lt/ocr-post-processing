from torch.utils.data import Dataset
from torchtext.vocab import build_vocab_from_iterator


special_symbols = ['<unk>', '<pad>', '<bos>', '<eos>']

class OCRDataset(Dataset):
    def __init__(self, df, source_column, target_column):
        self.df = df
        self.source_texts = self.df[source_column]
        self.target_texts = self.df[target_column]
        self.source_vocab = build_vocab_from_iterator(self.source_texts.tolist(),
                                                      specials=special_symbols,
                                                      special_first=True)
        self.target_vocab = build_vocab_from_iterator(self.target_texts.tolist(),
                                                      specials=special_symbols,
                                                      special_first=True)

    def __len__(self):
        return len(self.df)


    def __getitem__(self, index):
        source_text = self.source_texts[index]
        target_text = self.target_texts[index]
        return source_text, target_text


if __name__ == '__main__':
    pass