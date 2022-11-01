#!/usr/bin/python3

import sys
from collections import defaultdict


class Node:
    """Klasse fuer die Knoten eines Buchstabenbaumes"""

    # Index des naechsten generierten Knotens
    next_index = 0

    def __init__(self):
        # eindeutigen Knotenindex zuweisen
        self.index = Node.next_index
        self.is_end = False
        self.is_error = False
        Node.next_index += 1

        # Dictionary fuer Kanten zu Tochterknoten initialisieren
        self.target_node = defaultdict(Node)

    def add(self, string):
        ''' rekursive Funktion zum Aufbau des Buchstabenbaumes '''
        if string:
            # Rekursion
            self.target_node[string[0]].add(string[1:])
        else:
            # uebergang mit Leerzeichen als Endemarkierung erzeugen
            self.target_node[' ']
            self.is_end = True

    def print(self):
        visited_list = set()
        Node.print_node(self, visited_list)

    @staticmethod
    def print_node(node, visited_list):
        # track list if already visited
        visited_list.add(node.index)

        if node.is_end:  # add end marker if end state
            print(str(node.index) + '\t \tend ({})'.format(node.target_node[' '].index))

        for edge, target_node in node.target_node.items():
            if not target_node.is_error and not (target_node is node): # if not error or self ref (end)
                print(str(node.index) + '\t' + edge + '\t' + str(target_node.index))
                if target_node.index not in visited_list:  # Ignore visited nodes
                    Node.print_node(target_node, visited_list)


class Hopcroft:
    def __init__(self, root_node: Node):
        # deterministic finite automaton (DFA)
        self.dfa = root_node
        self.alphabets = Hopcroft.get_alphabets(self.dfa)

        self.f = set()  # final states
        self.nf = {self.dfa}  # non-final states. Add root node, since not final state

        self.error = Node()
        self.error.is_error = True
        self.error.target_node = {alphabet: self.error for alphabet in self.alphabets}  # point all to error

        self.nf.add(self.error)  # all error states are not final states
        self.complete(self.dfa)

    @staticmethod
    def get_alphabets(node: Node):
        # iterate the whole tree and collect the complete alphabet list
        alphabet_list = set()  # empty set

        # add all target nodes alphabets in list
        node_alpha = frozenset(node.target_node.keys())
        alphabet_list.update(node_alpha)

        # iterate to all target nodes from given node
        for target_node in node.target_node.values():
            alphabet_list.update(Hopcroft.get_alphabets(target_node))
        return sorted(alphabet_list, key=str)

    def complete(self, node: Node):
        # complete the tree by adding error node on every node
        tn = node.target_node
        for alpha in self.alphabets:
            if node.is_end and alpha == ' ':
                continue
            if alpha in tn:
                target = tn[alpha]
                # check if accepted state (endsymbol ' ')
                if target.is_end:
                    self.f.add(target)
                    target.target_node[' '] = target  # end state stays in end state
                else:
                    self.nf.add(target)
                self.complete(target)
            else:
                tn[alpha] = self.error  # insert error state

    def find_equivalences(self):
        # find equivalent nodes in the same class, and return as a set of sets
        p = {frozenset(self.f), frozenset(self.nf)}
        w = self.minimum(p)
        while w:
            y = w.pop()
            for alpha in self.alphabets:
                for x in p:
                    x1, x2 = self.split(x, alpha, y)
                    if x1 and x2:  # all not 0 -> true
                        p = set.union((p - {x}), {x1, x2})
                        if x in w:
                            w = set.union((w - {x}), {x1, x2})
                        else:
                            w = set.union(w, self.minimum({x1, x2}))
        return p

    @staticmethod
    def split(x, a, y):
        # add existing nodes in x1, and non-existing in x2
        x1 = set()
        x2 = set()
        for node in x:
            if node.target_node[a] in y:
                x1.add(node)
            else:
                x2.add(node)
        return frozenset(x1), frozenset(x2)

    @staticmethod
    def minimum(p):
        # return smaller set from p
        sort_set_by_len = sorted(p, key=lambda x: len(x))
        return {sort_set_by_len[0]}  # return smallest set

    @staticmethod
    def replace(p):
        # replace nodes from the same class with the representative node

        node_dict = defaultdict(Node)
        rep_nodes = []

        # assign every node in the same class, with the first element of the class.
        # get representative node from each class
        for equ_cls in p:
            equ_cls = sorted(equ_cls, key=lambda x: x.index)
            rep = equ_cls[0]
            rep_nodes.append(rep)
            for node in equ_cls:
                node_dict[node] = rep

        # replace all nodes with representative node
        for node in rep_nodes:
            for k, v in node.target_node.items():
                node.target_node[k] = node_dict[v]

        return rep_nodes

    @staticmethod
    def reindex(node_list):
        # reindex the tree in the given order
        sorted_list = sorted(node_list, key=lambda x: x.index)
        i = 0
        for node in sorted_list:
            node.index = i
            i += 1
        return sorted_list


if __name__ == "__main__":  # ./hopcroft.py wordlist
    wordlist = sys.argv[1]
    root = Node()

    with open(wordlist, 'r', encoding='utf-8') as file:
        for word in file:
            root.add(word.rstrip())

    # all modification would apply on the 'root' object
    dfa = Hopcroft(root)  # add to Hopcroft, and complete the tree
    equ_set = dfa.find_equivalences()  # find equivalence classes

    dfa.reindex(dfa.replace(equ_set))  # minimize and reindex the tree

    # print minimized tree = dfa.dfa.print()
    root.print()
