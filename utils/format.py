from string import punctuation as p

extended_punctuation = p + "–„”“—«»"

def format_token_out(token, start_punct, end_punct):
    tok_and_punct = ''
    if start_punct:
        tok_and_punct += start_punct
    tok_and_punct += token
    if end_punct:
        tok_and_punct += end_punct
    return tok_and_punct + ' '


def clean_token(token):
    token_out = token.strip(extended_punctuation)
    if token.endswith('-'):
        token_out += '-'
    return token_out


def format_line_out(line, junk_list):
    line_out = line
    for junk in junk_list:
        tmp_line_out = line_out.replace(junk, '')
        line_out = tmp_line_out
    return line_out.strip()
    #return ' '.join(line_out.split()).strip()

def is_editable(token, index):
    clean_token = ''.join([char for char in token if char.isalpha()])
    return (len(clean_token) > 3
            and not (index != 0 and len(token) < 4)
            and not token.endswith('-') 
            and not token.endswith('.')
            and not '—' in token
            and not all([char in extended_punctuation for char in token]))

