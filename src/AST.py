# Created 2023/07/17
# Author: Caleb Bryant
# Title: AST.py
# Description: This file defines a class to represent a Chronicle parser as an abstract syntax tree. This allows us to check for semantic errors easier. 
# References: https://en.wikipedia.org/wiki/Abstract_syntax_tree
# References: https://www.elastic.co/guide/en/logstash/current/filter-plugins.html

from State import *
import re

# Function classes and sub-classes
class Function:
    def __init__(self, name, config_options):
        self.name = name
        self.config_options = config_options
        self.missing_on_error = not self.has_on_error()

    def has_on_error(self):
        try:
            value = self.config_options["on_error"]
            return False
        except KeyError:
            return True

class Mutate(Function):
    def __init__(self, name, config_options):
        super().__init__(name, config_options)
        allowed_config_options = {
            "convert": None,
            "gsub": None,
            "lowercase": None,
            "merge": None,
            "rename": None,
            "replace": None,
            "uppercase": None,
            "remove_field": None,
            "copy": None,
            "split": None,
            "on_error": None
        }
        allowed_config_options.update(self.config_options)
        self.missing_on_error = not (self.needs_on_error() and self.has_on_error())

    def needs_on_error(self):
        needs_on_error = False
        for option, value in self.config_options:
            needs_on_error = needs_on_error and value.needs_on_error()
        return needs_on_error

class Grok(Function):
    def __init__(self, name, config_options):
        super().__init__(name, config_options)
        allowed_config_options = {
            "match": None,
            "overwrite": None,
            "on_error": None,
        }
        allowed_config_options.update(self.config_options)

class Date(Function):
    def __init__(self, name, config_options):
        super().__init__(name, config_options)
        allowed_config_options = {
            "match": None,
            "timezone": None,
            "on_error": None
        }
        allowed_config_options.update(self.config_options)

# Function option classes and sub-classes
class FunctionOption:
    def __init__(self, option_name, value):
        self.name = option_name
        self.value = value

    def needs_on_error(self):
        return False

class OnError(FunctionOption):
    def __init__(self, option_name, value):
        super().__init__(option_name, value)

class Hash(FunctionOption):
    def __init__(self, option_name, value):
        assert isinstance(value, dict)
        super().__init__(option_name, value)

class Replace(Hash):
    def __init__(self, value):
        super().__init__("replace", value)
        self.missing_on_error = self.needs_on_error() and self.has_on_error()

    # checks all values of key value pairs for %{} variables, if none are present then an on_error is not needed
    def needs_on_error(self):
        pattern = re.compile(r"%[{][^}][}]")
        all_values_in_string = ''.join(self.value.values()) # join all values into one big string, then regex match the string
        return False if re.search(pattern, all_values_in_string) else True

class Merge(Hash):
    def __init__(self, value):
        super().__init__("merge", value)

class Rename(Hash):
    def __init__(self, value):
        super().__init__("rename", value)

class List(FunctionOption):
    def __init__(self, option_name, value):
        assert isinstance(value, list)
        super().__init__(option_name, value)

class Lit(FunctionOption):
    def __init__(self, option_name, value):
        assert isinstance(value, str)
        super().__init__(option_name, value)

# Conditional classes and sub-classes
class Conditional:
    def __init__(self, tokens):
        self.name = tokens[0]
        if self.name != "else":
            self.statement = tokens[1]
            self.contents = tokens[2:]
        else:
            self.statement = None
            self.contents = tokens[1:]

# Loop classes and sub-classes
class Loop:
    def __init__(self, tokens):
        self.name = name
        self.statement = statement
        self.contents = contents