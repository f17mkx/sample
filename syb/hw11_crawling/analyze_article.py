import urllib.request
from nltk import word_tokenize, pos_tag
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
from collections import defaultdict


def get_html(url):
    return urllib.request.urlopen(url).read().decode("utf-8")


def get_text(html):
    # TODOne create the list of clean paragraphs (no HTML markup) from the given html
    # TODOne return paragraphs as a string. Hint: join the list of paragraphs by newline
    ps = [p.get_text() for p in BeautifulSoup(html, 'html.parser').find_all('p')]
    return '\n'.join(ps)
    # soup = BeautifulSoup(html, 'html.parser')
    # return '\n'.join([line.get_text() for line in soup.find_all('p')])


def get_headline(html):
    # TODOne return the headline of html
    return BeautifulSoup(html, 'html.parser').h1.string
    # soup = BeautifulSoup(html, 'html.parser')
    # return soup.h1.string


def get_normalized_tokens(text):
    # TODOne tokenize the text with NLTK and return list of lower case tokens without stopwords
    return [token.lower() for token in word_tokenize(text) if not token.lower() in stopwords.words('english')]


def get_pos_dict(tokens):
    # TODOne return a dictionary of homographs (a dictionary of words and their possible POS)
    token_to_pos = defaultdict(set)
    [token_to_pos[k].add(v) for k, v in pos_tag(tokens)]
    return dict(token_to_pos)


def filter_dict_homographs(word_dict_h):
    # TODOne delete an entry from dictionary, if not a homograph
    remove = [key for key, value in word_dict_h.items() if len(value) == 1]
    [word_dict_h.pop(i) for i in remove]
    # for w in list(word_dict_h.keys()):
    #     if len(word_dict_h[w]) == 1:
    #         word_dict_h.pop(w)

def find_homographs(tokens):
    # TODOne return a dictionary which holds homographs
    pos_dict = get_pos_dict(tokens)
    filter_dict_homographs(pos_dict)
    return list(pos_dict.keys())