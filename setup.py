from pathlib import Path
import pandas
from utils.sql.db_setup import FileToSQL
from utils.error_files_setup import write_replacements_to_single_file, create_correct_word_list
from globals import (read_files,
                     tokenize,
                     ORIGINAL_FILES,
                     CORRECTED_FILES,
                     ORIGINAL_VAL_FILES,
                     CORRECTED_VAL_FILES)


def handle_file(filename):
    file_path = Path(filename)
    if file_path.is_file():
        print(f'> {Path(filename).name} already exists. Overwriting.')
        file_path.unlink()
    else:
        print(f'> Writing to {Path(filename).name}.')



if __name__ == '__main__':
    print('> Building training dataframe')
    training_data = pandas.DataFrame()
    training_data['original'] = list(read_files(ORIGINAL_FILES, tokenizer=tokenize))
    training_data['corrected'] = list(read_files(CORRECTED_FILES, tokenizer=tokenize))
    training_data.to_pickle('dataframes/training_data.pickle')

    print('> Building validation dataframe')
    validation_data = pandas.DataFrame()
    validation_data['original'] = list(read_files(ORIGINAL_VAL_FILES, tokenizer=tokenize))
    validation_data['corrected'] = list(read_files(CORRECTED_VAL_FILES, tokenizer=tokenize))

    validation_data.to_pickle('dataframes/validation_data.pickle')

    correct_words = create_correct_word_list('data/parallel/50k_gold/corrected/')
    print('> Setting up files...')
    write_replacements_to_single_file('data/errors/all_replacements.tsv',
                                      correct_word_list=correct_words,
                                      ocr_files_path='data/parallel/50k_gold/original',
                                      corrected_files_path='data/parallel/50k_gold/corrected')
    print('> Setting up databases...')
    # This database contains original_string, corrected_string, frequency_of_substitution
    handle_file('dbs/replacements.db')
    original_replacement_to_db = FileToSQL(file_to_db='data/errors/all_replacements.tsv',
                                           db_name='dbs/replacements')
    original_replacement_to_db.create_db_orig_corr_freq('REPLACEMENTS',
                                                        'original',
                                                        'replacement',
                                                        'frequency',
                                                        field_separator='\t',
                                                        headers=['original',
                                                                 'replacement',
                                                                 'frequency'])
