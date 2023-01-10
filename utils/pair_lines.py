from tokenizer import correct_spaces
from .lexicon_lookup import (makes_sense, exists_in_bin, exists_in_bin_or_old_words, 
                    n_good_words,
                    sub_tokens_in_line)
from .format import (clean_token, 
                    format_line_out)





ocr_junk = ['<unk>', 'alt;', 'quot;', 'aguot;', '139;', 'a39;', '& 39;', 'a 39;', 'alt;']

def read_lines(file):
    with open(file, 'r', encoding='utf-8') as infile:
        return infile.read().splitlines()

def process_torch_lines(transformed_lines):
            """
            Iterate over all the lines in a file. The format is as such:
            First part of a sentence <newline> which continues here
            which continues here <newline> and ends here.
            and ends here. <newline> The next sentence
            The model is trained on data like this, because its input (during
            the inference phase) is very often split between lines, and the
            transformer's attention mechanism only works on running sequences.
            This helps it learn between lines.
            """
            n_lines = len(transformed_lines)
            current_index = 0
            while current_index < n_lines:
                current_line_out = ''
                curr_line_is_last_in_file = current_index+1 == n_lines

                line_is_split = len(transformed_lines[current_index].split('<newline>')) > 1
                curr_first_half = transformed_lines[current_index].split('<newline>')[0].strip()

                curr_secnd_half = None
                next_first_half = None

                next_secnd_half = None
                last_secnd_half = None

                if line_is_split:
                    curr_secnd_half = transformed_lines[current_index].split('<newline>')[1].strip()
                    # current_line_out set as curr_secnd_half.
                    current_line_out = curr_secnd_half
                else:
                    current_Line_out = curr_first_half
                if not curr_line_is_last_in_file:
                    next_first_half = transformed_lines[current_index+1].split('<newline>')[0].strip()
                    next_line_is_split = len(transformed_lines[current_index+1].split('<newline>')) > 1
                    if next_line_is_split:
                        next_secnd_half = transformed_lines[current_index+1].split('<newline>')[1]
                try:
                    last_line = transformed_lines[current_index-1]
                    last_secnd_half = last_line.split('<newline>')[1].strip()
                except IndexError:
                    pass
                # This is only for the fist line. Special case because of the indexing.
                if current_index == 0:
                    yield format_line_out(curr_first_half, ocr_junk)

                else:
                    # The following code block has to do with picking a line based on whether the first word in the following
                    # line and the last word in the current line can be conjoined into a single known word. If not, it picks
                    # curr_secnd_half
                    try:
                        if all([curr_secnd_half, next_first_half, next_secnd_half]):
                            last_word_in_curr_secnd_half = curr_secnd_half.split()[-1]
                            last_word_in_next_first_half = next_first_half.split()[-1] 
                            first_word_in_next_secnd_half = next_secnd_half.split()[0]                    
                            if last_word_in_curr_secnd_half.endswith('-'):
                                last_word_in_curr_secnd_half = last_word_in_curr_secnd_half[:-1]
                            if last_word_in_next_first_half.endswith('-'):
                                last_word_in_next_first_half = last_word_in_next_first_half[:-1]
                            combined_curr_secnd_next_secnd = last_word_in_curr_secnd_half + first_word_in_next_secnd_half
                            combined_next_first_next_secnd = last_word_in_next_first_half + first_word_in_next_secnd_half
                            if combined_curr_secnd_next_secnd != combined_next_first_next_secnd:
                                if exists_in_bin_or_old_words(combined_next_first_next_secnd):
                                    current_line_out = next_first_half
                                else:
                                    current_line_out = curr_secnd_half   
                    # The following block has to do with picking a line based on whether the last word in the preceding
                    # line and the first word in the current line can be conjoined into a single known word. If not,
                    # it picks curr_secnd_half
                        if all([curr_secnd_half, next_first_half, last_secnd_half]):
                            first_word_in_current_second_half = curr_secnd_half.split()[0]
                            first_word_in_next_first_half = next_first_half.split()[0]
                            last_word_in_last_second_half = last_secnd_half.split()[-1]
                            if last_word_in_last_second_half.endswith('-'):
                                last_word_in_last_second_half = last_word_in_last_second_half[:-1]
                            combined_curr_secnd_last_secnd = last_word_in_last_second_half + first_word_in_current_second_half
                            combined_next_first_last_secnd = last_word_in_last_second_half + first_word_in_next_first_half
                            if combined_curr_secnd_last_secnd != combined_next_first_last_secnd:
                                if exists_in_bin_or_old_words(combined_next_first_last_secnd):
                                    current_line_out = next_first_half
                                else:
                                    current_line_out = curr_secnd_half
                    except:
                        current_line_out = curr_secnd_half
                if current_line_out is not None and not ((current_index + 1) == n_lines and current_line_out == ''):
                    yield format_line_out(current_line_out, ocr_junk)
                current_index += 1  


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-f', '--file')
    parser.add_argument('-l', '--include-lexicon-lookup', action='store_true')
    args = parser.parse_args()
    test_file = args.file
    for line in process_transformed_lines(read_lines(test_file)):
        if args.include_lexicon_lookup:
            print(sub_tokens_in_line(line))
        else:
            print(line)
            pass
