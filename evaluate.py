import argparse
from nltk.translate import chrf_score

parser = argparse.ArgumentParser()
parser.add_argument('--original')
parser.add_argument('--corrected')
parser.add_argument('--transformed')
parser.add_argument('--include-identical', action='store_true')
args = parser.parse_args()

def read_file(file):
    with open(file, 'r', encoding='utf-8') as infile:
        for (index, line) in enumerate(infile):
            yield (index, line.rstrip())


def evaluate(original_file, corrected_file, transformed_file):
    if args.include_identical:
        original = [token for d, token in list(read_file(original_file))]
        corrected = [token for d, token in list(read_file(corrected_file))]
        transformed = [token for d, token in list(read_file(transformed_file))]
        orig_corr_chrf = round(chrf_score.corpus_chrf(original, corrected), 7)
        orig_trns_chrf = round(chrf_score.corpus_chrf(original, transformed), 7)
        corr_trns_chrf = round(chrf_score.corpus_chrf(corrected, transformed), 7)

    else:
        original = list(read_file(original_file))
        corrected = list(read_file(corrected_file))
        transformed = list(read_file(transformed_file))

        original_corrected_set = set(original) & set(corrected)
        original_transformed_set = set(original) & set(transformed)
        corrected_transformed_set = set(corrected) & set(transformed)

        #
        original_not_in_corrected = [line for (index, line) in original if (index, line) not in original_corrected_set]
        corrected_not_in_original = [line for (index, line) in corrected if (index, line) not in original_corrected_set]
        #
        original_not_in_transformed = [line for (index, line) in original if (index, line) not in original_transformed_set]
        transformed_not_in_original = [line for (index, line) in transformed if (index, line) not in original_transformed_set]
        #
        transformed_not_in_corrected = [line for (index, line) in transformed if (index, line) not in corrected_transformed_set]
        corrected_not_in_transformed = [line for (index, line) in corrected if (index, line) not in corrected_transformed_set]

        orig_corr_chrf = round(chrf_score.corpus_chrf(original_not_in_corrected, corrected_not_in_original), 7)
        orig_trns_chrf = round(chrf_score.corpus_chrf(original_not_in_transformed, transformed_not_in_original), 7)
        corr_trns_chrf = round(chrf_score.corpus_chrf(corrected_not_in_transformed, transformed_not_in_corrected), 7)
    scores = {
        'Original/Corrected CHRF:': orig_corr_chrf,
        'Original/Transformed CHRF:': orig_trns_chrf,
        'Corrected/Transformed CHRF:': corr_trns_chrf,
        'Improvement:': round((corr_trns_chrf - orig_corr_chrf), 7),
        'Prop improv:': round((corr_trns_chrf - orig_corr_chrf)/(1 - orig_corr_chrf), 7)
    }
    return scores

if __name__=='__main__':
    for i in evaluate(args.original, args.corrected, args.transformed).items():
        print(i)
