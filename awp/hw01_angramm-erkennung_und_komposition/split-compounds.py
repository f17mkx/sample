#!/usr/bin/env python3

import sys
import math
from collections import defaultdict

freq = defaultdict(int)
# frequency dictionary, words to wordcount from corpus
capitals = defaultdict(lambda: defaultdict(int))
# dictionary of dictionary for capitals -> lowercase form to its uccurences in corpus to frequencys in corpus

with open(sys.argv[1], 'r') as file:
    for line in file:
        word, tag, lemma = line.strip().split('\t')
        words = []
        if word.isalpha() and len(word) >= 3 and tag == 'NN':
            # fliter corpus by word length and tag 'noun', remove punctuation
            freq[word.lower()] += 1
            # increase wordcount of normalized token by 1
            capitals[word.lower()][word] += 1
            # increase actual form of 'word' corpus by 1 in its subdictionary


freq['s'] = 0
# add Fugenelement "s" to the frequency dictionary

capitals = {key: max(capitals[key], key=capitals[key].get) for key in capitals.keys()}
# store most frequent actual form of normalized token in dictionary: normalized form to most frequent occurence

def split(word, s=0, partial_words=None):
    # s = start position of index
    if partial_words is None:
        partial_words = []
    for e in range(s, len(word) + 1):
        # iterate through whole word, start with s
        if word[s:e] in freq.keys():
            # check if string in freq
            partial_words.append(word[s:e])
            # append dict wit found word
            if e == len(word):
                yield partial_words
                # return combination at the end of the word
                partial_words.pop()
                # remove last word to keep looking for other compunds
            else:
                yield from split(word, e, partial_words)
                # look for a new word after what you just found
    if partial_words:
        partial_words.pop()
        # remove leftover words within recursion


def ratings(word_splits):
    # takes the list of combinations as input
    parts = [word for word in word_splits if word != 's']
    # delete Fugenelement "s" from word_splits
    frequencys = [freq[word] for word in parts]
    # get frequencys for words for the calculation of geo_mean
    geo_mean = math.prod(frequencys) ** (1 / len(frequencys))
    # calculate geometric mean
    return round(geo_mean, 1), parts
    # return rounded mean and parts


for word in freq.keys():
    if word == 's':
        continue
    results = [ratings(word_splits) for word_splits in split(word)]
    # create results for all split combinations of a word
    if len(results) > 1:
        # if more than 1 result, print results
        mean, parts = sorted(results, reverse=True)[0] # besser wäre mit max()
        # sort and get result with highest score
        parts = [capitals[word] for word in parts]
        # get most frequent actual form of 'word' from capitals dictionary
        print(capitals[word], mean, *parts)
        # print(capitals[word], mean, ' '.join(parts))
