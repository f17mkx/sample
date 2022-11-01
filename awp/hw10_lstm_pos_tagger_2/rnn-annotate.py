#!/usr/bin/env python3

from Data import Data
import argparse

import torch


if __name__ == '__main__':
    '''
    Aufruf .rnn-annotate.py path_param sentences
    '''

    # working run parameters
    # model_store sentences.txt

    parser = argparse.ArgumentParser()
    parser.add_argument("path_param")
    parser.add_argument("sentences")
    args = parser.parse_args()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    data = Data(args.path_param + ".io")  # read the symbol mapping tables
    model = torch.load(args.path_param + ".rnn")  # read the model
    model.to(device)

    for wordlist in data.sentences(args.sentences):
        wordIDs = data.words2IDs(wordlist)
        wordIDs = torch.LongTensor(wordIDs).to(device)  # convert to tensor before sending to GPU
        bestTagIDs = model.annotate(wordIDs)
        bestTags = data.IDs2tags(bestTagIDs)

        for word, tag in zip(wordlist, bestTags):
            print(word, tag)
        print("") # empty line after each sentence (specified in Vorlesung recording 13:10)


