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
            state.errors.append(f"'{self.keyword.value}' block does not have a statement?!?!  this is divide by zero level shit")

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
        #print(f"  TT I am a conditional statement trying to test if my variables exist")
        for token in self.tokens:
            #print(f"     TTT token: {token} of type: {type(token)}")
            if isinstance(token, ConditionalToken):
                #print(f"    TTTT name: {token.get_name()}")
                state.does_variable_exist(token.get_name())

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
        # Need to check that there is a source and an on_error
        if self.config['source'] == None:
            state.errors.append(f"no 'source' for '{self.keyword.value}' command on line: {(self.keyword.coordinates()[0])}")
        else:
            # a source is provided, but is it in the state?
            the_source_variable = self.config['source'].value.value
            #print(f"what is type {type(self.config['source'].value)} and value: {self.config['source'].value.value}")
            if not state.does_variable_exist(the_source_variable):
                state.errors.append(f"source '{the_source_variable}' for CSV command is not in state.  Line: {(self.keyword.coordinates()[0])}")

        if self.config['on_error'] == None:
            state.errors.append(f"no 'on_error' for command '{self.keyword.value}' on line: {(self.keyword.coordinates()[0])}")
        else:
            the_error_variable = self.config['on_error'].value.value
            #print(f"what is type {type(self.config['on_error'].value)} and value: {self.config['on_error'].value.value}")
            state.add_variable(the_error_variable)

        # Now insert the column values
        if self.config['target'] != None:
            # Need to add a state method that will add the columnXX to target.columnXX
            for n in range(100):
                state.add_variable( f"column{n}" )
        else:
            for n in range(100):
                state.add_variable( f"column{n}" )


        super().process_state(state)

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
            self.config['replace'].check_right_vars_in_braces_exist(state)
            self.config['replace'].insert_left_vars(state)

        if self.config['merge'] != None:
            self.config['merge'].check_right_vars_exist(state)
            self.config['merge'].insert_left_vars(state)

        if self.config['rename'] != None:
            self.config['rename'].check_left_vars_exist(state)
            self.config['rename'].insert_right_vars(state)
            self.config['rename'].remove_left_vars(state)

        if self.config['gsub'] != None:
            the_variable = self.config['gsub'].get_first_value()
            if not state.does_variable_exist(the_variable):
                state.error_list.append(f"variable '{the_variable}' not in state.  gsub on line: {self.keyword.coordinates()[0]}")
                
        if self.config["convert"] != None:
            self.config['convert'].check_left_vars_exist(state)

        if self.config["lowercase"] != None:
            for variable in self.config['lowercase'].get_variable_list():
                if not state.does_variable_exist(variable):
                    state.errors.append(f"variable '{variable}' in lowercase command is not in state.  Line: {self.keyword.coordinates()[0]}")

        if self.config["uppercase"] != None:
            for variable in self.config['uppercase'].get_variable_list():
                if not state.does_variable_exist(variable):
                    state.errors.append(f"variable '{variable}' in uppercase command is not in state.  Line: {self.keyword.coordinates()[0]}")

        if self.config["remove_field"] != None:
            for value in self.config['remove_field'].get_variable_list():
                try:
                    state.remove_variable(value)
                except KeyError:
                    # it is fine if the item does not exist?
                    pass

        if self.config["copy"] != None:
            print(f"   copy in a mutate, type is: {type(self.config['copy'])}")
            state.deep_variable_copy(self.config['copy'].l_val, self.config['copy'].l_val)

        if self.config["split"] != None:
            print(f"   split in a mutate, type is: {type(self.config['split'])}")

        if self.config["on_error"] != None:
            print(f"   on_error in a mutate, type is: {type(self.config['on_error'])}")
    

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
            
        # TODO: Check keywords contain the correct data type. Ex. make sure overwrite contains a list, etc...

    # returns the values in the List of the parser.  So the array of a GSUB or LowerCase
    def get_variable_list(self):
        if not isinstance(self.value, List):
            return []
        else:
            return self.value.get_values_of_list()

    def check_right_vars_in_braces_exist(self, state):
        #print('= NEW testing for %{} in replace')
        for value in self.value.get_right_values():
            if value[0:2] == '%{' and value[-1] == '}':
                the_real_value = value[2:-1]
                if not state.does_variable_exist(the_real_value):
                    print(f"!! RIGHT SIDE DOES NOT EXIST IN REPLACE '{the_real_value}' is not in the state")

    def check_right_vars_exist(self, state):
        #print('= NEW testing right values as-is in state')
        for value in self.value.get_right_values():
           if not value[0:2] == '%{':
               if not state.does_variable_exist(value):
                   state.errors.append(f"'{value}' not in state - '{self.keyword.value}' function on line: {self.keyword.coordinates()[0]}")
                       
    def remove_left_vars(self, state):
        for value in self.value.get_left_values():
            if state.does_variable_exist(value):
                del state.value_occurrances[value]


    def insert_right_vars(self, state):
        for value in self.value.get_right_values():
            state.add_variable(value)

    def insert_left_vars(self, state):
        for value in self.value.get_left_values():
            state.add_variable(value)

    def check_left_vars_exist(self, state):
        for value in self.value.get_left_values():
            if not state.does_variable_exist(value):
                state.errors.append(f"'{value}' not in state - '{self.keyword.value}' function on line: {self.keyword.coordinates()[0]}")

    def get_first_value(self):
        if self.keyword.value != 'gsub':
            #print("!!!! Divide by zero")
            return None
        else:
            return self.value.get_first_item()


    def process_state(self, state):
        print(f"           I am a FuncConf, running process_state()")


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
    
    def get_first_item(self):
        return self.values[0].value

    # returns JUST the values of the list, not the commas
    def get_values_of_list(self):
        strings = []
        for value in self.values:
            if not isinstance(value, CommaToken):
               strings.append(value.value)
        return strings


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
