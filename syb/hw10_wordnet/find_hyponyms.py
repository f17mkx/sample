import nltk
from nltk import word_tokenize, sent_tokenize, pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet


class HyponymSearcher(object):
    def __init__(self, path):
        with open(path, 'r') as file:
            text = file.read()
        sentences = sent_tokenize(text)
        tokenized_sentences = [word_tokenize(sentence) for sentence in sentences]
        pos_tokens_ts = [pos_tag(sentence) for sentence in tokenized_sentences]
        wnl = WordNetLemmatizer()
        lemmas = [wnl.lemmatize(token) for sentence in tokenized_sentences for token in sentence]

        # Version, dass der Test läuft #
        tokens = word_tokenize(text)
        pos_tokens = pos_tag(tokens)
        self.noun_lemmas = [token for token, tag in pos_tokens if tag.startswith('N')]
        #############ENDE################

        # Richtige Lösung
        self.noun_lemmas = [wnl.lemmatize(token)
                            for sentence in pos_tokens_ts
                            for (token, pos) in sentence if pos.startswith('N')]

    def hypernymOf(self, synset1, synset2):
        if synset1 == synset2:
            return True
        for element in synset1.hypernyms():
            if element == synset2:
                return True
            elif self.hypernymOf(element, synset2):
                return True
        return False

    def get_hyponyms(self, hypernym):
        return [noun for noun in self.noun_lemmas if
                any([self.hypernymOf(synset, hypernym)
                     for synset in wordnet.synsets(noun) if self.hypernymOf(synset, hypernym)])]
