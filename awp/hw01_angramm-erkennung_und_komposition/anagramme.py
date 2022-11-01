#!/usr/bin/env python3

import sys
from collections import defaultdict

anagrams = defaultdict(set)

# read in all words in first column
with open(sys.argv[1], 'r') as file:
    for line in file:
        # only extract the word in first column
        word, _, _ = line.strip().split('\t')
        if word.isalpha() and len(word) > 2:
            sorted_word = ''.join(sorted(word.lower()))
            # add korpus words as dict values if they consist of
            # the sorted letters, which are the dict keys
            anagrams[sorted_word].add(word.lower())

# print words if there is more than one anagram available
for v in anagrams.values():
    if len(v) > 1:
        print(*v)
