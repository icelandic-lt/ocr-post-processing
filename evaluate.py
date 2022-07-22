import argparse
from nltk.translate import chrf_score, bleu_score
from nltk.metrics import precision, recall, f_measure


parser = argparse.ArgumentParser()
parser.add_argument('--original')
parser.add_argument('--corrected')
parser.add_argument('--transformed')
args = parser.parse_args()

def read_file(file, for_precis=False):
    with open(file, 'r', encoding='utf-8') as infile:
        for line in infile:
            if for_precis:
                yield line.rstrip()
            else:
                yield line.rstrip()

def evaluate_chrf(original_file, corrected_file, transformed_file):
    original = list(read_file(original_file))
    corrected = list(read_file(corrected_file))
    transformed = list(read_file(transformed_file))
    met_corr = set(read_file(corrected_file, for_precis=True))
    met_trans = set(read_file(transformed_file, for_precis=True))
    precis = precision(met_corr, met_trans)
    rec = recall(met_corr, met_trans)
    f_meas = f_measure(met_corr, met_trans)
    orig_corr_chrf = round(chrf_score.corpus_chrf(original, corrected), 7)
    corr_trns_chrf = round(chrf_score.corpus_chrf(corrected, transformed), 7)

    scores = {
        'Original/Corrected CHRF:': orig_corr_chrf,
        'Corrected/Transformed CHRF:': corr_trns_chrf,
        'Improvement:': round((corr_trns_chrf - orig_corr_chrf), 7),
        'Prop improv:': round((corr_trns_chrf - orig_corr_chrf)/(1 - orig_corr_chrf), 7),
        'Precision': round(precis, 7),
        'Recall': round(rec, 7),
        'F-Measure': round(f_meas, 7)

    }
    return scores

def evaluate_bleu(original_file, corrected_file, transformed_file):
    scores = {

    }
    original_file = list([sent] for sent in original_file)
    corrected_file = list(corrected_file)
    original_corrected_score = bleu_score.corpus_bleu(original_file, corrected_file)
    
    corrected_file = [[sent] for sent in corrected_file]
    transformed_file = list(transformed_file)
    corrected_transformed_score = bleu_score.corpus_bleu(corrected_file, transformed_file)
    
    scores['Original/Corrected'] = round(original_corrected_score, 7)
    scores['Corrected/Transformed'] = round(corrected_transformed_score, 7)
    scores['Improvement:'] = round((corrected_transformed_score - original_corrected_score), 7)
    scores['Prop improv:'] = round((corrected_transformed_score - original_corrected_score)/(1 - original_corrected_score), 7)
    return scores

if __name__=='__main__':
    chrf = """
########
# CHRF #
########
           """
    bleu = """
########
# BLEU #
########
           """
    print(chrf)
    for i in evaluate_chrf(args.original, args.corrected, args.transformed).items():
        print(i)
    print(bleu)
    for i in evaluate_bleu(read_file(args.original), read_file(args.corrected), read_file(args.transformed)).items():
        print(i)