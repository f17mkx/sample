#!/usr/bin/python3

import sys


def add(tree, nodeID, letter, targetNode):
    if nodeID == len(tree):
        tree.append({})
        # create new dictionary when there is none for a traceID exceeding len(tree)
    tree[nodeID][letter] = targetNode
        # add targetNode as key in respective list at index NodeID


def search(word):
    nodeID = 0
    word = word.replace('\n', ' ')
    # replace '\n' with our endsymbol ' '
    for letter in word:
        if letter in tree[nodeID]:
            # verify there is a dictionary entry for the character in the list of dictionaries
            nodeID = tree[nodeID][letter]
            # if so, make the targetNode the new NodeID / index
        else:
            print(f'{word}\nunknown')
            return
            # return to stop processing
    print(f'{word}\nknown')


if __name__ == "__main__":
    treefile, wordlist = sys.argv[1:]

    # treefile, wordlist = 'tree', 'wordlist.txt'

    tree = []

    with open(treefile) as file:
        for rule in file:
            nodeID, letter, targetNode = rule[:-1].split('\t')
            add(tree, int(nodeID), letter, int(targetNode))

    with open(wordlist) as file:
        for word in file:
            search(word)


