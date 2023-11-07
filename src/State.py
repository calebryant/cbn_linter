from AST import *
import re

class State:
    def __init__(self, ast):
        self.ast = ast
        self.values_used = []
        # self.functions_used = [] come back to later maybe
        self.value_occurrances = {}
        self.scan_tree(self.ast.filter)

    def __init__(self):
        self.values_used = []
        self.value_occurrances = {}
        

    #def add_token(self,token):
    #    self.values_used.append(token.value)
    #    try:
    #        self.value_occurrances[token.value] += 1
    #    except KeyError as e:
    #        self.value_occurrances[token.value] = 0

    def add_variable(self, variable_name):
        current_var = ''
        index = 0
        for sub_variable in variable_name.split('.'):
            current_var += f".{sub_variable}"
            if index == 0:
                current_var = current_var[1:]
            index += 1

            if current_var[0:6] != 'column':
                print(f"+ adding {current_var} to state")
            self.values_used.append(current_var)
            try:
                self.value_occurrances[current_var] += 1
            except KeyError as e:
                self.value_occurrances[current_var] = 1

    def does_variable_exist(self, variable):
        if not isinstance(variable, str):
            print(f"= testing if '{variable}' is in the state: False")
            return False
        try:
            self.value_occurrances[variable]
            print(f"= testing if '{variable}' is in the state: True")
            return True
        except KeyError:
            print(f"= testing if '{variable}' is in the state: False")
            return False

    def add_value(self, value):
        self.add_variable(value)

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
        state_data_set = set() # list of variable names that are added to state data in the grok function
        state_data_used = set() # list of varible names that are used in the grok function i.e. it needs to exist in state data already
        errors = []
        # Handle the match value
        for pair in match.value.pairs: # match.value is always a hash
            state_data_used = state_data_used.union({pair.left_value.value})
            patterns = pair.right_value # patterns can be either a StringToken or it can be a List
            if isinstance(patterns, List):
                for value in patterns.values:
                    state_data_set = state_data_set.union(set(self.parse_grok_pattern(value.value)))
            elif isinstance(patterns, StringToken):
                state_data_set = state_data_set.union(set(self.parse_grok_pattern(patterns.value)))
        state_data_set = state_data_set
        state_data_used = state_data_used
        # Handle the overwrite value
        overwrite = grok.config["overwrite"]
        if not overwrite: 
            errors.append(f"Grok function at line {grok.keyword.row} missing overwrite.")
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
                formatted_values = ', '.join([f'"{value}"' for value in missing_values])
                errors.append(f"Grok function at line {grok.keyword.row} missing values from overwrite: {formatted_values}")
        # Handle the on_error
        on_error = grok.config["on_error"]
        if not on_error:
            errors.append(f"Grok function at line {grok.keyword.row} missing on_error.")
        else:
            state_data_set = state_data_set.union(on_error.value.value)
            state_data_set = state_data_set.union()
        return list(state_data_set), list(state_data_used), errors
    # takes a grok pattern and returns a list of state data values set in the pattern
    def parse_grok_pattern(self, pattern):
        matches = re.findall("%\{[^}]+?:([^}]+?)\}", pattern) # matches '%{IP:value}' values in grok patterns
        matches += re.findall("\?P<([^>]+)>", pattern) # matches '(?P<value>whatever is here)' values in grok patterns
        return matches

    def check_json(self, json):
        source = json.config["source"]
        target = json.config["target"]
        array_function = json.config["array_function"]
        on_error = json.config["on_error"]
        return None
    def check_xml(self, xml):
        source = xml.config["source"]
        target = xml.config["target"]
        xpath = xml.config["xpath"]
        on_error = xml.config["on_error"]
        return None
    def check_kv(self, kv):
        source = kv.config["source"]
        target = kv.config["target"]
        field_split = kv.config["field_split"]
        unescape_field_split = kv.config["unescape_field_split"]
        value_split = kv.config["value_split"]
        unescape_value_split = kv.config["unescape_value_split"]
        whitespace = kv.config["whitespace"]
        trim_value = kv.config["trim_value"]
        on_error = kv.config["on_error"]
        return None
    def check_csv(self, csv):
        source = csv.config["source"]
        target = csv.config["target"]
        separator = csv.config["separator"]
        unescape_separator = csv.config["unescape_separator"]
        return None
    def check_mutate(self, mutate):
        convert = mutate.config["convert"]
        gsub = mutate.config["gsub"]
        lowercase = mutate.config["lowercase"]
        merge = mutate.config["merge"]
        rename = mutate.config["rename"]
        replace = mutate.config["replace"]
        uppercase = mutate.config["uppercase"]
        remove_field = mutate.config["remove_field"]
        copy = mutate.config["copy"]
        split = mutate.config["split"]
        on_error = mutate.config["on_error"]
        return None
    def check_base64(self, base64):
        source = base64.config["source"]
        target = base64.config["target"]
        encoding = base64.config["encoding"]
        on_error = base64.config["on_error"]
        return None
    def check_date(self, date):
        match = date.config["match"]
        source = date.config["source"]
        target = date.config["target"]
        timezone = date.config["timezone"]
        rebase = date.config["rebase"]
        on_error = date.config["on_error"]
        return None
    def check_drop(self, drop):
        tag = drop.config["tag"]
        return None
    def check_statedump(self, statedump):
        label = statedump.config["label"]
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

    def __str__(self):
        return f"I am a state with {len(self.value_occurrances.keys())} values"

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
