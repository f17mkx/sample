#!/usr/bin/python3

import numpy as np
import sys


class Levenshtein:
    def __init__(self, string_1, string_2):
        self.str1 = string_1
        self.str2 = string_2
        self.n = len(string_1)
        self.m = len(string_2)

        # for storing the alignment strings (eg. a:a, e:i)
        self.alignment = []

        self.table = np.empty((self.n + 1, self.m + 1), dtype=int)

        # make first row number from 0 to length of string
        self.table[0] = np.arange(self.m + 1)

        # make first column number from 0 to length of string
        self.table[:, 0] = np.arange(self.n + 1)

        # fill the table with the distances
        self.compute_distance()

        # find the alignments (result will be in reversed order)
        self.find_alignments(self.n, self.m)

        # put alignments in right order
        self.alignment.reverse()

        print(f'{self.str1} -> {self.str2}: {self.table[self.n, self.m]} \n'
              f'{" ".join(self.alignment)} \n')

    def get_best_op(self, i, k):
        # calculate which operation (replace, insert, delete, ignore) yields the best score
        # for position i,k in the table

        if self.str1[i - 1] != self.str2[k - 1]:
            # replace
            x = self.table[i - 1, k - 1] + 1
        else:
            # ignore
            x = self.table[i - 1, k - 1]

        y = self.table[i - 1, k] + 1
        # delete

        z = self.table[i, k - 1] + 1
        # insert

        return min([x, y, z])  # return the result of the best operation

    def find_alignments(self, i, k):
        # find the alignments

        if i != 0 or k != 0:
            # if the functions has not reached field 0,0 in the table yet
            best_prev = min([self.table[i - 1, k - 1], self.table[i - 1, k], self.table[i, k - 1]])
            # the value that the current position was derived from

            if self.table[i - 1, k - 1] == best_prev:
                # if the operation was ignore or replace
                align = f' {self.str1[i - 1]}:{self.str2[k - 1]}'
                i -= 1
                k -= 1

            elif self.table[i, k - 1] == best_prev:
                # if the operation was insert
                align = f' :{self.str2[k - 1]}'
                k -= 1

            else:  # if table[i-1,k] == best_prev:
                # if the operation was delete
                align = f' {self.str1[i - 1]}:'
                i -= 1

            # add to "alignment list
            self.alignment.append(align)

            # find the next previous operation
            self.find_alignments(i, k)

    def compute_distance(self):
        for i in range(1, self.n + 1):
            # for each row, not including the first because it is already initialized
            for k in range(1, self.m + 1):
                # for each column, not including the first because it is already initialized
                self.table[i, k] = self.get_best_op(i, k)
                # calculate the lowest distance of the current prefixes


if __name__ == '__main__':
    with open(sys.argv[1]) as wordlist:
        # read word list
        for line in wordlist:
            # for each word pair
            str1, str2 = line.split()
            Levenshtein(str1, str2)
