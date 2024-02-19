# Created 2023/07/12
# Author: Caleb Bryant
# Title: Grammar.py
# Description: This file defines a Grammar class that contains the grammar definitions of a Chronicle parser config file.
# References:
    # https://pyparsing-docs.readthedocs.io/en/latest/HowToUsePyparsing.html, 
    # https://www.geeksforgeeks.org/introduction-to-grammar-in-theory-of-computation/


from AST import *
from pyparsing import (
    Word, alphanums, alphas, nums, Combine,
    Opt, QuotedString, ZeroOrMore, Group,
    OneOrMore, Keyword, Literal, Forward, SkipTo,
    LineStart, LineEnd, srange, Each, lineno, 
    col, line, StringStart, StringEnd, Suppress,
    Optional
)

class Grammar:
    def __init__(self):
        # helper function that turns parsed hash into a python dict object
        def hash_parse_action(key_values):
            to_return = {}
            for kv in key_values.as_list():
                key, value = kv
                to_return[key] = value
            return to_return

        # helper function that turns a parsed function config into a custom FunctionConfig object
        def function_config_parse_action(key_value):
            name, value = key_value
            if isinstance(value, dict):
                if name == "replace":
                    return (name, Replace(value))
                elif name == "merge":
                    return (name, Merge(value))
                elif name == "rename":
                    return (name, Rename(value))
                else:
                    return (name, Function(name, value))
            elif isinstance(value, list):
                return (name, List(name, value))
            else:
                return (name, Lit(name, value))
                
        # helper function that turns a parsed function into a custom Function object
        def function_parse_action(tokens):
            name = tokens[0]
            config_options = {}
            for option in tokens[1:]:
                key, value = option
                config_options[key] = value
            if name == "mutate":
                return Mutate(name, config_options)
            elif name == "grok":
                return Grok(name, config_options)
            elif name == "date":
                return Date(name, config_options)
            else:
                return Function(name, config_options)

        #######################################################
        # Define the grammar for CBN configuration files #
        #######################################################

        ####################
        # Token defintions #
        ####################
        # Literal value tokens
        # String token, strings can be surrounded by "" or ''
        string_token = QuotedString('"', escChar='\\', multiline=True) | QuotedString("'", escChar='\\', multiline=True)
        string_token.set_name("string")
        # Token token, Chronicle calls state value field names tokens in their docs
        token_token = Word(srange("[a-zA-Z0-9_.\-@]"))
        token_token = token_token | QuotedString('"') | QuotedString("'")
        token_token.set_name("token")
        # Boolean token
        boolean_token = Keyword("true") | Keyword("false")
        boolean_token.set_name("boolean")
        # Numerical tokens
        number_token = Combine(Optional(Optional(Word(nums)) + Literal(".")) + Word(nums))
        number_token.set_name("number")

        # Punctuation tokens
        # Arrow charater
        arrow_token = Literal('=>').suppress() | Literal('=').suppress() | Literal(':').suppress()
        arrow_token.set_name('=>')
        # Left brace character
        lbrace_token = Literal('{').suppress()
        lbrace_token.set_name('{')
        # Right brace character
        rbrace_token = Literal('}').suppress()
        rbrace_token.set_name('}')
        # Left bracket character
        lbracket_token = Literal('[').suppress()
        lbracket_token.set_name('[')
        # Right bracket character
        rbracket_token = Literal(']').suppress()
        rbracket_token.set_name(']')
        # Left parentheses
        lparen_token = Literal('(').suppress()
        lparen_token.set_name('(')
        # Right parentheses
        rparen_token = Literal(')').suppress()
        rparen_token.set_name(')')
        # Comma character
        comma_token = Literal(',').suppress()
        comma_token.set_name(',')
        comment_token = Literal('#') + ... + LineEnd()

        # Keyword tokens
        # function keyword
        function_keyword_token = Word(srange("[a-z0-9_]"))
        function_keyword_token = function_keyword_token | (Literal("\"").suppress() + function_keyword_token + Literal("\"").suppress()) | (Literal("'").suppress() + function_keyword_token + Literal("'").suppress())
        function_keyword_token.set_name("function keyword")
        
        # Function config keyword tokens
        function_config_keyword_token = Word(srange("[a-z0-9_]"))
        function_config_keyword_token.set_name("function config keyword")

        # Conditional statement tokens
        # if keyword token
        if_token = Keyword("if")
        if_token.set_name("if")
        # else if keyword token
        elseif_token = Keyword("else if")
        elseif_token.set_name("else if")
        # else keyword token
        else_token = Keyword("else")
        else_token.set_name("else")

        # Loop statement tokens
        # for keyword token
        for_token = Keyword("for")
        for_token.set_name("for")
        # in keyword token, also allowed in conditional statements
        in_token = Keyword("in").suppress()
        in_token.set_name("in")

        #######################
        # Pattern definitions #
        #######################
        # recursive pattern initialization
        if_block_pattern = Forward()
        elseif_block_pattern = Forward()
        else_block_pattern = Forward()
        conditional_pattern = Forward()
        loop_pattern = Forward()
        hash_pattern = Forward()
        # Lazy list definition, used in filter config options, commas optional and empty indices allowed
        list_pattern = lbracket_token - Group(ZeroOrMore(string_token | token_token | comma_token)) + rbracket_token
        list_pattern.set_name("list")
        list_pattern.set_parse_action(lambda tokens: tokens.as_list())
        # Key value pair pattern definition, used as values of a hash
        key_value_pattern = token_token + arrow_token - (string_token | token_token | list_pattern | hash_pattern) + Optional(comma_token)
        key_value_pattern.set_name("key value")
        key_value_pattern.set_parse_action(lambda kv: (kv[0], kv[1]))
        # Hash pattern definition, key value pairs surrounded by brackets
        hash_pattern <<= lbrace_token - OneOrMore(key_value_pattern) + rbrace_token
        hash_pattern.set_name("hash")
        hash_pattern.set_parse_action(hash_parse_action)
        # Function config pattern definition
        function_config_pattern = function_config_keyword_token + arrow_token + (string_token | token_token | boolean_token | number_token | list_pattern | hash_pattern) + Optional(comma_token)
        function_config_pattern.set_name("function config")
        function_config_pattern.set_parse_action(function_config_parse_action)
        # Function pattern definition
        function_pattern = function_keyword_token + lbrace_token - ZeroOrMore(function_config_pattern) + rbrace_token
        function_pattern.set_name("function block")
        function_pattern.set_parse_action(function_parse_action)

        # Conditional expressions are difficult to parse and are not really necessary to fully evaluate so we can just skip to the lbrace
        statement_pattern = SkipTo(lbrace_token, include=True)
        statement_pattern.set_name("statement")

        if_block_pattern <<= if_token + statement_pattern - ZeroOrMore(function_pattern|conditional_pattern|loop_pattern) + rbrace_token
        if_block_pattern.set_name("if block")
        if_block_pattern.set_parse_action(lambda tokens: Conditional(tokens))

        elseif_block_pattern <<= elseif_token + statement_pattern - ZeroOrMore(function_pattern|conditional_pattern|loop_pattern) + rbrace_token
        elseif_block_pattern.set_name("else if block")

        else_block_pattern <<= else_token + lbrace_token - ZeroOrMore(function_pattern|conditional_pattern|loop_pattern) + rbrace_token
        else_block_pattern.set_name("else block")

        conditional_pattern <<= if_block_pattern - ZeroOrMore(elseif_block_pattern) + Optional(else_block_pattern)
        conditional_pattern.set_name("conditional block")

        loop_pattern <<= for_token + statement_pattern - ZeroOrMore(function_pattern|conditional_pattern|loop_pattern) + rbrace_token
        loop_pattern.set_name("loop block")

        filter_block = Keyword("filter").suppress() + lbrace_token - OneOrMore(function_pattern|conditional_pattern|loop_pattern) + rbrace_token
        filter_block.set_name("filter block")

        comment = Literal('#') + ... + LineEnd()
        self.grammars = StringStart() + filter_block + StringEnd()
        # Ignore commented statements
        self.grammars.ignore(comment_token) # may not want to ignore comments if we want to be able to re-write the parser after taking it in

    def parse_file(self, file_name):
        return self.grammars.parse_file(file_name).as_list()

    def parse_string(self, string):
        return self.grammars.parse_string(string).as_list()
        