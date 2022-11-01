import string
import numpy as np
import random


class Reader:

    def __init__(self, path):
        self.path = path
        self.punctuation = set(string.punctuation)
        self.courses = self.get_lines()
        self.vocabulary = self.get_vocabulary()
        self.vector_spaced_data = self.data_to_vectorspace()

    def get_lines(self):
        with open(self.path) as f:
            return [line.strip() for line in f.readlines()]

    def normalize_word(self, word):
        removed_puncutation = ''.join(i for i in word if i not in self.punctuation)
        return removed_puncutation.lower()

    def get_vocabulary(self):
        return sorted(set(self.normalize_word(word) for i in self.courses for word in i.split()))

    def vectorspaced(self, course):
        c_words = [self.normalize_word(word) for word in course.split()]
        return [int(word in c_words) for word in self.vocabulary]

    def data_to_vectorspace(self):
        return [self.vectorspaced(course) for course in self.courses if course]


class Kmeans:
    """performs k-means clustering"""

    def __init__(self, k):
        self.k = k
        self.means = None

    def distance(self, x, y):
        return np.sqrt(np.sum([((x[idx] - y[idx])**2) for idx in range(len(x))]))

    def classify(self, input):
        dists = [self.distance(input, self.means[idx]) for idx in range(len(self.means))]
        return dists.index(min(dists))
        # distance_to_input = [(Kmeans.distance(mean, input), i) for i, mean in enumerate(self.means)]
        # distances_sorted = sorted(distance_to_input, key=lambda x: x[0])
        # return distances_sorted[0][1]

    def vector_mean(self, vectors):
        return np.mean(vectors, axis=0).tolist()

    def train(self, inputs):
        # choose k random points as the initial means
        self.means = random.sample(inputs, self.k)
        # self.means = [inputs[32], inputs[67], inputs[46]]

        assignments = None
        iteration = 0
        while iteration != 100:
            # find new assignments
            assignments = list(map(self.classify, inputs))

            # compute new means based on the new assignments
            for i in range(self.k):
                # find all the points assigned to cluster i
                i_points = [p for p, a in zip(inputs, assignments) if a == i]
                if i_points:
                    # make sure i_points is not empty so don't divide by 0
                    self.means[i] = self.vector_mean(i_points)
            iteration += 1
