#!/usr/bin/python3

import sys


def add(tree, word, nodeID=0):
    if nodeID == len(tree):
        # if the node that is being pointed to does not exist yet: create it
        tree.append({})

    if word[0] == '\n':
        # replace '\n' with ' '
        letter = ' '
    else:
        letter = word[0]

    if letter not in tree[nodeID].keys():
        # if the node does not have an edge with the current letter: create it, pointing to a new node
        tree[nodeID][letter] = len(tree)


    print(f'{nodeID}\t{letter}\t{tree[nodeID][letter]}')
    # print "node   letter  targetnode"

    if letter == ' ':
        # end of word: finish
        return

    nodeID = tree[nodeID][letter]
    add(tree, word[1:], nodeID)
    # go to next node and process next letter




if __name__ == "__main__":
    wordlist = sys.argv[1]
    # file with wordlist
    tree = []
    # list of dictionaries (every index is a node)

    with open(wordlist) as file:
        for word in file:
            add(tree, word)

