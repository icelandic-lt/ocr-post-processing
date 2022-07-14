from shlex import split
from string import punctuation as p
from tokenizer import correct_spaces
extended_punctuation = p + "–„”“—«»"


def format_token_out(token, start_punct, end_punct):
    tok_and_punct = ''
    if start_punct:
        tok_and_punct += start_punct
    tok_and_punct += token
    if end_punct:
        tok_and_punct += end_punct
    if tok_and_punct.endswith('—'):
        return tok_and_punct
    return tok_and_punct + ' '


def clean_token(token):
    token_out = token.strip(extended_punctuation.replace('-', ''))
    # hyphen_index = token.find('-')
    # if hyphen_index:
    #     print(hyphen_index)
    if token.endswith('-') and not token_out.endswith('-'):
        token_out += '-'
    if token.startswith('--'):
        token_out = token_out[1:]
    return token_out


def format_line_out(line, junk_list):
    line_out = line
    for junk in junk_list:
        tmp_line_out = line_out.replace(junk, '')
        line_out = tmp_line_out
    line_out = line_out.replace(' – ', '–')
    #return line_out.strip()
    return correct_spaces(line_out)
    #return ' '.join(line_out.split()).strip()

def is_editable(token, index, len_sent):
    clean_token = ''.join([char for char in token if char.isalpha()])
    return (len(clean_token) > 3
            #and not (index != 0 and len(token) < 4)
            and not (index == 0)
            and not token.endswith('-') 
            and not token.endswith('.')
            and not '—' in token
            and not all([char in extended_punctuation for char in token])
            and not len([char for char in token if char in extended_punctuation]) > 1
            and not index == (len_sent-1))

def split_keep_delimiter(line, delimiter):
    line = line.split(delimiter)
    return [token + delimiter for token in line[:-1]] + [line[-1]]





if __name__ == '__main__':
    spl = ' '.join(split_keep_delimiter('sjeu stjzttarflokkur,—talsmenn', '—'))
    print(spl.split())
