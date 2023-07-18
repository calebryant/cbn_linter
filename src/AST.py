# Created 2023/07/17
# Author: Caleb Bryant
# Title: AST.py
# Description: This file defines a class to represent a Chronicle parser as an abstract syntax tree. This allows us to check for semantic errors easier. 
# References: https://en.wikipedia.org/wiki/Abstract_syntax_tree

from Tokens import *
from Grammar import function_enums, filter_enums

class AST:
    def __init__(self, tokens):
        self.kind = tokens[0]
        self.start = tokens[1]
        self.end = tokens[-1]
        self.branches = []

class Function(AST):
    def __init__(self, tokens):
        for token_list in tokens:
            self.kind = token_list[0]
            if type(self.kind) == FunctionToken:
                self.assign = tokens[1]
                self.start = tokens[2]
                self.end = tokens[-1]
                self.branches.append(build_tree(tokens[3:-1]))
            if type(self.kind) == StringToken:

            if type(self.kind) == IDToken:

    def build_tree(self, tokens):
        return_value = []


class Plugin(AST):
    def __init__(self, tokens):
        super().__init__(tokens)
        self.branches.append(build_tree(tokens[2:-1]))

    def build_tree(self, tokens):
        return_value = []
        for token_list in tokens:
            if type(token_list[0]) == FunctionToken:
                return_value.append(Function(tokens))

class Filter(AST):
    def __init__(self, tokens):
        super().__init__(tokens)
        self.branches = build_tree(tokens[2:-1])
    
    def build_tree(self, tokens):
        return_value = []
        for token_list in tokens:
            # At this level, there are 5 types of tokens we can expect to see: plugin, if, elif, else, for
            if type(token_list[0]) == PluginToken:
                return_value.append(Plugin(token_list))
            elif type(token_list[0]) == IfToken:
            
            elif type(token_list[0]) == ElseIfToken:

            elif type(token_list[0]) == ElseToken:
            
            elif type(token_list[0]) == ForToken:

            else:
                print(f"Invalid token: {token_list[0]}")