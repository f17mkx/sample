from nltk import word_tokenize, sent_tokenize, pos_tag
import nltk


class Sentences:
    def __init__(self, tagged_sentences):
        """Construct and instance of the class Sentence from a list of
        pos-tagged sentences ([[(word,tag),...],...])"""
        self.sentences = tagged_sentences

    def __iter__(self):
        return iter(self.sentences)

    def __getitem__(self, i):
        return self.sentences[i]

    @classmethod
    def from_file(cls, path):
        """Create an instance of the class Sentences from a
        path. Reads the file and pos-tags the sentences in the
        file. [2 point]"""
        with open(path, mode='r', encoding='utf-8') as file:
            text = file.read()
        sentences = nltk.sent_tokenize(text)
        return cls([nltk.pos_tag(nltk.word_tokenize(sentence)) for sentence in sentences])


class PosExpr:
    def __init__(self, expressions):
        """Construct an instance of the class PosExpr from a list of
        expressions."""
        self.expressions = expressions

    @classmethod
    def from_string(cls, expr):
        """Create an instance of the class PosExpr from the given
        string.  [0 points]"""
        return cls(expr.split(' '))
        # return cls([expression for expression in expr.split()])

    @staticmethod
    def match_expr(expr, pos):
        """This method returns True if expr matches pos. An expression
        'XX' matches if pos equals 'XX', the expression '*' matches
        any pos and an expression XX* matches if pos starts with 'XX'
        or is equal to 'XX'.  [2 points]"""
        if expr.endswith('*'):
            return pos.startswith(expr[:-1])
        else:
            return expr == pos

    def matches(self, sentence):
        """This method returns the list of matches in a pos-tagged
        sentence (list of (word,pos)-pairs). A match is a list of
        (word, pos)-pairs, where the tags in the sentence matched the
        expression mask provided by PosExpr for all possible
        positions.  [4 points]"""
        matches = list()
        for i in range(len(sentence)):
            tag = sentence[i][1]
            matched_expressions = []
            for j in range(len(self.expressions)):
                if PosExpr.match_expr(self.expressions[j], tag) and (i+j+1 < len(sentence)):
                    matched_expressions.append(tag)
                    tag = sentence[i + j:][1][1]
            if len(self.expressions) == len(matched_expressions):
                matched_sequence = [sentence[i + j] for j in range(len(self.expressions))]
                matches.append(matched_sequence)
        return matches


def find(sentences, expr):
    """Return a list of strings that match the given expression. E.g.
    `find_string(sentences, "JJ NN") should return the list
    [...,"prior year",...].  [2 points]"""
    matches = [m for s in sentences for m in PosExpr.from_string(expr).matches(s)]
    return [' '.join([element[0] for element in match]) for match in matches]
