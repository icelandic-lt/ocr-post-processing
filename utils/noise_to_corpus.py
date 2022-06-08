import argparse
from glob import glob
from pathlib import Path
from os import mkdir
from noise_to_text import read_file, noise_file


parser = argparse.ArgumentParser()
parser.add_argument('-c', '--corpus', help='A directory containing the files to be noised')
args = parser.parse_args()

def noise_corpus(corpus_path):
    i = 1
    original_files = glob(f'{corpus_path}/*')
    base_dir = Path(args.corpus).parents[0]
    target_original_dir = f'{base_dir}/original'
    if not Path(target_original_dir).exists():
        mkdir(target_original_dir)
    for file in original_files:
        print(f'[{i}/{len(original_files)}]')
        filename = Path(file).name
        noised_file = [line for line in noise_file(read_file(file))]
        with open(f'{target_original_dir}/{filename}', 'w', encoding='utf-8') as outfile:
            for line in noised_file:
                outfile.write(line + '\n')
        i += 1


if __name__ == '__main__':
    noise_corpus(args.corpus)