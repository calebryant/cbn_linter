# Created 2023/07/17
# Author: Caleb Bryant
# Title: AST.py
# Description: This file defines a class to represent a Chronicle parser as an abstract syntax tree. This allows us to check for semantic errors easier. 
# References: https://en.wikipedia.org/wiki/Abstract_syntax_tree
# References: https://www.elastic.co/guide/en/logstash/current/filter-plugins.html

from State import *
import re

# class to represent the AST for the parser
class AST:
    def __init__(self):
        self.values = [] # basic list of all the parsed data from a parser as objects
        self.state = State()
        self.mutates = [] # list of all mutate functions used
        self.mutate_source_variables = []

    # This function builds a new .conf file in a string using every mutate filter, that file can then be used with the parser API to obtain which UDM fields are used
    def __str__(self):
        string_to_return = ""
        for mutate_function in self.mutates:
            string_to_return += f"{str(mutate_function)} "
        return string_to_return

    def add_function(self, func):
        self.values.append(func)

    def add_mutate(self, func):
        self.values.append(func)
        if any(x in ["replace", "merge", "copy", "rename"] for x in func.config_options.keys()):
            self.mutates.append(func)
            self.mutate_source_variables = list(set(self.mutate_source_variables + func.get_all_source_variables()))

    def add_grok(self, func):
        self.values.append(func)

    def add_date(self, func):
        self.values.append(func)

    def add_conditional(self, func):
        self.values.append(func)

    def add_loop(self, func):
        self.values.append(func)

    # build a replace function that initializes all source varibles used as an empty string
    def build_replace_initialize(self):
        key_values = [ f"\"{variable}\" => \"\" " for variable in self.mutate_source_variables]
        return "mutate {{ replace => {{ {}}} }} ".format("".join(key_values))

# Function classes and sub-classes
class Function:
    def __init__(self, name, config_options):
        self.name = name
        self.config_options = config_options
        self.missing_on_error = not self.has_on_error() # boolean value denoting if this function needs an on_error statement

    # returns true if the function has an on_error statement, false if not
    def has_on_error(self):
        return True if "on_error" in self.config_options else False
    
    def get_all_source_variables(self):
        source_variables = []
        for config_op in self.config_options.values():
            if config_op.name in ["replace", "merge", "copy", "rename"]:
                source_variables += config_op.source_variables
        return source_variables

class Mutate(Function):
    def __init__(self, name, config_options):
        super().__init__(name, config_options)
        self.missing_on_error = self.needs_on_error() and not self.has_on_error()

    def needs_on_error(self):
        needs_on_error = False
        for value in self.config_options.values():
            needs_on_error = needs_on_error or value.needs_on_error
        return needs_on_error
    
    def __str__(self):
        config_options_string = ""
        for value in self.config_options.values():
            config_options_string += f"{str(value)} "
        return f"mutate {{ {config_options_string}}}"
    
class Grok(Function):
    def __init__(self, name, config_options):
        super().__init__(name, config_options)

class Date(Function):
    def __init__(self, name, config_options):
        super().__init__(name, config_options)

# Function option classes and sub-classes
class FunctionOption:
    def __init__(self, option_name, value):
        self.name = option_name
        self.value = value
        self.needs_on_error = False

    def __str__(self):
        return ""

# class for function options that take a hash as input
class Hash(FunctionOption):
    def __init__(self, option_name, value):
        assert isinstance(value, dict)
        super().__init__(option_name, value)
        self.source_variables = []
        self.target_variables = []

    def __str__(self):
        kv_string = ""
        for key, value in self.value.items():
            kv_string += f"\"{key}\" => \"{value}\" "
        return f"{self.name} => {{ {kv_string}}}"

class Replace(Hash):
    def __init__(self, value):
        super().__init__("replace", value)
        self.source_variables = self.search_for_source_variables()
        self.target_variables = list(self.value.keys())
        self.needs_on_error = True if self.source_variables != [] else False # replaces only need on_error if source variables are used

    # return a list of source variable names
    def search_for_source_variables(self):
        pattern = re.compile(r"%[{]([^}]+)[}]")
        all_values_in_string = ''.join(self.value.values()) # join all values into one big string, then regex match the string
        matches = re.findall(pattern, all_values_in_string)
        return matches
            

class Merge(Hash):
    def __init__(self, value):
        super().__init__("merge", value)
        self.source_variables = list(self.value.values())
        self.target_variables = list(self.value.keys())

class Rename(Hash):
    def __init__(self, value):
        super().__init__("rename", value)
        self.source_variables = list(self.value.keys())
        self.target_variables = list(self.value.values())

class Copy(Hash):
    def __init__(self, value):
        super().__init__("copy", value)
        self.source_variables = list(self.value.values())
        self.target_variables = list(self.value.keys())

class GrokMatch(Hash):
    def __init__(self, value):
        super().__init__("match", value)
        self.source = self.value[0]

# class for function objects that take a list as input
class List(FunctionOption):
    def __init__(self, option_name, value):
        assert isinstance(value, list)
        super().__init__(option_name, value)

class DateMatch(List):
    def __init__(self, value):
        super().__init__("match", value)
        self.source = self.value[0]

# class for function objects that take a literal value (usually string or boolean) as input
class Lit(FunctionOption):
    def __init__(self, option_name, value):
        assert isinstance(value, str)
        super().__init__(option_name, value)

class OnError(Lit):
    def __init__(self, value):
        super().__init__("on_error", value)

# Conditional classes and sub-classes
class Conditional:
    def __init__(self, name, statement=None, contents=None):
        self.name = name
        self.statement = statement
        self.contents = contents

# Loop classes and sub-classes
class Loop:
    def __init__(self, statement, contents):
        self.name = "for"
        self.statement = statement
        self.contents = contents