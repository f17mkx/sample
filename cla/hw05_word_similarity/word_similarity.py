import math
import numpy as np
from hw05_word_similarity.cooccurrence import vocabulary_from_wordlist, cooccurrences, cooc_dict_to_matrix, ppmi_weight
from sklearn.decomposition import TruncatedSVD



class DenseSimilarityMatrix:
    def __init__(self, word_matrix, word_to_id):
        """
        Creates a WordSimilarity object.

        :param word_matrix: A matrix-like object (numpy 2d array or scipy sparse matrix), where rows correspond to words
            and columns correspond to dimensions of the representation space (context or embedding feature).
        :param word_to_id: A dictionary from word string to word id (= row number in word_matrix).
        """
        self.word_matrix = word_matrix
        self.word_to_id = word_to_id
        self.id_to_word = {id: word for word, id in self.word_to_id.items()}

    def word_similarity(self, wordA, wordB):
        """ Computes cosine similarity between two words."""
        if not (wordA in self.word_to_id and wordB in self.word_to_id):
            return .0
        rowA, rowB = (self.word_to_id[wordA], self.word_to_id[wordB])
        vecA, vecB = (self.word_matrix[rowA, :], self.word_matrix[rowB, :])
        dotAB, dotAA, dotBB = (vecA.dot(vecB.T), vecA.dot(vecA.T), vecB.dot(vecB.T))
        return dotAB / math.sqrt(dotAA * dotBB)

    def similarities_of_word(self, word):
        """ Computes cosine similarity between one query word and all words in the vocabulary. Efficient
        matrix-multiplication is used."""
        row = self.word_to_id[word]
        vec = self.word_matrix[row, :]
        m = self.word_matrix
        dot_m_v = m.dot(vec.T)  # n-dim vector
        dot_m_m = np.sum(m * m, axis=1)  # n-dim vector, sum of element-wise multiplication
        dot_v_v = vec.dot(vec.T)  # float
        return dot_m_v / (math.sqrt(dot_v_v) * np.sqrt(dot_m_m))

    def most_similar_words(self, word, n):
        """ Returns a list of n words with the greatest similarities to the given word."""
        if word not in self.word_to_id:
            return []

        sims = self.similarities_of_word(word)
        return [self.id_to_word[id] for id in (-sims).argsort()[:n]]


class PpmiWeightedSparseMatrix:
    def __init__(self, word_list, vocab_size, window_size):
        """
        Creates an object for similarity computation with sparse, PPMI weighted co-occurrence matrices.
        Co-occurrences are obtained from a word list.
        :param word_list: Word list.
        :param vocab_size: Number of top n most frequent words to be considered.
        :param window_size: Window size for co-occurrences.
        """

        # define the vocabulary
        # get co-occurrences dict
        # create word matrix, word to column and column to word mapping
        # Apply PPMI weighting to the word matrix
        # (Use the class attribute names accessed in other class methods)


        vocab = vocabulary_from_wordlist(word_list, vocab_size)
        cooc_dict = cooccurrences(word_list, window_size, vocab)


        self.word_matrix, self.word_to_id = cooc_dict_to_matrix(cooc_dict, vocab)
        self.id_to_word = {id: word for word, id in self.word_to_id.items()}
        self.word_matrix = ppmi_weight(self.word_matrix)



    def toSvdSimilarityMatrix(self, n_components):
        """ Computes truncated SVD with only n columns retained."""
        svd = TruncatedSVD(n_components=n_components)
        u_sigma_trunc = svd.fit_transform(self.word_matrix)
        return DenseSimilarityMatrix(u_sigma_trunc, self.word_to_id)

    def similarities_of_word(self, word):
        """ Computes cosine similarity between one query word and all words in the vocabulary. Efficient
        matrix-multiplication is used."""
        row = self.word_to_id[word]
        vec = self.word_matrix[row, :]
        m = self.word_matrix
        dot_m_v = m.dot(vec.T)
        dot_m_m = (m.multiply(m)).sum(axis=1)
        dot_v_v = vec.dot(vec.T)[0, 0]
        return (dot_m_v / (math.sqrt(dot_v_v) * np.sqrt(dot_m_m))).A1

    def most_similar_words(self, word, n):
        """ Returns a list of n words with the greatest similarities to the given word."""
        if word not in self.word_to_id:
            return []
        sims = self.similarities_of_word(word)
        return [self.id_to_word[id] for id in (-sims).argsort()[:n]]
