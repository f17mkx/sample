import nltk


def normalized_tokens(text):
    """ This takes a string and returns lower-case tokens, using nltk for tokenization. """
    low = text.lower()
    return nltk.word_tokenize(low)  # TODOne: return list with lower-case tokens.


def make_dict(text):
    word_count_dict = {}
    tokens = normalized_tokens(text)
    for x in tokens:
        if x in word_count_dict:  # count +1
            word_count_dict[x] += 1
        else:  # make new entry
            word_count_dict[x] = 1
    return word_count_dict

class TextDocument:
    def __init__(self, text, id=None):
        """ This creates a TextDocument instance with a string, a dictionary and an identifier. """
        self.text = text
        # TODOne: Create dictionary that maps words to their counts.
        self.word_to_count = make_dict(text)
        self.id = id

    @classmethod  # TODOne: Was heißt @classmethod + cls?
    # cls is referring to the class whereas self is referring to an instance of a class
    def from_file(cls, filename):
        """ This creates a TextDocument instance by reading a file. """
        f = open(filename, "r")  # TODOne: read text from filename
        text = f.read()
        return cls(text, filename)

    def __str__(self):
        """ This returns a short string representation, which is at most 25 characters long.
        If the original text is longer than 25 characters, the last 3 characters of the short string should be '...'.
        """
        if len(self.text) > 25:
            return self.text[0:22] + "..."

        return self.text  # TODOne: Implement correct return statement.

    def word_overlap(self, other_doc):
        """ This returns the number of words that occur in both documents (self and other_doc) at the same time.
        Every word should be considered only once, irrespective of how often it occurs in either document (i.e. we
        consider word *types*).
        """
        count = 0
        for x in self.word_to_count:
            if x in make_dict(other_doc.text):
                count += 1
        return count  # TODOne: Implement correct return statement.
