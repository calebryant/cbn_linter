# Created 2023/07/17
# Author: Caleb Bryant
# Title: AST.py
# Description: This file defines a class to represent a Chronicle parser as an abstract syntax tree. This allows us to check for semantic errors easier. 
# References: https://en.wikipedia.org/wiki/Abstract_syntax_tree

from Tokens import *
from State import State

class AST:
    def __init__(self, filter_object):
        self.filter = filter_object
        self.value_table = State()
        # self.scan_tree()

    def scan_tree(self):
        self.filter.scan_tree(self.value_table)

    def get_state(self):
        state = State()
        state.add_variable("message")
        self.filter.process_state(state)
        #print(f"I am an AST with filter type: {type(self.filter)}")
        return state


    def to_json(self):
        json_object = {
            "filter": {}
        }
        for value in self.filter.body:
            json_object[value.keyword.value] = value.to_json()
        return json_object

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
        #print( f"   A state here: my keyword is: {self.keyword.value} and my body is: {type(self.body)}" )
        for child in self.body:
           #print( f"     A child of state: {type(child)}" )
           child.process_state(state)


    def build_state(self, state):
        for value in self.body:
            value.build_state(state)
        if self.statement:
            for token in self.statement:
                if token == ConditionalToken:
                    state.add_value(token)

    def to_json(self):
        json_object = {}
        for value in self.body:
            json_object[value.keyword.value] = value.to_json()
        if self.statement:
            return [self.statement.to_string(), json_object]
        

class Filter(Block):
    def __init__(self, config):
        super().__init__(config)


class If(Block):
    def __init__(self, config):
        super().__init__(config)

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

    # TODO: add logic that will add tokens in state data to a value table

    def process_state(self, state):
        #print(f"       I am a Function: config is: {type(self.config)}")
        for child in self.config:
            #print(f"         Function Child: {type(child)}")
            child.process_state(state)

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

    # TODO add values to the state, may need to be defined in each child class instead
    def build_state(self, state):
        for line in self.config:
            line.build_state(state, self.keyword.value)

    def to_json(self):
        json_object = {}
        for key in self.config:
            json_object[key] = self.config[key].to_json()
        return json_object

class Grok(Function):
    def __init__(self, config):
        super().__init__(config)
        self.config = {
            "match": None,
            "overwrite": None,
            "on_error": None
        }
        self.set_config(config)

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

class Mutate(Function):
    def __init__(self, config):
        super().__init__(config)
        #self.config = {
        #    "convert" : None,
        #    "gsub" : None,
        #    "lowercase" : None,
        #    "merge" : None,
        #    "rename" : None,
        #    "replace" : None,
        #    "uppercase" : None,
        #    "remove_field" : None,
        #    "copy" : None,
        #    "split" : None,
        #    "on_error" : None
        #}
        #self.set_config(config)
    

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
            
        # TODO: Check keywords contain the correct data type. Ex. make sure overwrite contains a list, etc...

    def process_state(self, state):
        #print(f"           I am a FuncConf, keyword: {self.keyword.value} and value: {type(self.value)}")

        # make sure all right side %{} vars exist
        if self.keyword.value in [ "replace" ]:
            #print('= testing for %{} in replace')
            for value in self.value.get_right_values():
                if value[0:2] == '%{' and value[-1] == '}':
                    the_real_value = value[2:-1]
                    try:
                        print(f"= checking if {value} is in the state")
                        state.value_occurrances[the_real_value]
                    except KeyError:
                        print(f"!! RIGHT SIDE DOES NOT EXIST IN REPLACE '{the_real_value}' is not in the state")

        # make sure all right side vars exist as is
        if self.keyword.value in [ "merge" ]:
            #print('= testing right values as-is in state')
            for value in self.value.get_right_values():
               if not value[0:2] == '%{':
                   try: 
                       print(f"= testing '{value}' in state")
                       state.value_occurrances[value]
                   except KeyError:
                       print(f"!! LEFT SIDE DOES NOT EXIST IN MERGE '{value}' is not in the state")
                       
        # insert all left vars into state
        if self.keyword.value in [ "replace" , "merge" ]:
            for value in self.value.get_left_values():
                state.add_variable(value)


    def build_state(self, state, function):
        if self.keyword.value == 'replace':
            self.value.build_state('replace')
        if self.keyword.value == 'on_error':
            state.add_variable(self.value)
        if self.keywword.value == 'target':
            state.add_variable(self.value)

    def to_json(self):
        if type(self.value) == Hash:
            json_object = {}
            for key in self.value.pairs:
                lval = key.left_value
                json_object[lval] = key.r_val.value
        elif type(self.value) == List:
            json_object = []
            for key in self.value.values:
                json_object.append(key.value)
        # else:
            
            

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

class List:
    def __init__(self, config):
        self.begin = config[0]
        self.values = config[1:-1]
        self.end = config[-1]

class KeyValue:
    def __init__(self, config):
        self.left_value = config[0]
        self.assign = config[1]
        self.right_value = config[2]
        self.comma = config[-1] if type(config[-1]) == CommaToken else None
