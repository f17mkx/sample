#!/usr/bin/python3

import sys
from collections import defaultdict, namedtuple


class Parser:
    def __init__(self, grammarfile, lexiconfile):
        self.grammar = Parser.create_dict(grammarfile)
        self.lexicon = Parser.create_dict(lexiconfile)
        # generate grammar and lexicon from respective files
        self.chart = list()
        # create chart list
        self.Rule = namedtuple('Rule', ['lhs', 'rhs', 'dotpos', 'startpos'])

    @staticmethod
    def create_dict(rules):
        """Setup method to create the dictionaries"""
        dictionary = defaultdict(list)
        with open(rules) as file:
            for rule in file:
                lhs, *rhs = rule.split()
                # separate left hand side from right hand side of the rule
                dictionary[lhs].append(rhs)
                # add rule to the dictionary: key:= left hand side value:= right hand side
        return dictionary

    def parse(self, tokens):
        """Parses the sentence, returns bool"""
        self.chart = [() for word in tokens]
        # initialize chart
        self.chart.insert(0, ())
        # add startpos = -1 as another item to predict rules prior to the first word

        self.predict('S', startpos=0, endpos=0)
        # start gathering these rules

        for position in range(len(tokens)):
            self.scan(tokens[position], position)
            # scan every word to create rules

        for item in self.chart[-1]:
            # return true if it is a grammatical sentence
            if item.lhs == 'S':
                return True
        # if not grammatical return false.
        return False

    def scan(self, Terminal, position):
        """Scan the next token and add all possible combinations to the set"""

        # If word not in lexicon, print error.
        if Terminal not in self.lexicon:
            print('unknown word:', Terminal, file=sys.stderr)
        else:
            for POS in self.lexicon[Terminal][0]:
                # add all possible parts of speech from the lexikon
                self.add(POS, [Terminal], 1, position, position + 1)

    def predict(self, nonTerminal, startpos, endpos):
        """finds all rules whose right side starts with nonTerminal on the left side"""
        # predict all possibilities of building 'nonTerminal'
        for rhs in self.grammar[nonTerminal]:
            self.add(nonTerminal, rhs, 0, startpos, endpos)

    def complete(self, nonTerminal, startpos, endpos):
        """completes rules which expect the newly found constituent"""
        # check all rules that end with 'startpos'
        for item in self.chart[startpos]:
            # check if the item can be further processed with the newly found constituent
            if item.dotpos < len(item.rhs) and item.rhs[item.dotpos] == nonTerminal:
                self.add(item.lhs, item.rhs, item.dotpos + 1, item.startpos, endpos)

    def add(self, lhs, rhs, dotpos, startpos, endpos):
        """Makes an entry for a rule with dot posision"""
        item = self.Rule._make([lhs, rhs, dotpos, startpos])
        # if chart does not already have the same entry in the column
        if item not in self.chart[endpos]:
            # make entry in chart
            self.chart[endpos] += (item,)
            if dotpos == len(rhs):
                # If a constituent was found
                self.complete(lhs, startpos, endpos)
            if dotpos < len(rhs) and rhs[dotpos] in self.grammar.keys():
                self.predict(rhs[dotpos], startpos, endpos)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("Usage: earley.py grammar.txt lexicon.txt sentences.txt")

    grammar, lexicon, sentences = sys.argv[1:]
    # gather grammar, lexicon and sentences from sys.argv

    parser = Parser(grammar, lexicon)
    # initialzie class object Parser from grammar- and lexiconflie

    # initializing punctuations string
    punc = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''

    # read sentences from file
    with open(sentences) as file:
        for line in file:
            # remove punctuations
            no_punc_line = ''.join([char if char not in punc else "" for char in line])

            # remove extra white space, and split word into tokens for parsing
            tokens = no_punc_line.strip().split()

            if len(tokens) > 0:
                # print whether sentence is grammatical or not
                if parser.parse(tokens):
                    print('the sentence is grammatical')
                else:
                    print('the sentence is not grammatical')

