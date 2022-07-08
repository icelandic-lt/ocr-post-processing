import re
from sql.lookup import SQLDatabase, SQLiteQuery
from format import extended_punctuation
from statistics import mean
from math import log

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

def exists_in_bin(token):
    return bin_conn.lookup(token) != []

class TextToken:
    def __init__(self, token):
        # The token exactly as it appears in the line. Tokens are gotten by
        # splitting a line on spaces (\s)
        self.original_token = token
        self.is_punct = all(char in extended_punctuation for char in self.original_token)
        # A list of punctuation marks (excl. hyphens) and character strings
        # (a word can contain a hyphen) of a given OCRed token.
        self.token_and_punct = re.findall(r'[\w-]+|[^\s\w]', self.original_token)

        # The longest character string (possibly including a hyphen)
        # of self.token_and_punct
        self.clean = max(self.token_and_punct, key=count_chars)

        self.startswith_punct = self.original_token[0] in extended_punctuation
        self.endswith_punct = (self.original_token[-1] in extended_punctuation
                               and not self.original_token[-1] in ['—', '-'])

        self.last_character_index = max([index for index, char in enumerate(self.original_token)
                                        if char not in extended_punctuation],
                                        default=len(self.original_token))

        self.first_character_index = min([index for index, char in enumerate(self.original_token)
                                         if char not in extended_punctuation],
                                         default=len(self.original_token))

        self.start_punct_index = [index for index, char in enumerate(self.original_token)
                                  if char in extended_punctuation and index < self.first_character_index]

        self.end_punct_index = [index for index, char in enumerate(self.original_token)
                                if char in extended_punctuation and index > self.last_character_index]

    def __str__(self):
        return self.original_token


class OCRToken:
    """
    This class represents a single token, which will be read from a single line
    at a time in other modules. Its attributes mostly have to do with various
    versions of the token, i.e. with and without punctuation, lower and
    titleized versions of it, etc. Some other attributes are its "Icelandicness",
    i.e. how frequently its character trigrams appear in a specific corpus,
    and mutated versions of it which are made by performing character substitutions
    based on how frequently said substitutions appear in an original/corrected
    OCR parallel corpus.
    """
    def __init__(self, token):
        # The token exactly as it appears in the line. Tokens are gotten by
        # splitting a line on spaces (\s)
        self.original_token = token
        self.is_punct = all(char in extended_punctuation for char in self.original_token)
        # A list of punctuation marks (excl. hyphens) and character strings
        # (a word can contain a hyphen) of a given OCRed token.
        self.token_and_punct = re.findall(r'[\w\-—]+|[^\s\w]', self.original_token)

        # The longest character string (possibly including a hyphen)
        # of self.token_and_punct
        self.clean = max(self.token_and_punct, key=len)

        # Boolean. Whether self.clean consists of only numeric characters
        self.is_number = all(char.isnumeric() or char in [',', '.', '-'] for char in (str(self.original_token)))

        # Boolean. Whether a token contains any numeric characters, but is not wholly numeric.
        self.contains_number = any(char.isnumeric() for char in self.clean) and not self.is_number


        self.startswith_punct = self.original_token[0] in extended_punctuation
        self.endswith_punct = (self.original_token[-1] in extended_punctuation
                               and not self.original_token[-1] in ['—', '-'])


        self.start_pattern = re.compile(f'^[{extended_punctuation}]*')
        self.end_pattern = re.compile(f'[{extended_punctuation}]*$')

        self.start_punct_info = re.match(self.start_pattern, self.original_token)
        self.start_punct = self.start_punct_info.group()
        self.start_punct_span = self.start_punct_info.span()
        
        self.end_punct_info = re.search(self.end_pattern, self.original_token)
        if self.end_punct_info:
            self.end_punct = self.end_punct_info.group()
            self.end_punct_span = self.end_punct_info.span()
        

        # self.last_character_index = max([index for index, char in enumerate(self.original_token)
        #                                 if char not in extended_punctuation],
        #                                 default=len(self.original_token))

        # self.first_character_index = min([index for index, char in enumerate(self.original_token)
        #                                  if char not in extended_punctuation],
        #                                  default=len(self.original_token))

        # self.start_punct_index = [index for index, char in enumerate(self.original_token)
        #                           if char in extended_punctuation and index < self.first_character_index]

        # self.end_punct_index = [index for index, char in enumerate(self.original_token)
        #                         if char in extended_punctuation and index > self.last_character_index]

    def __str__(self):
        return self.original_token

    def __repr__(self):
        return self.original_token

    def __len__(self):
        return len(self.original_token)


class SubstitutionToken:
    def __init__(self, token, char_subs, cutoff=1):
        self.token = token
        self.exists_in_bin = None
        self.is_known_old_word = None
        self.substitutions_score = 0
        self.formatted_subs = list(self.format_char_subs(char_subs))
        self.subs_freqs = self._setup_subs_freq()
        self.cutoff = cutoff
        self.all_subs_possible = (len(list(self.formatted_subs)) == len(self.subs_freqs) != 0)
        self.mean_log_freq = mean([log(freq) for freq in self.subs_freqs]) if self.all_subs_possible else 0

    def format_char_subs(self, subs):
        for sub in subs:
            for ngr in sub:
                tmp_del = ''
                tmp_add = ''
                tmp_add += ngr[0]
                tmp_del += ngr[1]
                yield tmp_del, tmp_add


    def get_subs_freq(self, orig, repl):
        sql = SQLDatabase(db_name='../dbs/replacements.db')
        query = SQLiteQuery(table_name='REPLACEMENTS', cursor=sql.cursor)
        return query.cursor.execute("""
                                        SELECT original, replacement, frequency
                                        FROM REPLACEMENTS
                                        WHERE original=? AND replacement=?
                                    """, (orig, repl)).fetchone()

    def _setup_subs_freq(self):
        subs_freqs = []
        for sub in self.formatted_subs:
            try:
                subs_and_freq = self.get_subs_freq(orig=sub[0], repl=sub[1])[-1]
                subs_freqs.append(subs_and_freq)
            except TypeError:
                pass
        return subs_freqs

    def __str__(self):
        return self.token

    def __repr__(self):
        return self.token

if __name__ == '__main__':
    tok = OCRToken('<.')
    print(dir(tok.start_punct))
    print(tok.start_punct)
