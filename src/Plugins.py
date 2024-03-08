# Created 2024/03/04
# Author: Caleb Bryant
# Title: Plugins.py
# Description: Plugins.py defines classes for all the different filter plugins types that can be used in a logstash configuration file.
# References: https://www.elastic.co/guide/en/logstash/current/filter-plugins.html

import re

# Filter classes and sub-classes
class Filter:
    def __init__(self, name: str, config_options: dict) -> None:
        self.name = name
        self.config_options = config_options
        self.missing_on_error = not self.has_on_error() # boolean value denoting if this function needs an on_error statement

    # returns true if the function has an on_error statement, false if not
    def has_on_error(self) -> bool:
        return True if "on_error" in self.config_options else False
    
    # returns a list of all source variables used in the function
    def get_all_source_variables(self) -> list:
        source_variables = []
        for config_op in self.config_options.values():
            if config_op.name in ["replace", "merge", "copy", "rename"]:
                source_variables += config_op.source_variables
        return source_variables

class Mutate(Filter):
    def __init__(self, name: str, config_options: dict) -> None:
        super().__init__(name, config_options)
        self.missing_on_error = self.needs_on_error() and not self.has_on_error()

    def needs_on_error(self) -> bool:
        needs_on_error = False
        for value in self.config_options.values():
            needs_on_error = needs_on_error or value.needs_on_error
        return needs_on_error
    
    def __str__(self) -> str:
        config_options_string = ""
        for value in self.config_options.values():
            config_options_string += f"{str(value)} "
        return f"mutate {{ {config_options_string}}}"
    
class Grok(Filter):
    def __init__(self, name: str, config_options: dict) -> None:
        super().__init__(name, config_options)

class Date(Filter):
    def __init__(self, name: str, config_options: dict) -> None:
        super().__init__(name, config_options)

# Function option classes and sub-classes
class FunctionOption:
    def __init__(self, option_name: str) -> None:
        self.name = option_name
        self.needs_on_error = False

    def __str__(self) -> str:
        return "TODO"

# class for function options that take a hash as input
class Hash(FunctionOption):
    def __init__(self, option_name: str, value: dict) -> None:
        super().__init__(option_name)
        self.value = value
        self.source_variables = []
        self.target_variables = []

    def __str__(self) -> str:
        kv_string = ""
        for key, value in self.value.items():
            kv_string += f"\"{key}\" => \"{value}\" "
        return f"{self.name} => {{ {kv_string}}}"

class Replace(Hash):
    def __init__(self, value: dict) -> None:
        super().__init__("replace", value)
        self.source_variables = self.search_for_source_variables()
        self.target_variables = list(self.value.keys())
        self.needs_on_error = True if self.source_variables != [] else False # replaces only need on_error if source variables are used

    # return a list of source variable names
    def search_for_source_variables(self) -> list:
        pattern = re.compile(r"%[{]([^}]+)[}]")
        all_values_in_string = ''.join(self.value.values()) # join all values into one big string, then regex match the string
        matches = re.findall(pattern, all_values_in_string)
        return matches
            

class Merge(Hash):
    def __init__(self, value: dict) -> None:
        super().__init__("merge", value)
        self.source_variables = list(self.value.values())
        self.target_variables = list(self.value.keys())

class Rename(Hash):
    def __init__(self, value: dict) -> None:
        super().__init__("rename", value)
        self.source_variables = list(self.value.keys())
        self.target_variables = list(self.value.values())

class Copy(Hash):
    def __init__(self, value: dict) -> None:
        super().__init__("copy", value)
        self.source_variables = list(self.value.values())
        self.target_variables = list(self.value.keys())

class GrokMatch(Hash):
    def __init__(self, value: dict) -> None:
        super().__init__("match", value)
        self.source = self.value[0]

# class for function objects that take a list as input
class List(FunctionOption):
    def __init__(self, option_name: str, value: list) -> None:
        super().__init__(option_name)
        self.value = value

class DateMatch(List):
    def __init__(self, value: list) -> None:
        super().__init__("match", value)
        self.source = self.value[0]

# class for function objects that take a literal value (usually string or boolean) as input
class Lit(FunctionOption):
    def __init__(self, option_name: str, value: str) -> None:
        super().__init__(option_name)
        self.value = value

class OnError(Lit):
    def __init__(self, value: str) -> None:
        super().__init__("on_error", value)

# Conditional classes and sub-classes
class Conditional:
    def __init__(self, name: str, statement=None, contents=None) -> None:
        self.name = name
        self.statement = statement
        self.contents = contents

# Loop classes and sub-classes
class Loop:
    def __init__(self, statement: list, contents) -> None:
        self.name = "for"
        self.statement = statement
        self.contents = contents