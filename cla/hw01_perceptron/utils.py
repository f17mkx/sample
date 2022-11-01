import random
from nltk import word_tokenize
from collections import defaultdict, Counter


def dot(dictA, dictB):
    return sum([dictA.get(key) * dictB.get(key, 0) for key in dictA])


def normalized_tokens(text):
    return [token.lower() for token in word_tokenize(text)]


class DataInstance:
    def __init__(self, feature_counts, label):
        """ A data instance consists of a dictionary with feature counts (string -> int) and a label (True or False)."""
        self.feature_counts = feature_counts
        self.label = label

    @classmethod
    def from_list_of_feature_occurrences(cls, feature_list, label):
        """ Creates feature counts for all features in the list."""
        feature_counts = Counter(feature_list)
        return cls(feature_counts, label)

    @classmethod
    def from_text_file(cls, filename, label):
        with open(filename, 'r') as myfile:
            token_list = normalized_tokens(myfile.read().strip())
        return cls.from_list_of_feature_occurrences(token_list, label)


class Dataset:
    def __init__(self, instance_list):
        """ A data set is defined by a list of instances """
        self.instance_list = instance_list
        self.feature_set = set.union(*[set(inst.feature_counts.keys()) for inst in instance_list])

    def get_topn_features(self, n):
        """ This returns a set with the n most frequently occurring features (i.e. the features that are contained in 
        most instances). """
        feature_counts = defaultdict(int)
        for instance in self.instance_list:
            for key, value in instance.feature_counts.items():
                feature_counts[key] += value
        feature_counts = sorted(feature_counts, key=feature_counts.get, reverse=True)
        return set(feature_counts[:n])

    def set_feature_set(self, feature_set):
        """
        This restricts the feature set. Only features in the specified set are retained. All other feature are removed
        from all instances in the dataset AND from the feature set."""
        for instance in self.instance_list:
            instance.feature_counts = {k: v for k, v in instance.feature_counts.items() if k in feature_set}
        self.feature_set = set.union(*[set(inst.feature_counts.keys()) for inst in self.instance_list])


    def most_frequent_sense_accuracy(self):
        """ Computes the accuracy of always predicting the overall most frequent sense for all instances in the 
        dataset. """
        counts = Counter([instance.label for instance in self.instance_list])
        most_common_label = sorted(counts, key=counts.get, reverse=True)[0]
        return counts[most_common_label]/(counts[False] + counts[True])

    def shuffle(self):
        """ Shuffles the dataset. Beneficial for some learning algorithms."""
        random.shuffle(self.instance_list)
