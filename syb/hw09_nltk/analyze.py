from nltk import FreqDist
from nltk import word_tokenize


class Analyzer(object):
    def __init__(self, path):
        """reads the file text, creates the list of words (use nltk.word_tokenize to tokenize the text),
            and calculates frequency distribution """
        with open(path, 'r') as f:
            self.text = word_tokenize(f.read())
        self.token_counts = FreqDist(self.text)

    def numberOfTokens(self):
        """returns number of tokens in the text """
        return len(self.text)

    def vocabularySize(self):
        """returns a list of the vocabulary of the text """
        return len(self.token_counts.keys())

    def lexicalDiversity(self):
        """returns the lexical diversity of the text """
        return self.numberOfTokens()/self.vocabularySize()

    def getKeywords(self):
        """return words as possible key words, that are longer than seven characters, that occur more than seven
        times (sorted alphabetically) """
        return sorted([word for word, count in self.token_counts.items() if len(word) > 7 and count > 7])

    def numberOfHapaxes(self):
        """returns the number of hapaxes in the text"""
        return len(self.token_counts.hapaxes())

    def avWordLength(self):
        """returns the average word length of the text"""
        return sum([len(word) for word in self.token_counts.keys()]) / self.vocabularySize()

    def topSuffixes(self):
        """returns the 10 most frequent 2-letter suffixes in words
            (restrict to words of length 5 or more)"""
        two_letter_suff = FreqDist(word[-2:] for word in self.token_counts.keys() if len(word) >= 5)
        return sorted(two_letter_suff, key=two_letter_suff.get, reverse=True)[:10]

    def topPrefixes(self):
        """returns the 10 most frequent 2-letter prefixes in words
            (restrict to words of length 5 or more)"""
        two_letter_pref = FreqDist(word[:2] for word in self.token_counts.keys() if len(word) >= 5)
        return sorted(two_letter_pref, key=two_letter_pref.get, reverse=True)[:10]

    def tokensTypical(self):
        """returns first 5 tokens of the (alphabetically sorted) vocabulary
        that contain both often seen prefixes and suffixes in the text. As in topPrefixes()
        and topSuffixes(), Prefixes and Suffixes are 2 characters long."""
        top_pref = self.topPrefixes()
        top_suff = self.topSuffixes()
        return [word for word in sorted(self.token_counts.keys()) if word[:2] in top_pref and word[-2:] in top_suff][:5]
