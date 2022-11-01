#!/usr/bin/python3

import sys
import torch
from torch import nn

import Data


class TaggerModel(nn.Module):
    def __init__(self, numWords, numTags, embSize, rnnSize, hiddenSize, dropoutRate):
        super().__init__()
        self.word_embeddings = nn.Embedding(numWords + 1, embSize)
        self.lstm = nn.LSTM(input_size=embSize, hidden_size=hiddenSize, num_layers=rnnSize, bidirectional=True)
        self.hidden2tag = nn.Linear(hiddenSize * 2, numTags)  # bidirektionalen LSTMs besitzen die doppelte Laenge.
        self.dropout = nn.Dropout(dropoutRate)

    def forward(self, sentence):
        embeds = self.word_embeddings(sentence)
        embeds_drop = self.dropout(embeds)

        lstm_out, _ = self.lstm(torch.unsqueeze(embeds_drop, dim=1))
        lstm_drop = self.dropout(lstm_out)

        tag_space = self.hidden2tag(torch.squeeze(lstm_drop, dim=1))

        return tag_space

    def annotate(self):
        # spaeter implementieren.
        pass


def run_test():
    # init model with test values
    numWords, numTags, embSize, rnnSize, hiddenSize, dropoutRate = 50, 50, 50, 50, 512, 0.3
    tagger = TaggerModel(numWords, numTags, embSize, rnnSize, hiddenSize, dropoutRate)

    # generate random input & label
    tensor_input = torch.LongTensor(torch.randint(0, 50, (6,)))
    tensor_label = torch.LongTensor(torch.randint(0, 50, (6,)))

    # Test model with random input, and get loss value
    tagScores = tagger(tensor_input)
    criterion = nn.CrossEntropyLoss()
    loss = criterion(tagScores, tensor_label)
    # loss.backward()
    print("Loss: ", loss.item())


if __name__ == "__main__":
    run_test()
