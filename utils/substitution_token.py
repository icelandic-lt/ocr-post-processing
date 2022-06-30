from sys import path
path.append('..')
from sql.lookup import SQLDatabase, SQLiteQuery
from math import log
from statistics import mean
from Levenshtein import editops, distance
from difflib import SequenceMatcher

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
        return query.cursor.execute(f"""
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

def get_similar_by_known_subs(token, similar_tokens):
    """
    Looks up whether given a similar token makes sense to the original one,
    given the difference (Levenshtein insertions/deletions/replacements) between the two
    """
    similar_words = []
    for similar in similar_tokens:
        sm = SequenceMatcher(None, token, similar).get_opcodes()
        token_subs = []
        substitution_sequence = []
        for tag, i1, i2, j1, j2 in sm:
            if tag != 'equal':
                try:
                    original = token[i1:i2]
                    sub = similar[j1:j2]
                    change = sub, original
                    substitution_sequence.append(change)
                except IndexError:
                    pass
        else:
            if substitution_sequence:
                token_subs.append(substitution_sequence)
            substitution_sequence = []
        st = SubstitutionToken(similar, token_subs)
        if st.all_subs_possible:
            similar_words.append(st)
    return similar_words



if __name__ == '__main__':
    print(get_similar_by_known_subs('kiörsljórn', ['kjörstjórn']))