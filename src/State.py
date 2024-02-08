# Created 2023/11/06
# Author: Caleb Bryant
# Title: State.py
# Description: Keeps track of the state of variables used in a parser

from AST import *
from Tokens import *
import re

class State:
    def __init__(self):
        # List of everything that exists in the current state
        self.explicit_state = [ "@collectionTimestamp", "@collectionTimestamp.nanos", "@collectionTimestamp.seconds", "@createTimestamp", "@createTimestamp.nanos", "@createTimestamp.seconds", "@enableCbnForLoop", "@onErrorCount", "@output", "@timezone", "message" ]
        self.implicit_state = []

        # Dictionary that stores the name of all values set using a mutate function and a list of StateValue objects for each use of that value
        self.value_table = {}
        self.scope = []
        # Issues that are absolutely not allowed
        self.errors = []
        # Issues that may not be fatal but should notify the user
        self.warnings = []

    def found_in_explicit_state(self, variable):
        return True if variable in self.explicit_state else False

    def found_in_implicit_state(self, variable):
        return True if variable in self.implicit_state else False

    def add_explicit_value(self, value_string):
        current_var = ''
        val_as_list = value_string.split('.')
        for index, sub_variable in enumerate(val_as_list):
            if index == 0:
                current_var = sub_variable
            else:
                current_var += f".{sub_variable}"
            self.explicit_state.append(current_var) if current_var not in self.explicit_state else None
    
    def remove_explicit_value(self, value_string):
        for name in self.explicit_state:
            pattern = f"^{value_string}[.].+"
            if re.match(pattern, name):
                self.explicit_state.remove(name)
    
    def rename_explicit_value(self, value_string):
        for name in self.explicit_state:
            pattern = f"^{value_string}"
            new_name = re.sub(pattern, value_string, name)
            self.explicit_state[self.explicit_state.index(name)] = new_name if new_name else None

    def add_implicit_value(self, value_string):
        current_var = ''
        val_as_list = value_string.split('.')
        for index, sub_variable in enumerate(val_as_list):
            if index == 0:
                current_var = sub_variable
            else:
                current_var += f".{sub_variable}"
            self.implicit_state.append(current_var) if current_var not in self.implicit_state else None
    
    def remove_implicit_value(self, value_string):
        for name in self.implicit_state:
            pattern = f"^{value_string}[.].+"
            if re.match(pattern, name):
                self.implicit_state.remove(name)

    def rename_implicit_value(self, value_string):
        for name in self.implicit_state:
            pattern = f"^{value_string}"
            new_name = re.sub(pattern, value_string, name)
            self.implicit_state[self.implicit_state.index(name)] = new_name if new_name else None
    
    # def add_to_value_table(self, name, contents):
    #     if isinstance(name, CommaToken): return
    #     assert isinstance(name, TokenToken) or isinstance(name, StringToken)
    #     assert isinstance(contents, TokenToken) or isinstance(contents, StringToken) or isinstance(contents, list) or contents == None
    #     if str(name) not in self.value_table:
    #         if not isinstance(contents, list):
    #             self.value_table[str(name)] = [StateValue(name, contents)]
    #         else: 
    #             self.value_table[str(name)] = contents
    #     else:
    #         if not isinstance(contents, list):
    #             self.value_table[str(name)].append(StateValue(name, contents))
    #         else:
    #             self.value_table[str(name)] += contents
    
    def add_to_value_table(self, name, contents):
        if isinstance(name, CommaToken): return
        split_name = str(name).split('.')
        # if the value exists in the table
        if location_in_table := self.get_value(split_name, self.value_table):
            if isinstance(contents, list) and isinstance(location_in_table, list):
                location_in_table += contents
            elif isinstance(location_in_table, list):
                location_in_table += [contents]
        else:
            placeholder = self.traverse_value_table(split_name[:-1], self.value_table)
            if isinstance(contents, list) or isinstance(contents, dict):
                placeholder[split_name[-1]] = contents
            else:
                placeholder[split_name[-1]] = [contents]

    # traverses to a spot in the table, creates entries if it doesnt exist, returns the final value
    def traverse_value_table(self, split_name, placeholder):
        if split_name == []:
            return placeholder
        try:
            if isinstance(placeholder[split_name[0]], list):
                placeholder[split_name[0]] = dict()
            placeholder = placeholder[split_name[0]]
        except KeyError:
            placeholder[split_name[0]] = dict()
            placeholder = placeholder[split_name[0]]
        return self.traverse_value_table(split_name[1:], placeholder)

    # returns true if value exists in the table, false if not
    def is_in_value_table(self, split_name, placeholder):
        if split_name == []:
            return True 
        try:
            placeholder = placeholder[split_name[0]]
            return self.is_in_value_table(split_name[1:], placeholder)
        except KeyError:
            return False

    # returns a value from the value table, None if it doesn't exist
    def get_value(self, split_name, placeholder):
        if split_name == []:
            return placeholder 
        try:
            placeholder = self.get_value(split_name[1:], placeholder[split_name[0]])
            return placeholder
        except TypeError:
            placeholder = {}
            return placeholder
        except KeyError:
            return None

    def check_value(self, value_name):
        return value_name in self.explicit_state

    def add_error(self, error_string):
        self.errors.append(error_string)
    
    def add_warning(self, warning_string):
        self.warnings.append(warning_string)

    def __str__(self):
        s = ""
        for val in sorted(self.values):
            s += val + '\n'
        return s

    def push_scope(self):
        state_copy = self.explicit_state.copy()
        self.scope.append(state_copy)

    def pop_scope(self):
        current_scope = self.explicit_state
        old_scope = self.scope.pop()
        for value in current_scope:
            if value not in old_scope:
                self.implicit_state.append(value)
        self.explicit_state = old_scope

class StateValue:
    def __init__(self, name, contents, explicit=False):
        # token of the entry in the state
        self.name = name
        # token of the value used to set the name
        self.contents = contents
        # line where name is set to contents
        self.lineno = self.get_line()
        # boolean indicating if the variable is guaranteed to exist in state data or not
        self.explicit = explicit

    def get_line(self):
        return int(self.name)

    def __str__(self):
        return str(self.name)
        # return f"{str(self.name)}: {str(self.contents)} at line {self.lineno}"

    def __int__(self):
        return self.lineno