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

def exists_in_bin(token):
    return bin_conn.lookup(token) != []

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
        self.is_punct = all(char in punctuation for char in self.original_token)
        # A list of punctuation marks (excl. hyphens) and character strings
        # (a word can contain a hyphen) of a given OCRed token.
        self.token_and_punct = re.findall(r'[\w-]+|[^\s\w]', self.original_token)

        # The longest character string (possibly including a hyphen)
        # of self.token_and_punct
        self.clean = max(self.token_and_punct, key=len)

        # Boolean. Whether self.clean consists of only numeric characters
        self.is_number = all(char.isnumeric() or char in [',', '.', '-'] for char in (str(self.original_token)))

        # Boolean. Whether a token contains any numeric characters, but is not wholly numeric.
        self.contains_number = any(char.isnumeric() for char in self.clean) and not self.is_number

        # Boolean. Whether a token contains punctuation (other than a hyphen)
        # but doesn't start or end with it.
        self.contains_bad_punct = any(char in punctuation for char in self.original_token
                                  if char != '-' and not token.startswith(char)
                                  and not token.endswith(char)
                                  and char != '-')

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

    

    def _check_if_possibly_compound(self):
        """
        This function can be used to check whether certain words "make sense"
        as an Icelandic compound word.
        """
        bin_lookup = Bin()
        return bin_lookup.lookup(self.original_token)[1] != []


    def mutate_token_with_unigram_replacements(self):
        """
        This function mutates a token based on known character substitutions
        (see: get_char_replacements) and returns all the possibilities if they
        exist in a dictionary.
        """
        all_possible_replacements = []
        length_of_product = reduce(mul, map(len, self.char_unigrams), 1)
        if length_of_product > 1000:
            return []
        for unigram in self.char_unigrams:
            possible_replacements = [char for char, freq in
                                     get_char_replacements(unigram[1], freq=3)]
            all_possible_replacements.append([unigram[1]] + possible_replacements[0:2])
        all_possible_replacements = [''.join(w) for w in product(*all_possible_replacements)]
        return [w for w in all_possible_replacements if word_in_any_dict(''.join(w))]

    def mutate_token_with_bigram_replacements(self):
        """
        Doesn't work. Could be useful, though.
        Same as above but replaces possibly erroneous bigrams with known substitutions.
        """
        all_possible_replacements = []
        for bigram in self.char_bigrams:
            possible_replacements = [char for char, freq in
                                     get_char_replacements(bigram[1], freq=3)]
            all_possible_replacements.append([bigram[1]] + possible_replacements[0:2])
        print(all_possible_replacements)
        all_possible_replacements = [''.join(w) for w in product(*all_possible_replacements)]
        return [w for w in all_possible_replacements if word_in_any_dict(''.join(w))]

    def __str__(self):
        return self.original_token

    def __repr__(self):
        return self.original_token

    def __len__(self):
        return len(self.original_token)

if __name__ == '__main__':
    pass
