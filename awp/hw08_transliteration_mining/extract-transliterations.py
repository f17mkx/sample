#!/usr/bin/python3

import sys
import numpy as np
from collections import defaultdict

def clip_value(val):
    return max(val, 1e-300)


class NoiseModel:
    def __init__(self, srcWordList, tgtWordList):
        """
        Noise Model
        :param srcWordList: Source word list
        :param tgtWordList: Target word list
        """

        self.srcLetterProb = NoiseModel.compute_LetterProb(srcWordList)
        self.tgtLetterProb = NoiseModel.compute_LetterProb(tgtWordList)

    def wordPairProb(self, srcWord, tgtWord):
        """
        Compute probability of word pairs.
        :param srcWord: Source word
        :param tgtWord: Target word
        :return: Probability of word pairs
        """

        scrWordProb = 1
        tgtWordProb = 1

        # Probability of Source word
        for char in srcWord:
            scrWordProb *= self.srcLetterProb[char]

        # Probability of Target word
        for char in tgtWord:
            tgtWordProb *= self.tgtLetterProb[char]

        return scrWordProb * tgtWordProb

    @staticmethod
    def compute_LetterProb(wordList):
        """
        Compute Probability for each letter in the language given the whole word list of language.
        :param wordList: Complete word list of the language
        :return: Probability for each letter in the language
        """

        # total number of letters in language
        langCount = 0
        # Number of each letter in langauge
        letterCount = defaultdict(int)
        # Probability of each letter in the language
        letterProb = defaultdict(float)

        # count letters in languag. Total, and by letter.
        for word in wordList:
            for char in word:
                letterCount[char] += 1
                langCount += 1

        # compute probability by dividing char count by total count
        for char, count in letterCount.items():
            letterProb[char] = count / langCount

        return letterProb


class TransliterationModel:
    def __init__(self, srcLetters, tgtLetters):
        """
        Transliteration Model
        """

        # Unit -> (srcChar, tgtChar) tuple
        # P(x, y) = sum(P(a)), a <- align(x, y)
        # sum by addFreq method

        self.transUnitProb = defaultdict(float)
        self.transUnitFreq = defaultdict(float)

        n = len(srcLetters)
        m = len(tgtLetters)
        for srcLetter in srcLetters:
            for tgtLetter in tgtLetters:
                self.transUnitProb[(srcLetter, tgtLetter)] = 1 / (n * m - 1)

    def addFreq(self, srcLetter, tgtLetter, freq):
        """

        :param srcLetter: Source letter
        :param tgtLetter: Target letter
        :param freq:
        """

        self.transUnitFreq[(srcLetter, tgtLetter)] += freq

    def reestimate(self):
        """

        :return: Total count of character pairs.
        """

        # sum frequences of all pairs
        totalFreq = sum(self.transUnitFreq.values())

        # calculate probability of pairs by dividing Pair frequency by total frequency
        for pair, freq in self.transUnitFreq.items():
            self.transUnitProb[pair] = freq / totalFreq

        # fresh start counting freq in next round
        self.transUnitFreq.clear()

        return totalFreq


class MiningModel:
    def __init__(self, srcWords, tgtWords, numIterations):
        """
        Mining Model
        :param srcWords: Source word list
        :param tgtWords: Target word list
        :param numIterations: number of EM steps
        """
        self.noiseModel = NoiseModel(srcWords, tgtWords)

        srcLetters = set(''.join(srcWords))
        tgtLetters = set(''.join(tgtWords))
        self.transModel = TransliterationModel(srcLetters, tgtLetters)

        # Interpolation factor: lambda
        self.modelPrior = 0.5
        self.modelFreq = 0

        # EM-Training
        for i in range(numIterations):
            self.em(srcWords, tgtWords)
            self.modelPrior = self.modelFreq / len(srcWords)

    def forward(self, srcWord, tgtWord):
        """
        Calculates the probability α[i, k] that the transliteration model
        generates the i-prefix of x and the k-prefix of y (with arbitrary alignment) together.
        :param srcWord: Source word
        :param tgtWord: Target word
        :return: alpha
        """

        n = len(srcWord)  # number of letters in source word
        m = len(tgtWord)  # number of letters in target word
        alpha = np.zeros((n + 1, m + 1))
        alpha[0, 0] = 1

        for i in range(1, n + 1):
            for k in range(m + 1):
                p_x = self.transModel.transUnitProb[(srcWord[i - 1], '')]
                p_y = self.transModel.transUnitProb[('', tgtWord[k - 1])]
                p_xy = self.transModel.transUnitProb[(srcWord[i - 1], tgtWord[k - 1])]
                alpha[i, k] = alpha[i - 1, k] * p_x + alpha[i, k - 1] * p_y + alpha[i - 1, k - 1] * p_xy
        return alpha

    def backward(self, srcWord, tgtWord):
        """
        Calculates the probability β[j, k] that the transliteration model
        generates the suffix of x from position j and the suffix of y from position k (with arbitrary alignment) together.
        :param srcWord: Source word
        :param tgtWord: Target word
        :return: beta
        """
        n = len(srcWord)  # number of letters in source word
        m = len(tgtWord)  # number of letters in target word
        beta = np.zeros((n + 1, m + 1))
        beta[n, m] = 1

        for i in reversed(range(n)):
            for k in reversed(range(m)):
                p_x = self.transModel.transUnitProb[(srcWord[i], '')]  # p(x_i:)
                p_y = self.transModel.transUnitProb[('', tgtWord[k])]  # p(:y_k)
                p_xy = self.transModel.transUnitProb[(srcWord[i], tgtWord[k])]  # p(x_i:y_k)
                beta[i, k] = beta[i + 1, k] * p_x + beta[i, k + 1] * p_y + beta[i + 1, k + 1] * p_xy
        return beta

    def reestimateProbs(self):
        """
        Reestimate the Transliteration Model word pair probability.
        """
        self.transModel.reestimate()

    def em(self, srcWords, tgtWords):
        """
        Expectation–maximization step
        :param srcWord: Source word
        :param tgtWord: Target word
        """
        # E-Schritt
        for srcWord, tgtWord in zip(srcWords, tgtWords):
            self.estimateFreqs(srcWord, tgtWord)
        # M-Schritt
        self.reestimateProbs()

    def estimateFreqs(self, srcWord, tgtWord):
        """
        Estimate the frequency of character pairs for the give word pair.
        :param srcWord: Source word
        :param tgtWord: Target word
        :return: Frequency
        """
        n, m = len(srcWord), len(tgtWord)
        alpha = self.forward(srcWord, tgtWord)
        beta = self.backward(srcWord, tgtWord)
        p_trans = clip_value(alpha[n, m])

        aposteriori = self.aposterioriProb(srcWord, tgtWord)
        self.modelFreq += aposteriori

        p = self.transModel.transUnitProb

        for i in range(n):
            for k in range(m):
                alpha_ik = clip_value(alpha[i, k])

                # xi:yk
                LPair1 = (srcWord[i], tgtWord[k])
                p_xi_yk = p[LPair1]
                beta_ik = clip_value(beta[i + 1, k + 1])
                gamma_xi_yk = aposteriori * alpha_ik * p_xi_yk * beta_ik / p_trans
                self.transModel.addFreq(*LPair1, gamma_xi_yk)

                # xi:
                LPair2 = (srcWord[i], '')
                p_xi = p[LPair2]
                beta_i = clip_value(beta[i + 1, k])
                gamma_xi = aposteriori * alpha_ik * p_xi * beta_i / p_trans
                self.transModel.addFreq(*LPair2, gamma_xi)

                # :yk
                LPair3 = ('', tgtWord[k - 1])
                p_yk = p[LPair3]
                beta_k = clip_value(beta[i, k + 1])
                gamma_yk = aposteriori * alpha_ik * p_yk * beta_k / p_trans
                self.transModel.addFreq(*LPair3, gamma_yk)

        return aposteriori

    def aposterioriProb(self, srcWord, tgtWord):
        """
        Calculate the aposteriori probability given the source and target word.
        :param srcWords: Source words
        :param tgtWords: Target words
        :return: aposteriori probability
        """
        n = len(srcWord)
        m = len(tgtWord)
        alpha = self.forward(srcWord, tgtWord)
        p_mining = self.modelPrior * alpha[n, m] + (1 - self.modelPrior) * self.noiseModel.wordPairProb(srcWord,
                                                                                                        tgtWord)
        aposteriori = self.modelPrior * alpha[n, m] / p_mining

        return aposteriori

    def printTransliterations(self, srcWords, tgtWords):
        """
        Output source word, target word with its aposteriori Prob
        :param srcWords: Source words
        :param tgtWords: Target words
        """

        for srcWord, tgtWord in zip(srcWords, tgtWords):
            aposteriori = self.aposterioriProb(srcWord, tgtWord)
            if aposteriori > 0.5:
                print(srcWord, tgtWord, aposteriori)


if __name__ == "__main__":
    numIterations = 3  # number of EM rounds

    srcWords = []
    tgtWords = []

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        for line in f:
            srcWord, tgtWord = line.strip().split()
            srcWords.append(srcWord)
            tgtWords.append(tgtWord)

    model = MiningModel(srcWords, tgtWords, numIterations)
    model.printTransliterations(srcWords, tgtWords)
