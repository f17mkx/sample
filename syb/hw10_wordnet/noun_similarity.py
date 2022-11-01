import nltk
from nltk.corpus import wordnet
from itertools import combinations
from collections import Counter


def leave_odd_man_out(words):
    sim_dict = {word: [other_word for other_word in words if other_word != word] for word in words}
    for word, other_words in sim_dict.items():
        pairs = [(word, other_word) for other_word in other_words]
        scores = get_similarity_scores(pairs)
        sim_dict[word] = sum([tpl[1] for tpl in scores])
    return max(sim_dict, key=lambda x: -sim_dict[x])


def get_similarity_scores(pairs):
    results = []
    for word_1, word_2 in pairs:
        synsets_1, synsets_2 = wordnet.synsets(word_1), wordnet.synsets(word_2)
        merger = [(set_1, set_2) for set_1 in synsets_1 for set_2 in synsets_2]
        max_score = max([pair[0].path_similarity(pair[1]) for pair in merger if
                        pair[0].path_similarity(pair[1]) is not None])
        max_line = (f'{word_1}-{word_2}', max_score)
        results.append(max_line)
    return sorted(results, key=lambda x: -x[1])
