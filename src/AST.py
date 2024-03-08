# Created 2023/07/17
# Author: Caleb Bryant
# Title: AST.py
# Description: This file defines a class to represent a Chronicle parser as an abstract syntax tree. This allows us to check for semantic errors easier. 
# References: https://en.wikipedia.org/wiki/Abstract_syntax_tree

import re
import Plugins

# class to represent the AST for the parser
class AST:
    def __init__(self) -> None:
        self.values = [] # basic list of all the parsed data from a parser as objects
        self.state = State() # state object that keeps track of the parser's state values

    # This function builds a new .conf file in a string using every mutate filter, that file can then be used with the parser API to obtain which UDM fields are used
    def __str__(self) -> str:
        string_to_return = ""
        for mutate_function in self.mutates:
            string_to_return += f"{str(mutate_function)} "
        return string_to_return

    def add_function(self, func: Plugins.Filter) -> None:
        self.values.append(func)

    def add_mutate(self, func: Plugins.Mutate) -> None:
        self.values.append(func)
        if isinstance(func, Plugins.Replace):
            self.state.add_replace(func)
        elif isinstance(func, Plugins.Merge):
            self.state.add_merge(func)
        elif isinstance(func, Plugins.Copy):
            self.state.add_copy(func)
        elif isinstance(func, Plugins.Rename):
            self.state.add_rename(func)

    def add_grok(self, func: Plugins.Grok) -> None:
        self.values.append(func)

    def add_date(self, func: Plugins.Date) -> None:
        self.values.append(func)

    def add_conditional(self, func: Plugins.Conditional) -> None:
        self.values.append(func)

    def add_loop(self, func: Plugins.Loop) -> None:
        self.values.append(func)

    # build a replace function that initializes all source varibles used as an empty string
    def build_replace_initialize(self):
        key_values = [ f"\"{variable}\" => \"\" " for variable in self.mutate_source_variables]
        return "mutate {{ replace => {{ {}}} }} ".format("".join(key_values))
    
class State:
    def __init__(self):
        self.value_table = {} # flat dictionary of all state values in the parser, with the key being the name of the value and value is a list of possible values
        self.scope = [] # list of all scopes in the parser
        self.mutates = [] # list of all mutate functions used
        self.mutate_source_variables = []

    def add_replace(self, mutate: Plugins.Replace) -> None:
        for key, value in mutate.config_options:
            self.add_to_value_table(key, value)

    def add_merge(self, mutate: Plugins.Merge) -> None:
        mutate.config_options

    def add_copy(self, mutate: Plugins.Copy) -> None:
        mutate.config_options

    def add_rename(self, mutate: Plugins.Rename) -> None:
        mutate.config_options

    def add_to_value_table(self, name: str, value) -> None:
        try:
            self.value_table[name].append(value)
        except KeyError:
            self.value_table[name] = [value]

class StateValue:
    def __init__(self, name, value=None, is_in_scope=False):
        self.name = name
        self.literal_values = [value] # Literal string value set if a replace function is used to set the field
        self.sub_fields = [] # sub fields that may belong to the value (from a rename, merge, or copy)
        self.in_scope = is_in_scope # boolean value that denotes whether or not the value exists in the current scope of the parser

    def __add__(self, other):
        try:
            assert isinstance(other, StateValue)
        except AssertionError:
            raise TypeError(f"unsupported operand type(s) for +: <class 'StateValue'> and '{type(other)}'")
        self.literal_values = list(set(self.literal_values + other.literal_values))
        self.other_fields = list(set(self.other_fields + other.other_fields))
        return self
    
    def __getitem__(self, item):
        return self.sub_fields[item]