# Created 2023/07/17
# Author: Caleb Bryant
# Title: AST.py
# Description: This file defines a class to represent a Chronicle parser as an abstract syntax tree. This allows us to check for semantic errors easier. 
# References: https://en.wikipedia.org/wiki/Abstract_syntax_tree

from Tokens import *

class AST:
    def __init__(self, filter_object):
        self.filter = filter_object
        self.value_table = dict()

    def to_json(self):
        return

class Block: 
    def __init__(self, config):
        if type(config[1]) == LBraceToken:
            self.config = {
                "keyword": config[0],
                "statement": None,
                "begin": config[1],
                "body": config[2:-1],
                "end": config[-1]
            }
        else:
            self.config = {
                "keyword": config[0],
                "statement": config[1],
                "begin": config[2],
                "body": config[3:-1],
                "end": config[-1]
            }

class Filter(Block):
    def __init__(self, config):
        super().__init__(config)

class If(Block):
    def __init__(self, config):
        super().__init__(config)

class ConditionalToken:
    def __init__(self,tokens):
        self.tokens = tokens
        
    def get_name(self):
        name = []
        for token in self.tokens:
            if type(token) == TokenToken:
                name.append(token.value)
        return '.'.join(name)

class ConditionalStatement:
    def __init__(self,tokens):
        self.value = tokens

class ElseIf(Block):
    def __init__(self, config):
        super().__init__(config)

class Else(Block):
    def __init__(self, config):
        super().__init__(config)

class For(Block):
    def __init__(self, config):
        super().__init__(config)

class LoopStatement:
    def __init__(self, tokens):
        self.statement = tokens

class Function:
    def __init__(self, config):
        self.config = {
            "keyword": config[0],
            "begin": config[1],
            "config": config[2:-1],
            "end": config[-1]
        }

    def get_name(self):
        return self.config["keyword"].value

class FunctionConfig:
    def __init__(self, config):
        self.config = {
            "keyword": config[0],
            "assign": config[1],
            "value": config[2],
            "comma": config[-1] if type(config[-1]) == CommaToken else None
        }

class Hash:
    def __init__(self, config):
        self.config = {
            "begin": config[0],
            "pairs": config[1:-1],
            "end": config[-1]
        }

class List:
    def __init__(self, config):
        self.config = {
            "begin": config[0],
            "values": config[1:-1],
            "end": config[-1]
        }

class KeyValue:
    def __init__(self, config):
        config = {
            "l_val": config[0],
            "assign": config[1],
            "r_val": config[2],
            "comma": config[-1] if type(config[-1]) == CommaToken else None
        }

# class Grok(Function):
#     def __init__(self, keyword, begin, config, end):
#         super().__init__(keyword, begin, config, end)
#         self.config = {
#             "match": None,
#             "overwrite": None,
#             "on_error": None
#         }

# class Json(Function):
#     def __init__(self, keyword, begin, config, end):
#         super().__init__(keyword, begin, config, end)
#         self.config = {
#             "source" : None,
#             "target" : None,
#             "array_function" : None,
#             "on_error" : None
#         }

# class Xml(Function):
#     def __init__(self, keyword, begin, config, end):
#         super().__init__(keyword, begin, config, end)
#         self.config = {
#             "source" : None,
#             "target" : None,
#             "xpath" : None,
#             "on_error" : None
#         }

# class Kv(Function):
#     def __init__(self, keyword, begin, config, end):
#         super().__init__(keyword, begin, config, end)
#         self.config = {
#             "source" : None,
#             "target" : None,
#             "field_split" : None,
#             "value_split" : None,
#             "whitespace" : None,
#             "trim_value" : None,
#             "on_error" : None
#         }

# class Csv(Function):
#     def __init__(self, keyword, begin, config, end):
#         super().__init__(keyword, begin, config, end)
#         self.config = {
#             "source" : None,
#             "target" : None,
#             "separator" : None,
#             "on_error" : None
#         }

# class Mutate(Function):
#     def __init__(self, keyword, begin, config, end):
#         super().__init__(keyword, begin, config, end)
#         self.config = {
#             "convert" : None,
#             "gsub" : None,
#             "lowercase" : None,
#             "merge" : None,
#             "rename" : None,
#             "replace" : None,
#             "uppercase" : None,
#             "remove_field" : None,
#             "copy" : None,
#             "split" : None,
#             "on_error" : None
#         }

# class Base64(Function):
#     def __init__(self, keyword, begin, config, end):
#         super().__init__(keyword, begin, config, end)

# class Date(Function):
#     def __init__(self, keyword, begin, config, end):
#         super().__init__(keyword, begin, config, end)

# class Drop(Function):
#     def __init__(self, keyword, begin, config, end):
#         super().__init__(keyword, begin, config, end)

# class Statedump(Function):
#     def __init__(self, keyword, begin, config, end):
#         super().__init__(keyword, begin, config, end)
        