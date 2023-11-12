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

    def update_state(self, state):
        print(f"CSV class here updating state")
        for num in range(1,101):
            state.add_implicit_value(f"column{num}")
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
        elif split or copy or merge or convert: # split, copy, merge, and convert always need on_error statements 
            state.add_error(f"line {self.keyword.row}, mutate function missing on_error statement")
        elif replace and replace.does_replace_string_contain_variables(): # replace does not need an on_error if no values are used in the right side
            state.add_error(f"line {self.keyword.row}, mutate function missing on_error statement")
        elif rename and not rename.source_already_exists(state): # rename only needs an on_error if the source (left) field does not exist
                state.add_error(f"line {self.keyword.row}, mutate function missing on_error statement")


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
            state.add_to_value_table(destination, source )

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
        
    def source_already_exists(self, state):
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
