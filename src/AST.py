# Created 2023/07/17
# Author: Caleb Bryant
# Title: AST.py
# Description: This file defines a class to represent a Chronicle parser as an abstract syntax tree. This allows us to check for semantic errors easier. 
# References: https://en.wikipedia.org/wiki/Abstract_syntax_tree

from Tokens import *
from Grammar import Grammar

class AST:
    def __init__(self, tokens):
        self.tokens = tokens

    def recurse_ast(self, tokens):
        for token in tokens:
            if type(token) == list:
                self.recurse_ast(token)
            elif type(token) == PluginToken:
                if token.value == "grok":
                    # do stuff
                elif token.value == "json":
                    # do stuff
                elif token.value == "xml":
                    # do stuff
                elif token.value == "kv":
                    # do stuff
                elif token.value == "csv":
                    # do stuff
                elif token.value == "mutate":
                    # do stuff
                elif token.value == "base64":
                    # do stuff
                elif token.value == "date":
                    # do stuff
                elif token.value == "drop":
                    # do stuff
                elif token.value == "statedump":
                    # do stuff
                else:
                    raise ValueError
            elif type(token) == ConfigOptionToken:
                if token.value == "convert":
                    # do stuff
                elif token.value == "gsub":
                    # do stuff
                elif token.value == "lowercase":
                    # do stuff
                elif token.value == "merge":
                    # do stuff
                elif token.value == "rename":
                    # do stuff
                elif token.value == "replace":
                    # do stuff
                elif token.value == "uppercase":
                    # do stuff
                elif token.value == "remove_field":
                    # do stuff
                elif token.value == "copy":
                    # do stuff
                elif token.value == "split":
                    # do stuff
                else:
                    raise ValueError

    def check_ast(self):
        results = self.recurse_ast(self.tokens)

    def to_json(self, tokens):
        output = []
        for token in tokens:
            if type(token) == list:
                l = self.to_json(token)
                output.append(l)
            else:
                output.append(token.value)
        return output