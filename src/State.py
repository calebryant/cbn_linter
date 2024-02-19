# Created 2024/02/19
# Author: Caleb Bryant
# Title: State.py
# Description: Keeps track of the state of variables used in a parser

from AST import *
import re

# class State:
#     def __init__(self):
        

class StateValue:
    def __init__(self, name, is_in_scope):
        self.name = name
        self.literal_values = [] # Literal string value set if a replace function is used to set the field
        self.other_fields = []
        self.in_scope = is_in_scope

    def __add__(self, other):
        try:
            assert isinstance(other, StateValue)
        except AssertionError:
            raise TypeError(f"unsupported operand type(s) for +: <class 'StateValue'> and '{type(other)}'")
        self.literal_values = list(set(self.literal_values + other.literal_values))
        self.other_fields = list(set(self.other_fields + other.other_fields))