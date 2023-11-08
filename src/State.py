from AST import *
import re

class State:
    def __init__(self, ast):
        self.ast = ast
        self.explicit_values = {} # values that we know for sure will exist in state data
        self.implicit_values = {} # values that might exist in state data depending on an error
        self.errors = []
        self.scan_tree(self.ast.filter)

    def __init__(self):
        self.values_used = [ "@collectionTimestamp", "@collectionTimestamp.nanos", "@collectionTimestamp.seconds", "@createTimestamp", "@createTimestamp.nanos", "@createTimestamp.seconds", "@enableCbnForLoop", "@onErrorCount", "@output", "@timezone", "message" ]
        self.value_occurrances = {}
        self.errors = []

    def add_variable(self, variable_name):
        assert isinstance(variable_name, str)
        current_var = ''
        index = 0
        for sub_variable in variable_name.split('.'):
            current_var += f".{sub_variable}"
            if index == 0:
                current_var = current_var[1:]
            index += 1
            self.values_used.append(current_var) if current_var not in self.values_used else None
            try:
                self.value_occurrances[current_var] += 1
            except KeyError as e:
                self.value_occurrances[current_var] = 1

    def does_variable_exist(self, variable):
        if not isinstance(variable, str):
            return False
        try:
            self.value_occurrances[variable]
            return True
        except KeyError:
            return False

    def add_value(self, value):
        self.add_variable(value)

    def remove_value(self, token):
        self.values.remove(token.value)

    def check_value(self, value_name):
        return value_name in self.values_used

    def add_error(self, error_string):
        self.errors.append(error_string)

    def __str__(self):
        s = ""
        for val in sorted(self.values_used):
            s += val + '\n'
        return s
