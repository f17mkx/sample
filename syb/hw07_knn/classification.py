import math
import os
from collections import Counter
from collections import defaultdict

from nltk import FreqDist, word_tokenize


def dot(dictA, dictB):  # Skalarprodukt zwischen zwei Vekotoren
    return sum([dictA.get(tok) * dictB.get(tok, 0) for tok in dictA])


def normalized_tokens(text):  # normalisierungsfunktion
    return [token.lower() for token in word_tokenize(text)]


class TextDocument:  # erhält den Text und macht ein Klassenobject draus
    def __init__(self, text, id=None, category=None):
        self.text = text
        self.token_counts = FreqDist(normalized_tokens(text))
        self.id = id
        self.category = category

    @classmethod
    def from_file(cls, filename, category):  # Einlesen vom pfad
        print(filename)
        with open(filename, 'r', encoding="ISO-8859-1") as myfile:
            text = myfile.read().strip()
        return cls(text, filename, category)


def cosine_similarity(weightedA, weightedB):
    dotAB = dot(weightedA, weightedB)
    normA = math.sqrt(dot(weightedA, weightedA))
    normB = math.sqrt(dot(weightedB, weightedB))
    return dotAB / (normA * normB)


class DocumentCollection:
    def __init__(self, term_to_df, term_to_docids, docid_to_doc, doc_to_category):
        # string to int
        self.term_to_df = term_to_df
        # string to set of string
        self.term_to_docids = term_to_docids
        # string to TextDocument
        self.docid_to_doc = docid_to_doc
        # TextDocument to category
        self.doc_to_category = doc_to_category

    @classmethod
    def from_dir(cls, dir):
        files = [(os.path.join(root, name), os.path.relpath(root, dir)) for root, dirs, f in os.walk(dir, topdown=False)
                 for name in f]
        docs = [TextDocument.from_file(f, cat) for f, cat in files]
        return cls.from_document_list(docs)

    @classmethod
    def from_document_list(cls, docs):
        term_to_df = defaultdict(int)
        term_to_docids = defaultdict(set)
        docid_to_doc = dict()
        doc_to_category = dict()
        for doc in docs:
            docid_to_doc[doc.id] = doc
            doc_to_category[doc] = doc.category
            for token in doc.token_counts.keys():
                term_to_df[token] += 1
                term_to_docids[token].add(doc.id)
        return cls(term_to_df, term_to_docids, docid_to_doc, doc_to_category)

    def tfidf(self, counts):
        N = len(self.docid_to_doc)
        return {tok: tf * math.log(N / self.term_to_df[tok]) for tok, tf in counts.items() if tok in self.term_to_df}


class KNNClassifier:
    def __init__(self, n_neighbors=1):
        self.n_neighbors = n_neighbors
        self.doc_collection = None
        self.vectorsOfDoc_collection = None

    def fit(self, doc_collection):
        self.doc_collection = doc_collection
        self.vectorsOfDoc_collection = [(doc, self.doc_collection.tfidf(doc.token_counts))
                                        for doc in self.doc_collection.docid_to_doc.values()]

    def calculate_similarities(self, vecTestDoc, vectorsOfTrainDocs):
        return [(cosine_similarity(vecTestDoc, x), y.category) for y, x in vectorsOfTrainDocs]

    def order_nearest_to_farthest(self, distances):
        return sorted(distances, reverse=True)

    def labels_k_closest(self, sorted_distances):
        return [nearest_label for _, nearest_label in sorted_distances][:self.n_neighbors]

    def choose_one(self, labels):
        counts = Counter(labels)
        winner, winnercount = counts.most_common(1)[0]
        num_winners = len([x for x in counts.values() if x == winnercount])
        if num_winners == 1:
            return winner
        else:
            return self.choose_one(labels[:-1])

    def classify(self, test_file):
        test_doc = TextDocument.from_file(test_file, 'unknowcat')
        test_vec = self.doc_collection.tfidf(test_doc.token_counts)
        distsribution = self.calculate_similarities(test_vec, self.vectorsOfDoc_collection)
        distsribution = self.order_nearest_to_farthest(distsribution)
        k_labels = self.labels_k_closest(distsribution)
        return self.choose_one(k_labels)

    def get_accuracy(self, gold, predicted):
        correct = 0
        for i in range(len(gold)):
            if gold[i] == predicted[i]:
                correct += 1
        return (correct/len(gold)) * 100
