# Created 2024/02/19
# Author: Caleb Bryant
# Title: State.py
# Description: Keeps track of the state of variables used in a parser

from AST import *
import re

class State:
    def __init__(self):
        self.value_table = {}
        self.scope = {}

    def add_replace(self, mutate):
        for key, value in mutate.config_options:
            self.add_to_value_table(key, value)

    def add_merge(self, mutate):
        mutate.config_options

    def add_copy(self, mutate):
        mutate.config_options

    def add_rename(self, mutate):
        mutate.config_options

    def add_to_value_table(self, name, value):
        split_name = name.split('.')
        placeholder = self.value_table[split_name[0]]
        for sub_name in split_name:
            try:
                placeholder = placeholder[sub_name] # probably need a try catch block here
            except KeyError:
                placeholder[sub_name] = StateValue(sub_name)
        placeholder = StateValue(name, value)
        return placeholder

class StateValue:
    def __init__(self, name, is_in_scope=False):
        self.name = name
        self.literal_values = [] # Literal string value set if a replace function is used to set the field
        self.other_fields = [] # sub fields that may belong to the value (from a rename or merge)
        self.sub_fields = {} # sub fields that may belong to the value (from a replace)
        self.in_scope = is_in_scope # boolean value that denotes whether or not the value exists in the current scope of the parser

    def __init__(self, name, value, is_in_scope=False):
        self.name = name
        self.literal_values = [value] # Literal string value set if a replace function is used to set the field
        self.other_fields = [] # sub fields that may belong to the value (from a rename or merge)
        self.sub_fields = {} # sub fields that may belong to the value (from a replace)
        self.in_scope = is_in_scope # boolean value that denotes whether or not the value exists in the current scope of the parser

    def __add__(self, other):
        try:
            assert isinstance(other, StateValue)
        except AssertionError:
            raise TypeError(f"unsupported operand type(s) for +: <class 'StateValue'> and '{type(other)}'")
        self.literal_values = list(set(self.literal_values + other.literal_values))
        self.other_fields = list(set(self.other_fields + other.other_fields))
        self.sub_fields.update(other.sub_fields)
        return self
    
    def __getitem__(self, item):
         return self.sub_fields[item]