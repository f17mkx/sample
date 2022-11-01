import nltk


class LangModeler(object):
    def __init__(self, languages, words):
        self.languages = languages
        self.words = words

    def build_language_models(self):
        return nltk.ConditionalFreqDist((language, word.lower())
                                        for language in self.languages for word in self.words[language])

    def guess_language(self, language_model_cfd, text):
        """Returns the guessed language for the given text"""
        language_max = 0
        score_max = 0
        for language in language_model_cfd.conditions():
            score = 0
            for word in text.split():
                word = word.lower()
                score += language_model_cfd[language].freq(word)
            if score > score_max:
                language_max, score_max = language, score
        return language_max
