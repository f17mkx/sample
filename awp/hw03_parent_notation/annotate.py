# !/usr/bin/env python3

import sys
import re


class Node:
    def __init__(self, arg):
        self.iserror = False  # error parameter to stop further processing if an error occurred

        self.label = str()
        self.feature = str()
        self.trace_id = 0
        self.filler_id = 0

        # assign label, feature, and id attributes
        self.trace_list = list()
        self.filler_list = list()

        # assign list of trace ids and filler ids for raising error, if lists dont match
        self.children = list()

        if type(arg) is str:

            # create first class instance from string
            p = re.compile(r' +\(')
            self.parse = p.sub('(', arg)

            # remove ' ' prior to '('
            if not self.parse.endswith('\n'):
                self.parse += '\n'
            self.endpos = 0
            self.parent = None

            # raise error if parse doesnt start with '(' like  S(NP(...
            if self.parse[0] != '(':
                self.error()

        else: # arg is instance of Node, and is parent
            self.parent = arg
            self.parse = arg.parse
            self.endpos = arg.endpos

        if not self.iserror:
            if self.parse[self.endpos] == '(':
                self.read_label()
                while self.parse[self.endpos] != ')' and not self.iserror:
                    child = Node(self)

                    self.children.append(child)
                    self.iserror = child.iserror

                    # update trace and filler list to be compared later
                    self.trace_list.extend(child.trace_list)
                    self.filler_list.extend(child.filler_list)

                    if self.iserror:
                        # in error(): self.endpos = len(self.parse)-1 := no need to go further
                        self.endpos = child.endpos

                    else: # self.parse[child.endpos] = ')' -> '+1' to go on
                        self.endpos = child.endpos + 1

                        # Error if (S(NP hey)  := missing '(',')' after child
                        if not self.parse[self.endpos] in ['(', ')']:
                            self.error()
            else:
                self.read_label()

            # analyse whole tree only if you are in highest Node
            if type(arg) is str and not self.iserror:

                # check whether the same traces and fillers were found
                if sorted(self.trace_list) != sorted(self.filler_list):
                    self.error(f'Input Error: TraceID and FillerID count not matching: {self.parse[:-1]}')

                # if it finished parent annotation but the input is not finished
                elif self.parse[self.endpos+1] != '\n':
                    self.endpos += 1
                    self.error()

                # raise error if there are no childeren in highest node
                elif len(self.children) == 0:
                    self.error()

                else: # find filler and trace path
                    self.add_trace_features(self.parse)

    def read_label(self):
        try: # to stop processing as soon as an error is found
            parse = self.parse

            if parse[self.endpos] == '(':  # read label of non-terminal
                self.endpos += 1

                if parse[self.endpos] == '(':  # error if ((ABC def)
                    raise ValueError

                while parse[self.endpos] not in [' ', '(']:
                    if parse[self.endpos] == ')':  # error if (ABC)
                        raise ValueError
                    self.label += parse[self.endpos]
                    self.endpos += 1

                    if self.endpos == len(parse):  # error if (abc
                        raise ValueError

                if parse[self.endpos+1] == ')':  # error if (abc ) <- with space
                    self.error()

            else: # read label of terminal
                self.endpos += 1

                while parse[self.endpos] not in [' ', '(', ')']:
                    self.label += parse[self.endpos]
                    self.endpos += 1

                    if self.endpos == len(parse):  # error if (ABC def
                        raise ValueError

                if parse[self.endpos] in [' ', '(']:  # error if (ABC def ) or (ABC def(
                    raise ValueError

                self.endpos -= 1

            # if trace id exists, extract and store in list to compare in search
            if re.match('^.*\*-\d+$', self.label):
                self.trace_id = int(re.findall('^.*?-(\d+)$', self.label)[0])
                self.trace_list.append(self.trace_id)

            # find filler id exists, extract and store in list to compare in search
            elif re.match('^.+-\d+$', self.label):
                self.filler_id = int(re.findall('^.*?-(\d+)$', self.label)[0])
                self.filler_list.append(self.filler_id)

            # keep label without filler or tracer id
            self.label = re.findall('^(.*?)(?=-\d+$|$)', self.label)[0]

        # print error message if syntax error in input
        except ValueError:
            self.error()

    def add_trace_features(self, parse):
        # recursively search tree for fillers
        for child in self.children:
            if child.add_trace_features(parse) or child.filler_id:
                child.annotate_trace_up(child.filler_id, child.label)


    def annotate_trace_up(self, filler_id, feature):
        # Recursively annotate the children from a node up (parent children)
        self.feature = '\\' + feature
        for child in self.parent.children:
            if child != self and child.annotate_trace_down(filler_id, feature):
                return True
        self.parent.annotate_trace_up(filler_id, feature)


    def annotate_trace_down(self, filler_id, feature):
        # Recursively annotate the children of traces from top down
        for child in self.children:
            if child.annotate_trace_down(filler_id, feature) or child.trace_id == filler_id:
                self.feature = '/' + feature
                return True
        return False


    def error(self, custom_message=None):
        # prevent from printing duplicate error message
        if self.iserror:
            return

        if not custom_message:  # syntax error
            print('Input Error! Rest of the string: ', self.parse[self.endpos:-1])

        else: # missing filler or trace error
            print(custom_message)

        self.endpos = len(self.parse)-1
        self.iserror = True


    def __str__(self):
        if self.iserror:
            # if an error was found during processing
            return 'Input Error: could not generate parse tree\n'

        if not self.children:
            # if terminal was reached
            return self.label

        else:
            children = ' '.join([child.__str__() for child in self.children if child.__str__() != ''])
            parent = self.parent.label if isinstance(self.parent, Node) else 'NONE'
            return '(' + self.label + '-' + parent + self.feature + ' ' + children + ')'


if __name__ == '__main__':
    with open(sys.argv[1], 'r') as file:
        for line in file:
            root = Node(line)
            print(root)
