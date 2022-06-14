from string import punctuation
import re
from sql.lookup import SQLDatabase, SQLiteQuery
punctuation += "–„”—«»"

def get_char_errors(ngr, freq=10):
    """
    This function returns known character replacements for a given ngram, based on how frequently it appears
    in an original/corrected OCR parallel corpus.
    """
    sql = SQLDatabase(db_name='../dbs/replacements.db')
    query = SQLiteQuery(table_name='REPLACEMENTS', cursor=sql.cursor)
    return query.get_replacement_by_corrected(corrected_ngr=ngr, freq=freq)


def gen_non_overlapping_ngrams(chars, ngr):
    return [chars[i:i + ngr] for i in range(0, len(chars), ngr)]

def count_chars(token):
    return len([char for char in token if char.isalpha()])

class TextToken:
    def __init__(self, token):
        # The token exactly as it appears in the line. Tokens are gotten by
        # splitting a line on spaces (\s)
        self.original_token = token
        self.is_punct = all(char in punctuation for char in self.original_token)
        # A list of punctuation marks (excl. hyphens) and character strings
        # (a word can contain a hyphen) of a given OCRed token.
        self.token_and_punct = re.findall(r'[\w-]+|[^\s\w]', self.original_token)

        # The longest character string (possibly including a hyphen)
        # of self.token_and_punct
        self.clean = max(self.token_and_punct, key=count_chars)

        self.startswith_punct = self.original_token[0] in punctuation
        self.endswith_punct = (self.original_token[-1] in punctuation
                               and not self.original_token[-1] == '-')

        self.last_character_index = max([index for index, char in enumerate(self.original_token)
                                        if char not in punctuation],
                                        default=len(self.original_token))

        self.first_character_index = min([index for index, char in enumerate(self.original_token)
                                         if char not in punctuation],
                                         default=len(self.original_token))

        self.start_punct_index = [index for index, char in enumerate(self.original_token)
                                  if char in punctuation and index < self.first_character_index]

        self.end_punct_index = [index for index, char in enumerate(self.original_token)
                                if char in punctuation and index > self.last_character_index]

    def __str__(self):
        return self.original_token

if __name__ == '__main__':
    pass
