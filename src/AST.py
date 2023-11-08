# Created 2023/07/17
# Author: Caleb Bryant
# Title: AST.py
# Description: This file defines a class to represent a Chronicle parser as an abstract syntax tree. This allows us to check for semantic errors easier. 
# References: https://en.wikipedia.org/wiki/Abstract_syntax_tree

from Tokens import *
from State import State
import re


class AST:
    def __init__(self, filter_object):
        self.filter = filter_object

    def get_state(self):
        state = State()
        self.filter.process_state(state)
        return state

class Block:
    def __init__(self, config):
        if type(config[1]) == LBraceToken:
            self.keyword = config[0]
            self.statement = None
            self.begin = config[1]
            self.body = config[2:-1]
            self.end = config[-1]
        else:
            self.keyword = config[0]
            self.statement = config[1]
            self.begin = config[2]
            self.body = config[3:-1]
            self.end = config[-1]

    def process_state(self, state):
        for child in self.body:
           child.process_state(state)

    def build_state(self, state):
        for value in self.body:
            value.build_state(state)
        if self.statement:
            for token in self.statement:
                if token == ConditionalToken:
                    state.add_value(token)

class Filter(Block):
    def __init__(self, config):
        super().__init__(config)

class If(Block):
    def __init__(self, config):
        super().__init__(config)

    def process_state(self, state):
        if self.statement != None:
            # Need to check if statements have
            self.statement.check_if_values_exist_in_state(state)
        else:
            print(f"!! ERROR '{self.keyword.value}' block does not have a statement?!?!  this is divide by zero level shit")

        super().process_state(state)

class ConditionalToken:
    def __init__(self,tokens):
        self.tokens = tokens
        self.value = self.get_name()
        
    def get_name(self):
        name = []
        for token in self.tokens:
            if type(token) == TokenToken:
                name.append(token.value)
        return '.'.join(name)

class ConditionalStatement:
    def __init__(self,tokens):
        self.tokens = tokens

    def check_if_values_exist_in_state(self, state):
        for token in self.tokens:
            if isinstance(token, ConditionalToken) and not state.does_variable_exist(token.get_name()):
                state.add_error(f"line {token.tokens[0].row}, undeclared variable used in if statement")


    def to_string():
        s = self.tokens[0].value
        for token in self.tokens[1:]:
            s += " " + token.value
        return s

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
        self.tokens = tokens
    # TODO: add functions to pull out token values to check against value table

class Function:
    def __init__(self, config):
        self.keyword = config[0]
        self.begin = config[1]
        #self.config = {}
        self.config = config[2:-1]
        self.end = config[-1]

    # TODO: check config["config"] for valid keywords and values depending on the function type
    # Ex. Make sure a grok only has one of each of match, overwrite, and on_error

    def get_config(self):
        return self.config

    def have_all_children_process_state(self, state):
        for child in self.config:
            #print(f"         Function Child: {type(child)} and value: {child}")
            if not isinstance(child, str):
                child.process_state(state)
        
    def process_state(self, state):
        # My children are FunctionConfig objects
        pass

    def process_on_error(self, state):
        on_error = self.check_config("on_error")
        if not on_error:
            state.add_error(f"line {self.keyword.row}, {str(self.keyword)} function missing on_error statement")
        else:
            state.add_variable(str(on_error.value))
        
    def set_config(self, config):
        # Loop through the list of function configs
        for value in config[2:-1]:
            keyword = value.keyword.value # get the function config keyword
            try:
                exists = True
                self.config[keyword] = value
            except KeyError:
                exists = None
            # If the keyword exists in the acceptable config for the function, add the value to the config
            if exists:
                self.config[keyword] = value

    # return the keyword of the function
    def get_name(self):
        return self.keyword.value

    # return the value in the function's config if it is set, return None if not set
    def check_config(self, keyword):
        return self.config[keyword] if keyword in self.config else None

    def __str__(self):
        config = ''
        for line in self.config:
            config += str(line) + '\n' if line != self.config[-1] else str(line)
        return str(self.keyword) + str(self.begin)

class Grok(Function):
    def __init__(self, config):
        super().__init__(config)
        self.config = {
            "match": None,
            "overwrite": None,
            "on_error": None
        }
        self.set_config(config)
    
    def process_state(self, state):
        # Need to parse each grok pattern to check for values used, each value needs to be in the overwrite statement
        match = self.config["match"]
        variables_used_in_patterns = []
        if match:
            for pair in match.value.pairs: # match.value is always a hash
                source_field = str(pair.left_value)
                state.does_variable_exist(source_field)
                patterns = pair.right_value # patterns can be either a StringToken or it can be a List
                if isinstance(patterns, List):
                    values = set()
                    for value in patterns.values:
                        values = values.union(set(self.parse_grok_pattern(value.value)))
                        for name in values:
                            variables_used_in_patterns.append(name) if name not in variables_used_in_patterns else None
        else:
            state.add_error(f"line {grok.keyword.row}, grok missing match configuration")

        # Handle the overwrite value
        overwrite = self.config["overwrite"]
        if overwrite:
            overwrite_list = overwrite.value
            # overwrite list can also be just a string token
            if isinstance(overwrite_list, List):
                overwrite_list = overwrite_list.as_strings()
            else:
                overwrite_list = [overwrite_list.value]
            missing_values = []
            for value in variables_used_in_patterns:
                missing_values.append(value) if value not in overwrite_list else None
            if missing_values != []:
                formatted_values = ', '.join([f'"{value}"' for value in missing_values])
                state.add_error(f"line {self.keyword.row}, grok function missing overwrite values: {formatted_values}")
        else:
            state.add_error(f"line {self.keyword.row}, grok function missing overwrite config")

        self.process_on_error(state)
    
    def parse_grok_pattern(self, pattern):
        matches = re.findall("%\{[^}]+?:([^}]+?)\}", pattern) # matches '%{IP:value}' values in grok patterns
        matches += re.findall("\?P<([^>]+)>", pattern) # matches '(?P<value>whatever is here)' values in grok patterns
        return matches


class Json(Function):
    def __init__(self, config):
        super().__init__(config)
        self.config = {
            "source" : None,
            "target" : None,
            "array_function" : None,
            "on_error" : None
        }
        self.set_config(config)

    def process_state(self, state):
        self.process_on_error(state)

class Xml(Function):
    def __init__(self, config):
        super().__init__(config)
        self.config = {
            "source" : None,
            "target" : None,
            "xpath" : None,
            "on_error" : None
        }
        self.set_config(config)
    
    def process_state(self, state):
        self.process_on_error(state)

class Kv(Function):
    def __init__(self, config):
        super().__init__(config)
        self.config = {
            "source" : None,
            "target" : None,
            "field_split" : None,
            "unescape_field_split" : None,
            "value_split" : None,
            "unescape_value_split" : None,
            "whitespace" : None,
            "trim_value" : None,
            "on_error" : None
        }
        self.set_config(config)

    def process_state(self, state):
        self.process_on_error(state)

class Csv(Function):
    def __init__(self, config):
        super().__init__(config)
        self.config = {
            "source" : None,
            "target" : None,
            "separator" : None,
            "unescape_separator" : None,
            "on_error" : None
        }
        self.set_config(config)

    def process_state(self, state):
        self.process_on_error(state)

class Mutate(Function):
    def __init__(self, config):
        super().__init__(config)
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
        self.set_config(config)
        
    def process_state(self, state):
        self.process_on_error(state)
        # replace is the only function that has the option to not generate an error so only that one needs to be defined
        if self.config['replace'] != None:
            pairs = self.config["replace"].value.pairs
            for pair in pairs:
                if not pair.do_bracketed_values_exist():
                    state.add_variable(str(pair.left_value))
    

class Base64(Function):
    def __init__(self, config):
        super().__init__(config)
        self.config = {
            "source" : None,
            "target" : None,
            "encoding" : None,
            "on_error" : None
        }
        self.set_config(config)

class Date(Function):
    def __init__(self, config):
        super().__init__(config)
        self.config = {
            "match" : None,
            "source" : None,
            "target" : None,
            "timezone" : None,
            "rebase" : None,
            "on_error" : None
        }
        self.set_config(config)
    
    def process_state(self, state):
        self.process_on_error(state)

class Drop(Function):
    def __init__(self, config):
        super().__init__(config)
        self.config = {
            "tag" : None
        }
        self.set_config(config)

class Statedump(Function):
    def __init__(self, config):
        super().__init__(config)
        self.config = {
            "label" : None
        }
        self.set_config(config)

class FunctionConfig:
    def __init__(self, config):
        self.keyword = config[0]
        self.assign = config[1]
        self.value = config[2]
        self.comma = config[-1] if type(config[-1]) == CommaToken else None

    def build_state(self, state, function):
        if self.keyword.value == 'replace':
            self.value.build_state('replace')
        if self.keyword.value == 'on_error':
            state.add_variable(self.value)
        if self.keywword.value == 'target':
            state.add_variable(self.value)

    def __str__(self):
        return str(self.keyword) + str(self.assign) + str(self.value)

class Hash:
    def __init__(self, config):
        self.begin = config[0]
        self.pairs = config[1:-1]
        self.end = config[-1]

    def get_left_values(self):
        return_list = []
        for pair in self.pairs:
            #print(f"                pair left: {pair.left_value.value}")
            return_list.append(pair.left_value.value)
            
        return return_list

    def get_right_values(self):
        return_list = []
        for pair in self.pairs:
            #print(f"                pair right: {pair.right_value.value}")
            return_list.append(pair.right_value.value)
            
        return return_list
    
    def __str__(self):
        pairs = ''
        for pair in self.pairs:
            pairs += str(pair.left_value) + str(self.assign) + str(self.right_value) + '\n' if pair != self.pairs[-1] else str(pair.left_value) + str(self.assign) + str(self.right_value)
        return str(self.begin) + pairs + str(self.end)

class List:
    def __init__(self, config):
        self.begin = config[0]
        self.values = config[1:-1]
        self.end = config[-1]
    
    # Returns the Logstash list object as a python list of string values
    def as_strings(self):
        strings = []
        for value in self.values:
            strings.append(value.value)
        return strings

    def __str__(self):
        values = ''
        for value in self.values:
            values += str(value) + '\n' if value != self.values[-1] else str(value)
        return str(self.begin) + values + str(self.end)

class KeyValue:
    def __init__(self, config):
        self.left_value = config[0]
        self.assign = config[1]
        self.right_value = config[2]
        self.comma = config[-1] if type(config[-1]) == CommaToken else None

    def do_bracketed_values_exist(self):
        # check if a replace string contains any variables
        right_value = str(self.right_value)
        match = re.match("%\{[^}]*}", right_value)
        return True if match else False

    def __str__(self):
        return str(self.left_value) + str(self.assign) + str(self.right_value)
