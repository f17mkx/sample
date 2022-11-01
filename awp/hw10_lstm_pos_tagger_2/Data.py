from collections import defaultdict
import collections
import sys
import json


class Data:
    def __init__(self, *args):
        if len(args) == 1:
            self.init_test(*args)
        else:
            self.init_train(*args)

        # define dict for faster lookup with id
        self.tag2id = defaultdict(int)
        for tag, id in zip(sorted(self.tag2ID, key=self.tag2ID.get, reverse=True), list(range(1, self.numTags + 1))):
            self.tag2id[tag] = id

        self.id2tag = defaultdict(str)
        for k, v in self.tag2id.items():
            self.id2tag[v] = k

    def init_test(self, paramfile):
        with open(paramfile, 'r') as file:
            self.word2ID, self.tag2ID = json.load(file)
            self.numTags = len(self.tag2ID)

    def init_train(self, trainfile, devfile, numWords):
        self.trainSentences = Data.readData(trainfile)  # train data
        self.devSentences = Data.readData(devfile)  # dev data
        self.numWords = numWords  # number of tags

        # lists of words and tags, sorted by frequency (index correspond to IDs)
        self.word2ID, self.tag2ID = self.getIDs()
        self.numTags = len(self.tag2ID)

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

    # def getIDs(self, filename):
    def getIDs(self):
        wordFreq = collections.Counter(word for words, _ in self.trainSentences for word in words)
        tagset = set(tag for _, tags in self.trainSentences for tag in tags)
        words, _ = zip(*wordFreq.most_common(self.numWords))
        word2ID = {word: id + 1 for id, word in enumerate(words)}  # +1 for unknown word
        tag2ID = {tag: id + 1 for id, tag in enumerate(tagset)}  # +1 for unknown tag
        word2ID[''] = 0  # for unknown word
        tag2ID[''] = 0  # for unknown tag
        return word2ID, tag2ID

    def words2IDs(self, words):
        return [self.word2ID.get(word, 0) for word in words]

    def tags2IDs(self, tags):
        return [self.tag2ID.get(tag, 0) for tag in tags]

    def IDs2tags(self, ids):
        return [self.id2tag[ID] for ID in ids]

    def store_parameters(self, paramfile):
        tables = self.word2ID, self.tag2ID
        toJson = json.dumps(tables, indent=4, ensure_ascii=False)
        outfile = open(paramfile, 'w')
        outfile.write(toJson)
        outfile.close()

    @staticmethod
    def sentences(filename):
        with open(filename) as file:
            for line in file:
                yield line.strip().split(" ")  # Output muss liste von Wörtern sein


def run_test():
    # load dev & train data: dev.tagged train.tagged
    train_file, dev_file = sys.argv[1:3]
    data = Data(train_file, dev_file, 50)

    training = data.trainSentences
    dev = data.devSentences
    print('done')


if __name__ == "__main__":
    run_test()
