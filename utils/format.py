def format_token_out(token, start_punct, end_punct):
    tok_and_punct = ''
    if start_punct:
        tok_and_punct += start_punct
    tok_and_punct += token
    if end_punct:
        tok_and_punct += end_punct
    return tok_and_punct + ' '
