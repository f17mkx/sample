from unittest import TestCase
import os

from hw04_text_search.text_vectors import TextDocument, DocumentCollection, SearchEngine


class DocumentCollectionTest(TestCase):

    def setUp(self):
        test_doc_list = [TextDocument(text_and_id[0], text_and_id[1]) for text_and_id in
                         [("the cat sat on a mat", "doc1"),
                          ("a rose is a rose", "doc2")]]
        self.small_collection = DocumentCollection.from_document_list(test_doc_list)

        # TODO: uncomment in case tests need access to whole document collection.
        # this_dir = os.path.dirname(os.path.abspath(__file__))
        # document_dir = os.path.join(this_dir, os.pardir, 'data/enron/enron1/ham/')
        # self.large_collection = DocumentCollection.from_dir(document_dir, ".txt")

    def test_unknown_word_cosine(self):
        """ Return 0 if cosine similarity is called for documents with only out-of-vocabulary words. """
        # Document that only contains words that never occurred in the document collection.
        query_doc = TextDocument(text="unknownwords", id=None)
        # Some document from collection.
        collection_doc = self.small_collection.docid_to_doc["doc1"]
        # Similarity should be zero (instead of undefined).
        self.assertEqual(self.small_collection.cosine_similarity(query_doc, collection_doc), 0.)


class TextDocumentTest(TestCase):
    # TODO: Unittests for TextDocument go here.

    def setUp(self):
        test_doc_list = [TextDocument(text_and_id[0], text_and_id[1]) for text_and_id in
                         [("the cat sat on a mat", "doc1"),
                          ("a rose is a rose", "doc2")]]
        self.small_collection = DocumentCollection.from_document_list(test_doc_list)
        this_dir = os.path.dirname(os.path.abspath(__file__))
        document_dir = os.path.join(this_dir, os.pardir, 'data/enron/enron1/ham/')
        self.large_collection = DocumentCollection.from_dir(document_dir, ".txt")
        self.searcher = SearchEngine(self.large_collection)

    def test_no_newlines(self):

        for doc in self.large_collection.docid_to_doc.values():
            find = doc.text.find("\n")
            self.assertEqual(find, -1)

    def test_no_indentation_marks(self):

        for doc in self.large_collection.docid_to_doc.values():
            find = doc.text.find("\n> ")
            self.assertEqual(find, -1)

    def test_no_with_all_tokens(self):

        query = "test ham"
        len_top_docs = len(self.searcher.ranked_documents(query))
        long_enough = len_top_docs > 0
        self.assertEqual(long_enough, True)

    def test_absolute_path(self):

        # does not work because the provided setup method uses the full path as a file id.
        # would work otherwise
        for path in self.large_collection.docid_to_doc.keys():

            if path[:5] == "data/":
                self.fail()

        """
        collection_doc_ids = self.large_collection.docid_to_doc.keys()
        collection_doc_paths = self.large_collection.docpath_to_doc.keys()

        # iterate over doc_ids and full_paths at the same time
        for doc_id, full_path in zip(collection_doc_ids, collection_doc_paths):
            full_path_through_docid = os.path.abspath(doc_id)
            self.assertEqual(full_path_through_docid, full_path)
        """


class SearchEngineTest(TestCase):
    # TODO: Unittests for SearchEngine go here.
    # test für full path: gucken, ob dingens mit data anfängt
    pass
