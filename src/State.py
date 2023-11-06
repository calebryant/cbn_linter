from AST import *
import re

class State:
    def __init__(self, ast):
        self.ast = ast
        self.values_used = []
        # self.functions_used = [] come back to later maybe
        self.value_occurrances = {}
        self.scan_tree(self.ast.filter)

    def scan_tree(self, root):
        for thing in root.body:
            # TODO worry about conditionals and loops later
            # if isinstance(thing, If):
            #     # TODO do something with the statement
            #     self.scan_tree(thing.body)
            # if isinstance(thing, ElseIf):
            # if isinstance(thing, Else):
            # if isinstance(thing, For):
            if isinstance(thing, Function):
                if thing.get_name() == "grok":
                    self.check_grok(thing)
                elif thing.get_name() == "json":
                    self.check_json(thing)
                elif thing.get_name() == "xml":
                    self.check_xml(thing)
                elif thing.get_name() == "kv":
                    self.check_kv(thing)
                elif thing.get_name() == "csv":
                    self.check_csv(thing)
                elif thing.get_name() == "mutate":
                    self.check_mutate(thing)
                elif thing.get_name() == "base64":
                    self.check_base64(thing)
                elif thing.get_name() == "date":
                    self.check_date(thing)
                elif thing.get_name() == "drop":
                    self.check_drop(thing)
                elif thing.get_name() == "statedump":
                    self.check_statedump(thing)
                elif thing.get_name() == "value":
                    self.check_value(thing)


        return None

    # TODO define check functions for every type of logstash function
    def check_grok(self, grok):
        # Go through the Grok config
        match = grok.config["match"]
        overwrite = grok.config["overwrite"]
        on_error = grok.config["on_error"]
        state_data_set = set() # list of variable names that are added to state data in the grok function
        state_data_used = set() # list of varible names that are used in the grok function i.e. it needs to exist in state data already
        # Handle the match value
        for pair in match.value.pairs: # match.value is always a hash
            state_data_used = state_data_used.union({pair.left_value.value})
            patterns = pair.right_value # patterns can be either a StringToken or it can be a List
            if isinstance(patterns, List):
                for value in patterns.values:
                    state_data_set = state_data_set.union(set(self.parse_grok_pattern(value.value)))
            elif isinstance(patterns, StringToken):
                state_data_set = state_data_set.union(set(self.parse_grok_pattern(patterns.value)))
        state_data_set = list(state_data_set)
        state_data_used = list(state_data_used)
        # Handle the overwrite value
        overwrite = grok.config["overwrite"]
        if not overwrite: 
            print(f"Grok function at line {grok.keyword.row} is missing an overwrite.")
        else: 
            overwrite_list = overwrite.value
            # overwrite list can also be just a string token
            if isinstance(overwrite_list, List):
                overwrite_list = overwrite_list.as_strings()
            else:
                overwrite_list = [overwrite_list.value]
            missing_values = []
            for value in state_data_set:
                if value not in overwrite_list:
                    missing_values.append(value)
            if missing_values != []:
                print(f"Missing values from overwrite: {missing_values}")
        # Handle the on_error
        return
    # takes a grok pattern and returns a list of state data values set in the pattern
    def parse_grok_pattern(self, pattern):
        matches = re.findall("%\{[^}]+?:([^}]+?)\}", pattern) # matches '%{IP:value}' values in grok patterns
        matches += re.findall("\?P<([^>]+)>", pattern) # matches '(?P<value>whatever is here)' values in grok patterns
        return matches

    def check_json(self, json):
        return None
    def check_xml(self, xml):
        return None
    def check_kv(self, kv):
        return None
    def check_csv(self, csv):
        return None
    def check_mutate(self, mutate):
        return None
    def check_base64(self, base64):
        return None
    def check_date(self, date):
        return None
    def check_drop(self, drop):
        return None
    def check_statedump(self, statedump):
        return None
    
    def check_value(self, value):
        return None
    def add_value(self,token):
        self.values_used.append(token.value)
        try:
            self.value_occurrances[token.value] += 1
        except KeyError as e:
            self.value_occurrances[token.value] = 0

    def remove_value(self, token):
        self.values_used.remove(token.value)
        self.value_occurrances[token.value] -= 1

    def check_value(self, value_name):
        return value_name in self.values_used

class Value:
    def __init__(self, name_token, contents_token):
        self.name = name_token
        self.contents = contents_token
        self.previous_value = None

    def get_name(self):
        return self.name

    def get_name_string(self):
        return self.name

    def get_contents(self):
        return self.contents.value
  
    def get_contents_string(self):
        return self.contents.value