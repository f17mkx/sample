from nltk import FreqDist, word_tokenize
import itertools
from collections import defaultdict
import os, math


def dot(dictA, dictB):
    """
    >>> dot({"a":1,"b":2,"c":3,"d":4},{"a":1,"b":2,"c":3,"d":4})
    30
    """
    return sum([dictA.get(tok) * dictB.get(tok, 0) for tok in dictA])


def normalized_tokens(text):
    """
    >>> normalized_tokens("This is getting out of hand")
    ['this', 'is', 'getting', 'out', 'of', 'hand']
    """
    return [token.lower() for token in word_tokenize(text)]


# TODO: Docstring documentation for all member functions (including constructors) Ex.3.2
class TextDocument:
    def __init__(self, text, id=None, full_path=None):
        """
        dictionary token_counts in which the counts of every normalized token is saved
        :param text: text of the document
        :param id: title of the document
        """
        self.text = text
        self.token_counts = FreqDist(normalized_tokens(text))
        self.id = id
        self.full_path = full_path

    @classmethod
    def from_file(cls, filename):
        """Reads a file and returns a TextDocument object with its text as text and filename as id"""
        with open(filename, 'r') as myfile:
            text = myfile.read().strip()
            full_path = os.path.abspath(filename)

        text = text.replace("\n> ", "\n")
        for i in range(0,10):
            text = text.replace("\n> ", "\n")
        text = text.replace("\n", "")
        # NEU: vorher filename als id
        return cls(text, full_path)



class DocumentCollection:
    def __init__(self, term_to_df, term_to_docids, docid_to_doc, docpath_to_doc=None):
        """constructor for DocumentCollection"""

        # string to int; dictionary with tokens as keys and their frequency in the collection as values
        self.term_to_df = term_to_df
        # string to set of string; dictionary with tokens as keys and a list of the doc ids of the docs they appear in as values
        self.term_to_docids = term_to_docids
        # string to TextDocument; dictionary with id as keys and TextDocument object as values
        self.docid_to_doc = docid_to_doc
        # NEU
        # self.docpath_to_doc = docpath_to_doc

    @classmethod
    def from_dir(cls, dir, file_suffix):
        """takes a directory and file suffix, creates and returns a list of TextDocument objects
        of all files with the given suffix in that directory"""
        files = [(dir + "/" + f) for f in os.listdir(dir) if f.endswith(file_suffix)]
        docs = [TextDocument.from_file(f) for f in files]
        return cls.from_document_list(docs)

    @classmethod
    def from_document_list(cls, docs):
        """
        create DocumentCollection object from list of documents, called from from_dir()
        :param docs: list of TextDocument objects
        :return: DocumentCollection object created out of list
        """
        term_to_df = defaultdict(int)
        term_to_docids = defaultdict(set)
        docid_to_doc = dict()
        # NEU
        # docpath_to_doc = dict()
        for doc in docs:
            # dictionary of docs gets doc.id as key and doc as value
            docid_to_doc[doc.id] = doc
            # NEU
            # docpath_to_doc[doc.full_path] = doc
            # go through all tokens of a TextDocument
            for token in doc.token_counts.keys():
                term_to_df[token] += 1
                term_to_docids[token].add(doc.id)

        return cls(term_to_df, term_to_docids, docid_to_doc)

    def docs_with_all_tokens(self, tokens):
        """
        supporting method for the search engine query to find docs that contain all given tokens
        :param tokens: a list of tokens
        :return: list of the TextDocument objects that contain all tokens
        """
        docids_for_each_token = [self.term_to_docids[token] for token in tokens]
        docids = set.intersection(*docids_for_each_token)
        return [self.docid_to_doc[id] for id in docids]

    def tfidf(self, counts):
        """ calculating inverse document frequency for one document
        :param counts: dictionary of the tokens and their count in a TextDocument
        :return: dictionary with token as keys and the inverse document frequency for each term as values
        """
        N = len(self.docid_to_doc)
        return {tok: tf * math.log(N / self.term_to_df[tok]) for tok, tf in counts.items() if tok in self.term_to_df}

    def cosine_similarity(self, docA, docB):
        """calculates the cosine similarity between two documents

        :param docA: TextDocument object A
        :param docB: TextDocument object B
        :return: their cosine similarity
        """
        weightedA = self.tfidf(docA.token_counts)
        weightedB = self.tfidf(docB.token_counts)
        dotAB = dot(weightedA, weightedB)
        normA = math.sqrt(dot(weightedA, weightedA))
        normB = math.sqrt(dot(weightedB, weightedB))

        # Ex 4.1
        if normA * normB == 0:
            return 0

        return dotAB / (normA * normB)


class SearchEngine:
    def __init__(self, doc_collection):
        """
        constructor
        :param doc_collection: the document collection which will be ranked according to the query
        """
        self.doc_collection = doc_collection

    def ranked_documents(self, query):
        """

        :param query: query
        :return: documents ranked by similarity to query according to cosine similarity
        """
        query_doc = TextDocument(query)
        query_tokens = query_doc.token_counts.keys()
        docs = self.doc_collection.docs_with_all_tokens(query_tokens)
        docs_sims = [(doc, self.doc_collection.cosine_similarity(query_doc, doc)) for doc in docs]
       # return sorted(docs_sims, key=lambda x: -x[1])


        # # VORLETZTE
        result = sorted(docs_sims, key=lambda x: -x[1])
        query_tokens_list = list(query_tokens)
        query_tokens_string = " ".join(query_tokens_list)
        query_permutations = [list(zip(x, query_tokens_string)) for x in itertools.permutations(query_tokens_string, len(query_tokens_string))]
        if len(result) == 0 and len(query_tokens_list[1:]) > 0:

            return self.ranked_documents(query_tokens_string[1:])
     #   elif len(self.ranked_documents(query_tokens)) == 0:
     #       return []
        else:
            return result

    def snippets(self, query, document, window=50):
        """

        :param query: the query as string
        :param document: the document as TextDocument
        :param window:
        :return: formated search result
        """
        tokens = normalized_tokens(query)
        text = document.text
        for token in tokens:
            start = text.lower().find(token.lower())
            if -1 == start:
                continue
            end = start + len(token)
            left = "..." + text[start - window:start]
            middle = "[" + text[start: end] + "]"
            right = text[end:end + window] + "..."
            yield left + middle + right
