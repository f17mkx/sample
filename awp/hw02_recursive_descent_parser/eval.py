# !/usr/bin/env python3

import sys


class RecursiveDecentParser:
    def __init__(self, expr):
        self.iserror = False
        # indicates wether there was an error processing so no result will be printed
        self.inbracket = False
        # indicates wether we are currently in a bracket to detect wrong ')' as in 4)-3
        self.expr = expr.replace(' ', '')
        self.int_dict = {str(num): num for num in range(10)}
        self.operators = ['+', '-', '*', '/', '.', '(', ')']
        # list of possible symbolys besides numbers to throw error if anything else occurrs

    def start(self):
        result, endpos = self.addexpr()
        if not self.iserror:
            # if there was no error thrown, print result
            print(self.expr, '=', round(result, 2))

    def addexpr(self, startpos=0):
        num, endpos = self.mulexpr(startpos)
        while self.expr[endpos] in ['+', '-'] and not self.expr.endswith('\t'):
            # '\t' signals the expr is fully processed (eigther with or without error) no need to go on from here
            if self.expr[endpos] == '+' and not endpos == len(self.expr) - 1:
                # circle out '+' at the end of expression
                num2, endpos = self.mulexpr(endpos + 1)
                num = num + num2
            elif self.expr[endpos] == '-' and not endpos == len(self.expr) - 1:
                # cirlce out '-' at the end of expression
                num2, endpos = self.mulexpr(endpos + 1)
                num = num - num2
            else:
                self.error(endpos)
                # throws error if '+' or '-' at the end of expression
        if self.expr[endpos] == ')' and not self.inbracket:
            # catch random ')' that is not closing a bracketexpression
            self.error(endpos)
            return 1, startpos
            # 1 and startpos are just placeholders at this point. The same holds true for any errors below
        return num, endpos

    def mulexpr(self, startpos):
        num, endpos = self.bracketexpr(startpos)
        while self.expr[endpos] in ['*', '/'] and not self.expr.endswith('\t'):
            if self.expr[endpos] == '*' and not endpos == len(self.expr) - 1:
                # cirlce out '*' at the end of expression
                num2, endpos = self.bracketexpr(endpos + 1)
                num = num * num2
            elif self.expr[endpos] == '/' and not endpos == len(self.expr) - 1:
                # cirlce out '/' at the end of expression
                num2, endpos = self.bracketexpr(endpos + 1)
                if num2 == 0:
                    # catch divison by 0, throw error
                    self.error(endpos, zero=True)
                else:
                    num = num / num2
            else:
                self.error(endpos)
                # throws error if '*' or '/' at the end of expression
        return num, endpos

    def bracketexpr(self, startpos):
        if self.expr[startpos] == '(':
            self.inbracket = True
            # we are in a bracket now and do not throw an error for ')'
            num, endpos = self.addexpr(startpos + 1)
            if self.expr[endpos] != ')':
                self.error(endpos)
            if endpos == len(self.expr) - 1:
                self.expr += '\t'
                # signal the end of processing with '\t' for ')' at the end of expression like 123+(99/11)
            self.inbracket = False
            # reset self.inbracket to default after coming out of the bracket
            return num, endpos + 1
        elif self.expr[startpos] == '-':
            if startpos == len(self.expr) - 1:
                # throw error for '-' within bracketexpr end of statement like 80-60--
                self.error(startpos)
                return 1, startpos
            num, endpos = self.bracketexpr(startpos + 1)
            return -num, endpos
        else:
            return self.number(startpos)

    def number(self, startpos):
        num, startpos = self.integer(startpos)
        if self.expr[startpos] != '.':
            return num, startpos
        num2, endpos = self.integer(startpos + 1)
        num = num + num2 * 10 ** -(endpos - startpos - 1)
        return num, endpos

    def integer(self, startpos):
        if self.expr[startpos] not in self.int_dict.keys():
            # throw error if self.expr[startpos] is not a number
            self.error(startpos)
            return 1, startpos
        num = self.int_dict[self.expr[startpos]]
        # assign num the int value of self.expr[startpos] by referencing self.int_dict
        if startpos < len(self.expr) - 1:
            # if we didnt reach the end of expr..
            if self.expr[startpos + 1] in self.int_dict.keys():
                # if the next item is a number..
                num2, endpos = self.integer(startpos + 1)
                # get said number from calling self.integer with the next position
                num = (num * 10 ** (endpos - startpos - 1)) + num2
                # the num2 from recursion times 10 to the power of as many numbers there were found:
                # 123 = 1*10^2 + 2*10^1 + 3*10^0
                return num, endpos
            if self.expr[startpos + 1] not in self.operators:
                # throw error if the next element is not in our laguage
                # 9?
                self.error(startpos + 1)
                return 1, startpos
        if startpos == len(self.expr) - 1:
            # mark expr with '\t' to signal the end of the expression for other functions to abort
            self.expr += '\t'
        return num, startpos + 1

    def error(self, pos, zero=False):
        if self.iserror:
            # dont print out another error message if there already was an error raised
            return
        if zero:
            # zero divison error
            print('division by 0: cannot calculate', self.expr)
        else:
            print('Fehler in arithmetischem Ausdruck:', self.expr)
            print(' ' * (pos + 34), '^')
        self.iserror = True
        # set iserror to true for start() not to print the result
        self.expr += '\t'
        # mark expr with '\t' to signal the end of the expression


with open('equations.txt', 'r') as file:
    # with open(sys.argv[1], 'r') as file:
    for equation in file:
        equation = equation.replace('\n', '')
        equation = RecursiveDecentParser(equation)
        equation.start()
        del equation
