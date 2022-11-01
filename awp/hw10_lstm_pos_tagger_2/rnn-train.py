#!/usr/bin/env python3

from Data import Data
from TaggerModel import TaggerModel

from numpy import random
import numpy as np
import torch
from torch import nn, optim
import argparse


def train(trainSentences, loss_function, optimizer):
    model.train(True)

    for words, tags in trainSentences:
        model.zero_grad()

        wordIDs = data.words2IDs(words)
        wordIDs = torch.LongTensor(wordIDs).to(device)  # convert to tensor before sending to GPU

        tagIDs = data.tags2IDs(tags)
        tagIDs = torch.LongTensor(tagIDs).to(device)  # convert to tensor before sending to GPU

        outputs = model(wordIDs)

        loss = loss_function(outputs, tagIDs)
        loss.backward()
        optimizer.step()

def evaluate(devSentences):
    model.train(False)

    ground_truth = []
    prediction = []

    # compare prediction with tag label
    with torch.no_grad():
        for words, tags in devSentences:
            wordIDs = data.words2IDs(words)
            wordIDs = torch.LongTensor(wordIDs).to(device)  # convert to tensor before sending to GPU
            bestTagIDs = model.annotate(wordIDs)
            prediction_tags = data.IDs2tags(bestTagIDs)
            ground_truth += tags
            prediction += prediction_tags

    correct_pred = np.array(prediction) == np.array(ground_truth)
    accuracy = sum(correct_pred) / len(correct_pred)
    return accuracy


if __name__ == "__main__":
    '''
    train.tagged dev.tagged model_store --num_epochs=20 --num_words=10000 
    --emb_size=200 --hidden_size=512 --rnn_size=200 --dropout_rate=0.5 --learning_rate=0.5
    
    example_train_file.txt example_test_file.txt model_store --num_epochs=20 --num_words=10000 
    --emb_size=200 --hidden_size=512 --rnn_size=200 --dropout_rate=0.5 --learning_rate=0.5
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument("trainfile")
    parser.add_argument("devfile")
    parser.add_argument("path_param")

    parser.add_argument("--num_epochs", type=int, default=20)
    parser.add_argument("--num_words", type=int, default=10000)
    parser.add_argument("--emb_size", type=int, default=200)
    parser.add_argument("--rnn_size", type=int, default=200)
    parser.add_argument("--hidden_size", type=int, default=512)
    parser.add_argument("--dropout_rate", type=float, default=0.5)
    parser.add_argument("--learning_rate", type=float, default=0.5)
    args = parser.parse_args()

    data = Data(args.trainfile, args.devfile, args.num_words)
    data.store_parameters(args.path_param + '.io')

    model = TaggerModel(args.num_words, data.numTags, args.emb_size, args.rnn_size, args.hidden_size, args.dropout_rate)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    optimizer = optim.SGD(model.parameters(), lr=args.learning_rate)
    # optimizer = optim.Adam(model.parameters(), lr=args.learning_rate)  # Adam als Optimizer
    loss_function = nn.CrossEntropyLoss()

    acc_max = 0
    for epoch in range(args.num_epochs):
        random.shuffle(data.trainSentences)
        train(data.trainSentences, loss_function, optimizer)
        acc = evaluate(data.devSentences)

        if acc > acc_max:
            torch.save(model, args.path_param + '.rnn')
            acc_max = acc
        print(f"{epoch} epoch accuracy: {acc}")

    print(f"best accuracy: {acc_max}")