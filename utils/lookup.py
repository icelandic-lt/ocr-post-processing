from tokens import SubstitutionToken
from difflib import SequenceMatcher
import pickle
from format import clean_token, is_editable
from islenska.bincompress import BinCompressed
from islenska import Bin
from Levenshtein import distance, editops

bin_conn = BinCompressed()
isl_lookup = Bin()

def get_similar_by_known_subs(token, similar_tokens, error_frequency=0):
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
        if st.all_subs_possible and all([subs_freq > error_frequency for subs_freq in st.subs_freqs]):
            similar_words.append(st)
    return similar_words

def exists_in_old_words(token):
    return old_tree.find(token, 0) != []

def get_most_similar_from_list(token, similar_tokens):
    """
    Gets the token with the least Levenshtein distance from a given token
    """
    least_distance = 100
    tok_and_dist = [(str(tok), distance(token, str(tok))) for tok in similar_tokens]
    min_dist = min(dist for tok, dist in tok_and_dist)
    possible_similar = [(tok, dist) for tok, dist in tok_and_dist if dist <= (min_dist+1)]
    return possible_similar

def makes_sense(token):
    return isl_lookup.lookup(token)[1] != []

def exists_in_bin(token):
    return bin_conn.lookup(token) != []

def n_good_words(line):
    sensemaking_words = [word for word in line.split() 
                         if exists_in_bin_or_old_words(clean_token(word))]
    return (len(sensemaking_words))


def exists_in_bin_or_old_words(token):
    return (exists_in_bin(token) 
            or exists_in_bin(token.lower()) 
            or exists_in_bin(token.title())
            or exists_in_old_words(token)
            or exists_in_old_words(token.lower())
            or exists_in_old_words(token.title()))


# BÍN stored in a BK-tree for fast fuzzy lookup
with open('../bin_tree.pickle', 'rb') as bt:
    bin_tree = pickle.load(bt)

# Ritmálssafn stored in a BK-tree for fast fuzzy lookup
with open('../old_words.pickle', 'rb') as ow:
    old_tree = pickle.load(ow)



def lookup_similar(token, error_frequency=0):
    """
    Looks for similar tokens to the given one. It finds similar tokens in BÍN and returns
    the one with the least Levenshtein distance, given that the character substitutions
    (e.g. 'rn' → 'm' /// 'rnaður' → 'maður') are more frequent than error_frequency.
    """
    most_similar_token = None
    initial_token = token
    # Allow a Levenshtein distance of 3 for very long tokens, otherwise only 1.
    lev_dist = 3 if len(token) > 12 else 1
    # Look for similar candidates in BÍN.
    similar_cands = [tok for dist, tok in bin_tree.find(token, n=lev_dist)]
    # If there aren't any, look for similar candiates in BÍN to lowercase token.
    if len(similar_cands) == 0:
        similar_cands = [tok for dist, tok in bin_tree.find(token.lower(), n=lev_dist)]
        # If a similar lowercase candidate is found, convert the token (temporarily) to lowercase.
        if similar_cands:
            token = token.lower()
    if similar_cands:      
        most_similar = [token for token, dist in get_most_similar_from_list(token, similar_cands)]
        known_subs = get_similar_by_known_subs(token, most_similar, error_frequency=error_frequency)
        if len(known_subs) > 1:
            filtered_subs = min(get_most_similar_from_list(token, known_subs), key=lambda x: x[1])
            if filtered_subs:
                most_similar_token =  filtered_subs[0]
        else:
            if known_subs:
                most_similar_token = known_subs[0]
    return most_similar_token


def spelling_modernized(original_token, edited_token):
    substitution_sequence = []
    sm = SequenceMatcher(None, original_token, edited_token).get_opcodes()
    for tag, i1, i2, j1, j2 in sm:
            if tag == 'replace':
                try:
                    original = original_token[i1:i2]
                    sub = edited_token[j1:j2]
                    change = sub, original
                    substitution_sequence.append(change)
                except IndexError:
                    pass
    return any([x in [('é', 'je'), ('s', 'z')] for x in substitution_sequence])


if __name__ == '__main__':
    print(map_edits('fjelag', 'félag'))
    # test_string = [
    #     'Kosninpúrslifin',
    #     'og ÞJóðviljinn',
    #     'ÞJÓÐVILJINN reynir í frétt',
    #     'og forustugrein í gær að telja',
    #     'Ritstjórnarsímar: 4091, 4902.',
    #     'Auglýsingar: Emilía Möller.',
    #     'Auglýsingasími: 4906.',
    #     'kaupstaðarins. Úrslitin á öðr-',
    #     'um stöðum ræðir blaðið ekki,',
    #     'nema hvað það birtir kosninga-'
    #     'tölmmar nú og 1946. Ástæðan',
    #     'liggur í augum uppi: Komm-',
    #     'únistar hafa beðið ósigur um',
    #     'land allt, þegar Norðfjörður er',
    #     'undanskiIinn!   •',
    #     'Ö1 og vindlar',
    #     'altaf á fartinni hjá',
    #     'E. Einarssyni.',
    #     'og fleira ef þarf.'
    # ]
    # for line in test_string:
    #     tokens = line.split()
    #     for token in tokens:
    #         clean = clean_token(token)
    #         if not exists_in_bin_or_old_words(clean) and is_editable(clean, 0):
    #             print(lookup_similar(clean))
    #         else:
    #             print(token)
    # #print(get_similar_by_known_subs('kiörsljórn', ['kjörstjórn'], error_frequency=10))