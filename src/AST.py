# Created 2023/07/17
# Author: Caleb Bryant
# Title: AST.py
# Description: This file defines a class to represent a Chronicle parser as an abstract syntax tree. This allows us to check for semantic errors easier. 
# References: https://en.wikipedia.org/wiki/Abstract_syntax_tree

from Tokens import *
from State import State
from pyparsing import ParseSyntaxException, ParseFatalException
import re


class AST:
    def __init__(self, filter_object):
        self.filter = filter_object
        self.state = self.get_state()

    def get_state(self):
        state = State()
        self.filter.update_state(state)
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

    def update_state(self, state):
        if isinstance(self.statement, ConditionalStatement):
            self.statement.update_state(state)
        # elif isinstance(self.statement, LoopStatement)
        state.push_scope()
        for child in self.body:
            child.update_state(state)
        state.pop_scope()

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

    def update_state(self, state):
        for token in self.tokens:
            if isinstance(token, ConditionalToken) and not state.found_in_explicit_state(token.get_name()):
                if state.found_in_implicit_state(token.get_name()):
                    state.add_error(f"line {token.tokens[0].row}, implicit value '{token.get_name()}' used in conditional statement, this value was used previously in the parser but is not guaranteed to exist in the state")
                else: 
                    state.add_error(f"line {token.tokens[0].row}, undeclared value '{token.get_name()}' used in conditional statement, this value is not guaranteed to exist in the state")

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

    def get_config(self):
        return self.config

    def update_state(self, state):
        source = self.config["source"]
        target = self.config["target"]
        on_error = self.config["on_error"]
        # if source: # TODO revisit if this is actually needed, as of now I don't think a warning needs to be raised for a missing source field since it can't cause errors if an on_error statement is present
        #     source.update_state(state)
        if not source and not isinstance(self, Date): # date does not have to have a source 
            state.add_error(f"line {self.keyword.row}, {str(self.keyword)} function missing source statement")
        if target: # target is not a required setting
            target.update_state(state)
        if on_error:
            on_error.update_state(state)
        else:
            state.add_error(f"line {self.keyword.row}, {str(self.keyword)} function missing on_error statement")
        
    def set_config(self, config):
        # Loop through the list of function configs
        for value in config[2:-1]:
            keyword = value.keyword.value # get the function config keyword
            if keyword in self.config:
                if self.config[keyword] == None:
                    self.config[keyword] = value
                else:
                    raise Exception(f"line {int(value)}, multiple {keyword} statements in {str(self.keyword)} not allowed")

    # return the keyword of the function
    def get_name(self):
        return self.keyword.value

    def __int__(self):
        return self.keyword.row

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
        try:
            assert isinstance(self.config["match"].value, Hash)
        except AssertionError:
            lineno = int(self.config["match"])
            raise Exception(f"line {lineno}, value given to grok match setting MUST be of type hash")

    def update_state(self, state):
        # Handle the match setting
        match = self.config["match"]
        if match:
            # get all the values used in each grok pattern
            pattern_values = match.update_state(state)
            for value in pattern_values: state.add_implicit_value(value)
        else:
            state.add_error(f"line {grok.keyword.row}, grok missing match configuration")
        # Handle the overwrite setting
        overwrite = self.config["overwrite"]
        if overwrite:
            missing_values = overwrite.check_values(pattern_values)
            overwrite.update_state(state)
            state.add_error(f"line {self.keyword.row}, grok function missing overwrite values: {missing_values}") if missing_values else None
        else:
            state.add_error(f"line {self.keyword.row}, grok function missing overwrite statement")
        # Handle the on_error setting
        on_error = self.config["on_error"]
        if on_error:
            on_error.update_state(state)
        else:
            state.add_error(f"line {self.keyword.row}, grok function missing on_error statement")

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

    def update_state(self, state):
        super().update_state(state)

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

    def update_state(self, state):
        super().update_state(state)

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

    def update_state(self, state):
        super().update_state(state)

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

    def update_state(self, state):
        super().update_state(state)

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

    def update_state(self, state):
        convert = self.config["convert"]
        if convert:
            convert.update_state(state)
        gsub = self.config["gsub"]
        if gsub:
            gsub.update_state(state)
        lowercase = self.config["lowercase"]
        if lowercase:
            lowercase.update_state(state)
        merge = self.config["merge"]
        if merge:
            merge.update_state(state)
        rename = self.config["rename"]
        if rename:
            rename.update_state(state)
        replace = self.config["replace"]
        if replace:
            replace.update_state(state)
        uppercase = self.config["uppercase"]
        if uppercase:
            uppercase.update_state(state)
        remove_field = self.config["remove_field"]
        if remove_field:
            remove_field.update_state(state)
        copy = self.config["copy"]
        if copy:
            copy.update_state(state)
        split = self.config["split"]
        if split:
            split.update_state(state)
        on_error = self.config["on_error"]
        if on_error:
            on_error.update_state(state)
        elif rename or split or copy or merge or convert: # split, copy, merge, and convert always need on_error statements 
            state.add_error(f"line {self.keyword.row}, mutate function missing on_error statement")
        elif replace and replace.does_replace_string_contain_variables(): # replace does not need an on_error if no values are used in the right side
            state.add_error(f"line {self.keyword.row}, mutate function missing on_error statement")
        # elif rename: # rename only needs an on_error if the destination (right) field already exists
        #         state.add_error(f"line {self.keyword.row}, mutate function missing on_error statement")

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

    def update_state(self, state):
        super().update_state(state)

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
        try:
            assert isinstance(self.config["match"].value, List)
        except AssertionError:
            lineno = int(self.config["match"])
            raise Exception(f"line {lineno}, value given to date match setting MUST be of type list")

    def update_state(self, state):
        super().update_state(state)

class Drop(Function):
    def __init__(self, config):
        super().__init__(config)
        self.config = {
            "tag" : None
        }
        self.set_config(config)

    def update_state(self, state):
        pass

class Statedump(Function):
    def __init__(self, config):
        super().__init__(config)
        self.config = {
            "label" : None
        }
        self.set_config(config)

    def update_state(self, state):
        pass

class FunctionConfig:
    def __init__(self, config):
        self.keyword = config[0]
        self.assign = config[1]
        self.value = config[2]
        self.comma = config[-1] if type(config[-1]) == CommaToken else None

    def update_state(self, state):
        pass

    def __int__(self):
        return self.keyword.row

    def __str__(self):
        return str(self.keyword) + str(self.assign) + str(self.value)

class Match(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

    def update_state(self, state):
        source_fields = self.value.get_left_values()
        # for source_field in source_fields: # TODO revisit if this is needed
        #     if state.found_in_implicit_state(source_field):
        #         state.add_warning(f"line {int(self.keyword)}, implicit value '{source_field}' used in grok match source, this value was used previously in the parser but is not guaranteed to exist in the state")
        #     # if the source value is not implicitly defined, it could still exist via a json filter or something else
        #     else:
        #         state.add_warning(f"line {int(self.keyword)}, value '{source_field}' used in grok match source is not defined in the parser, it could exist in state data but is not guaranteed")
        values_used = self.get_values_from_pattern()
        for value in values_used:
            state.add_implicit_value(value)
        return values_used
    
    # return a list of all variables used in a grok
    # also adds variables used in the grok pattern to the value table
    def get_values_from_pattern(self):
        for pair in self.value.pairs:
            variables_used_in_patterns = []
            patterns = pair.right_value # patterns can be either a StringToken or it can be a List
            if isinstance(patterns, List):
                values = set()
                for value in patterns.values:
                    values = values.union(set(self.parse_grok_pattern(str(value))))
                    for name in values:
                        variables_used_in_patterns.append(name) if name not in variables_used_in_patterns else None
            elif isinstance(patterns, StringToken):
                return self.parse_grok_pattern(patterns.value)
        return variables_used_in_patterns

    def parse_grok_pattern(self, pattern):
        matches = re.findall("%\{[^}]+?:([^}]+?)\}", pattern) # matches '%{IP:value}' values in grok patterns
        matches += re.findall("\?P<([^>]+)>", pattern) # matches '(?P<value>whatever is here)' values in grok patterns
        return matches

class Overwrite(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

    def update_state(self, state):
        for val in self.value.values:
            state.add_to_value_table(val, None)

    # checks if values used in a grok pattern also exist in the overwrite statement
    def check_values(self, variables_used_in_patterns):
        overwrite_list = self.value
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
            return formatted_values
        else:
            return None

class OnError(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

    def update_state(self, state):
        state.add_explicit_value(str(self.value))
        state.add_to_value_table(self.value, None)

class Source(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

    def update_state(self, state):
        # if the source value is not explicitly defined
        if not state.found_in_explicit_state(str(self.value)):
            # if the source value IS implicitly defined, i.e. it might exist but is not guaranteed
            if state.found_in_implicit_state(str(self.value)):
                state.add_warning(f"line {int(self.value)}, implicit value '{str(self.value)}' used in source, this value was used previously in the parser but is not guaranteed to exist in the state")
            # if the source value is not implicitly defined, it could also exist via a json filter or something else
            else:
                state.add_warning(f"line {int(self.value)}, implicit value '{str(self.value)}' used in source is not defined in the parser, it could exist in state data but is not guaranteed")

class Target(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

    def update_state(self, state):
        state.add_implicit_value(str(self.value))
        state.add_to_value_table(self.value, None)

class ArrayFunction(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

class Xpath(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

class FieldSplit(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

class UnescapeFieldSplit(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

class ValueSplit(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

class UnescapeValueSplit(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

class Whitespace(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

class TrimValue(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

class Separator(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

class UnescapeSeparator(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

class Convert(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

class Gsub(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

class Lowercase(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

class Merge(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

    def update_state(self, state):
        for kv in self.value.pairs:
            source = kv.right_value
            destination = kv.left_value
            state.add_implicit_value(str(destination))
            state.add_to_value_table(destination, source)

class Rename(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)
    
    def update_state(self, state):
        for kv in self.value.pairs:
            source = kv.left_value
            if state.found_in_explicit_state(str(source)):
                state.rename_explicit_value(str(source))
            if state.found_in_implicit_state(str(source)):
                state.rename_implicit_value(str(source))
            destination = kv.right_value
            state.add_implicit_value(str(destination))
            state.add_to_value_table(destination, source)
        
    def destination_already_exists(self, state):
        source_values = self.value.get_left_values()
        for val in source_values:
            if not state.found_in_explicit_state(str(val)):
                return False
        return True

class Replace(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

    def update_state(self, state):
        for kv in self.value.pairs:
            source = kv.right_value
            destination = kv.left_value
            state.add_implicit_value(str(destination))
            state.add_to_value_table(destination, source)

    def does_replace_string_contain_variables(self):
        for kv in self.value.pairs:
            source_string = str(kv.right_value)
            if re.match(r"%[{][^}]+[}]", source_string): # matches '%{.*}' values
                return True
            else: 
                return False

class Uppercase(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

class RemoveField(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

class Copy(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

    def update_state(self, state):
        for kv in self.value.pairs:
            source = kv.right_value
            destination = kv.left_value
            state.add_implicit_value(str(destination))
            state.add_to_value_table(destination, source)

class Split(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

    def update_state(self, state):
        for kv in self.value.pairs:
            if str(kv.left_value) == "target":
                state.add_implicit_value(str(kv.right_value))
                state.add_to_value_table(kv.right_value, None)

class Encoding(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

class Timezone(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

class Rebase(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

class Tag(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

class Label(FunctionConfig):
    def __init__(self, config):
        super().__init__(config)

class Hash:
    def __init__(self, config):
        self.begin = config[0]
        self.pairs = config[1:-1]
        self.end = config[-1]

    def get_values(self):
        left_values = []
        right_values = []
        for pair in self.pairs:
            left_values.append(pair.left_value)
            right_values.append(pair.right_value)
        return left_values, right_values

    def get_left_values(self):
        return_list = []
        for pair in self.pairs:
            return_list.append(pair.left_value)
        return return_list

    def get_right_values(self):
        return_list = []
        for pair in self.pairs:
            return_list.append(pair.right_value)
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
    
    # Returns the Logstash list object as a python list of string values
    def as_strings(self):
        strings = []
        for value in self.values:
            strings.append(value.value)
        return strings

    def get_values(self):
        return self.values

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
