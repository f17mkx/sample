#!/usr/bin/python3

from collections import defaultdict
import sys


class Data:
    def __init__(self, trainfile, devfile, numWords):
        self.trainSentences = Data.readData(trainfile)  # train data
        self.devSentences = Data.readData(devfile)  # dev data
        self.numWords = numWords  # number of tags

        # lists of words and tags, sorted by frequency (index correspond to IDs)
        self.wordlist, self.taglist = self.getIDs(trainfile)
        self.numTags = len(self.taglist)

    @staticmethod
    def readData(filename):
        sentences = []
        wordSeq = []
        tagSeq = []

        with open(filename, encoding='utf-8') as file:
            for line in file:  # every line is a word with its tag
                line = line.strip()
                if line:
                    # empty line means new sentence
                    word, tag = line.split('\t')
                    wordSeq.append(word)
                    tagSeq.append(tag)
                else:
                    # at the end of a sentence add, the generated sentence to "sentences"
                    sentences.append((wordSeq, tagSeq))
                    wordSeq = []
                    tagSeq = []
                    # [(["Das", "ist", "ein", "Satz"],["ART","V","ART","NE"]),(...)...]
        return sentences

    def getIDs(self, filename):
        # create a list of the n most frequent words and tags and save them lists
        # where the index is the ID (the unknown word has index 0)
        wordFreq = defaultdict(int)
        tagFreq = defaultdict(int)

        with open(filename, encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:
                    word, tag = line.split('\t')
                    wordFreq[word] += 1
                    tagFreq[tag] += 1

        sorted_wordFreq = dict(sorted(wordFreq.items(), key=lambda x: x[1], reverse=True))  # sort by frequency
        sorted_tagFreq = dict(sorted(tagFreq.items(), key=lambda x: x[1], reverse=True))  # sort by frequency

        words = [''] + list(sorted_wordFreq.keys())  # add unknown word to beginning of list
        tags = [''] + list(sorted_tagFreq.keys())  # add unknown tag to beginning of list

        words = words[:self.numWords + 1]  # cut-off infrequent words
        return words, tags

    def words2IDs(self, words):
        return [self.wordlist.index(word) if word in self.wordlist else 0 for word in words]

    def tags2IDs(self, tags):
        return [self.taglist.index(tag) if tag in self.taglist else 0 for tag in tags]

    def IDs2tags(self, ids):
        return [self.taglist[id] for id in ids]


def run_test():
    # load dev & train data: dev.tagged train.tagged
    train_file, dev_file = sys.argv[1:3]
    data = Data(train_file, dev_file, 50)

    training = data.trainSentences
    dev = data.devSentences
    print('done')


if __name__ == "__main__":
    run_test()
