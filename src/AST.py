# Created 2023/07/17
# Author: Caleb Bryant
# Title: AST.py
# Description: This file defines a class to represent a Chronicle parser as an abstract syntax tree. This allows us to check for semantic errors easier. 
# References: https://en.wikipedia.org/wiki/Abstract_syntax_tree

from Tokens import *
from Grammar import Grammar

class AST:
    def __init__(self, tokens):
        self.build_ast(tokens)

    def to_json(self, tokens):
        output = []
        for token in tokens:
            if type(token) == list:
                l = self.to_json(token)
                output.append(l)
            else:
                output.append(token.value)
        return output

class Filter: 
    def __init__(self, keyword, begin, body, end):
        self.keyword = keyword
        self.begin = begin
        self.body = body
        self.end = end

class If:
    def __init__(self, keyword, statement, begin, body, end):
        self.keyword = keyword
        self.statement = statement
        self.begin = begin
        self.body = body
        self.end = end

class ElseIf:
    def __init__(self, keyword, statement, begin, body, end):
        self.keyword = keyword
        self.statement = statement
        self.begin = begin
        self.body = body
        self.end = end

class Else:
    def __init__(self, keyword, begin, body, end):
        self.keyword = keyword
        self.begin = begin
        self.body = body
        self.end = end

class For:
    def __init__(self, keyword, statement, begin, body, end):
        self.keyword = keyword
        self.statement = statement
        self.begin = begin
        self.body = body
        self.end = end

class Function:
    def __init__(self, keyword, begin, config, end):
        self.keyword = keyword
        self.begin = begin
        self.end = end
        config_as_strings = val.value for val in config
        for key in self.config:
            if key in body

    def get_name(self):
        return self.keyword.value

class Grok(Function):
    def __init__(self, keyword, begin, config, end):
        super().__init__(keyword, begin, config, end)
        self.config = {
            "match": None,
            "overwrite": None,
            "on_error": None
        }

class Json(Function):
    def __init__(self, keyword, begin, config, end):
        super().__init__(keyword, begin, config, end)
        self.config = {
            "source" : None,
            "target" : None,
            "array_function" : None,
            "on_error" : None
        }

class Xml(Function):
    def __init__(self, keyword, begin, config, end):
        super().__init__(keyword, begin, config, end)
        self.config = {
            "source" : None,
            "target" : None,
            "xpath" : None,
            "on_error" : None
        }

class Kv(Function):
    def __init__(self, keyword, begin, config, end):
        super().__init__(keyword, begin, config, end)
        self.config = {
            "source" : None,
            "target" : None,
            "field_split" : None,
            "value_split" : None,
            "whitespace" : None,
            "trim_value" : None,
            "on_error" : None
        }

class Csv(Function):
    def __init__(self, keyword, begin, config, end):
        super().__init__(keyword, begin, config, end)
        self.config = {
            "source" : None,
            "target" : None,
            "separator" : None,
            "on_error" : None
        }

class Mutate(Function):
    def __init__(self, keyword, begin, config, end):
        super().__init__(keyword, begin, config, end)
        self.config = {
            "convert" : None,
            "gsub" : None,
            "lowercase" : None,
            "merge" : None,
            "rename" : None,
            "replace" : None,
            "uppercase" : None,
            "remove_field" : None,
            "copy" : None,
            "split" : None,
            "on_error" : None
        }

class Base64(Function):
    def __init__(self, keyword, begin, config, end):
        super().__init__(keyword, begin, config, end)

class Date(Function):
    def __init__(self, keyword, begin, config, end):
        super().__init__(keyword, begin, config, end)

class Drop(Function):
    def __init__(self, keyword, begin, config, end):
        super().__init__(keyword, begin, config, end)

class Statedump(Function):
    def __init__(self, keyword, begin, config, end):
        super().__init__(keyword, begin, config, end)
        