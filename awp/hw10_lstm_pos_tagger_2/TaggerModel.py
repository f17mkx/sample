
import torch
from torch import nn



class TaggerModel(nn.Module):
    def __init__(self, numWords, numTags, embSize, rnnSize, hiddenSize, dropoutRate):
        super().__init__()
        self.word_embeddings = nn.Embedding(numWords + 1, embSize)
        self.lstm = nn.LSTM(input_size=embSize, hidden_size=rnnSize, bidirectional=True)
        self.linear1 = nn.Linear(rnnSize * 2, hiddenSize) # bidirektionalen LSTMs besitzen die doppelte Laenge.
        self.linear2 = nn.Linear(hiddenSize, numTags)
        self.dropout = nn.Dropout(dropoutRate)

    def forward(self, sentence):
        embeds = self.word_embeddings(sentence)
        embeds_drop = self.dropout(embeds)

        lstm_out, _ = self.lstm(torch.unsqueeze(embeds_drop, dim=1))
        lstm_drop = self.dropout(lstm_out)

        tag_space = self.linear1(torch.squeeze(lstm_drop, dim=1))
        tag_space = self.linear2(tag_space)

        return tag_space

    def annotate(self, wordIDs):
        # return tags with the highest score
        outputs = self(wordIDs)
        return outputs.max(1).indices.tolist()


def run_test():
    # init model with test values
    numWords, numTags, embSize, rnnSize, hiddenSize, dropoutRate = 50, 50, 50, 50, 512, 0.3
    model = TaggerModel(numWords, numTags, embSize, rnnSize, hiddenSize, dropoutRate)

    # generate random input & label
    tensor_input = torch.LongTensor(torch.randint(0, 50, (6,)))
    tensor_label = torch.LongTensor(torch.randint(0, 50, (6,)))

    # Test model with random input, and get loss value
    tagScores = model(tensor_input)
    criterion = nn.CrossEntropyLoss()
    loss = criterion(tagScores, tensor_label)
    # loss.backward()
    print("Loss: ", loss.item())


if __name__ == "__main__":
    run_test()
