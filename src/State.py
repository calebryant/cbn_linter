from AST import *
import re

class State:
    def __init__(self, ast):
        self.ast = ast
        self.explicit_values = {} # values that we know for sure will exist in state data
        self.implicit_values = {} # values that might exist in state data depending on an error
        self.errors = []
        self.scan_tree(self.ast.filter)

    def scan_tree(self, root):
        for thing in root.body:
            if isinstance(thing, If):
                # TODO do something with the statement
                self.scan_tree(thing)
            if isinstance(thing, ElseIf):
                self.scan_tree(thing)
            if isinstance(thing, Else):
                self.scan_tree(thing)
            if isinstance(thing, For):
                self.scan_tree(thing)
            if isinstance(thing, Function):
                if thing.get_name() == "grok":
                    used = self.check_grok(thing)
                elif thing.get_name() == "json":
                    used = self.check_json(thing)
                elif thing.get_name() == "xml":
                    used = self.check_xml(thing)
                elif thing.get_name() == "kv":
                    used = self.check_kv(thing)
                elif thing.get_name() == "csv":
                    used = self.check_csv(thing)
                elif thing.get_name() == "mutate":
                    used = self.check_mutate(thing)
                elif thing.get_name() == "base64":
                    used = self.check_base64(thing)
                elif thing.get_name() == "date":
                    used = self.check_date(thing)
                elif thing.get_name() == "drop":
                    used = self.check_drop(thing)
                elif thing.get_name() == "statedump":
                    used = self.check_statedump(thing)
        return None

    def check_grok(self, grok):
        # Go through the Grok config
        match = grok.config["match"]
        state_data_added = set() # list of variable names that are added to state data in the grok function
        state_data_used = set() # list of varible names that are used in the grok function i.e. it needs to exist in state data already
        # Handle the match value
        for pair in match.value.pairs: # match.value is always a hash
            state_data_used = state_data_used.union({pair.left_value.value})
            patterns = pair.right_value # patterns can be either a StringToken or it can be a List
            if isinstance(patterns, List):
                for value in patterns.values:
                    state_data_added = state_data_added.union(set(self.parse_grok_pattern(value.value)))
                    for name in state_data_added:
                        self.add_implicit_value(name, pair.left_value.row)
            elif isinstance(patterns, StringToken):
                state_data_added = state_data_added.union(set(self.parse_grok_pattern(patterns.value)))
                self.add_implicit_value(patterns)
        # Handle the overwrite value
        overwrite = grok.config["overwrite"]
        if not overwrite: 
            self.add_error(f"Grok function at line {grok.keyword.row} missing overwrite.")
        else: 
            overwrite_list = overwrite.value
            # overwrite list can also be just a string token
            if isinstance(overwrite_list, List):
                overwrite_list = overwrite_list.as_strings()
            else:
                overwrite_list = [overwrite_list.value]
            missing_values = []
            for value in state_data_added:
                if value not in overwrite_list:
                    missing_values.append(value)
            if missing_values != []:
                formatted_values = ', '.join([f'"{value}"' for value in missing_values])
                self.add_error(f"Grok function at line {grok.keyword.row} missing overwrites: {formatted_values}")
        # Handle the on_error
        on_error = grok.config["on_error"]
        if not on_error:
            self.add_error(f"Grok function at line {grok.keyword.row} missing on_error.")
        else:
            self.add_explicit_value(on_error.value)
        return list(state_data_used)

    # takes a grok pattern and returns a list of state data values used in the pattern
    def parse_grok_pattern(self, pattern):
        matches = re.findall("%\{[^}]+?:([^}]+?)\}", pattern) # matches '%{IP:value}' values in grok patterns
        matches += re.findall("\?P<([^>]+)>", pattern) # matches '(?P<value>whatever is here)' values in grok patterns
        return matches

    def check_json(self, json):
        state_data_used = []
        source = json.config["source"]
        if source:
            state_data_used.append(source.value.value)
        target = json.config["target"]
        if target:
            self.add_implicit_value(target.value)
        array_function = json.config["array_function"]
        on_error = json.config["on_error"]
        if not on_error:
            self.add_error(f"JSON function at line {json.keyword.row} missing on_error.")
        else: 
            self.add_explicit_value(on_error.value)
        return state_data_used

    def check_xml(self, xml):
        errors = []
        source = xml.config["source"]
        target = xml.config["target"]
        if target:
            self.add_implicit_value(target.value)
        xpath = xml.config["xpath"]
        on_error = xml.config["on_error"]
        if not on_error:
            self.add_error(f"XML function at line {xml.keyword.row} missing on_error.")
        else: 
            self.add_explicit_value(on_error.value)

    def check_kv(self, kv):
        errors = []
        source = kv.config["source"]
        target = kv.config["target"]
        if target:
            self.add_implicit_value(target.value)
        field_split = kv.config["field_split"]
        unescape_field_split = kv.config["unescape_field_split"]
        value_split = kv.config["value_split"]
        unescape_value_split = kv.config["unescape_value_split"]
        whitespace = kv.config["whitespace"]
        trim_value = kv.config["trim_value"]
        on_error = kv.config["on_error"]
        if not on_error:
            self.add_error(f"KV function at line {kv.keyword.row} missing on_error.")
        else: 
            self.add_explicit_value(on_error.value)

    def check_csv(self, csv):
        errors = []
        source = csv.config["source"]
        target = csv.config["target"]
        if target:
            self.add_implicit_value(target.value)
        separator = csv.config["separator"]
        unescape_separator = csv.config["unescape_separator"]
        on_error = kv.config["on_error"]
        if not on_error:
            self.add_error(f"CSV function at line {csv.keyword.row} missing on_error.")
        else: 
            self.add_explicit_value(on_error.value)
            
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
        if not on_error:
            self.add_error(f"Mutate function at line {mutate.keyword.row} missing on_error.")
        else: 
            self.add_explicit_value(on_error.value)

    def check_base64(self, base64):
        errors = []
        source = base64.config["source"]
        target = base64.config["target"]
        if target:
            self.add_implicit_value(target.value)
        encoding = base64.config["encoding"]

    def check_date(self, date):
        errors = []
        match = date.config["match"]
        source = date.config["source"]
        target = date.config["target"]
        if target:
            self.add_implicit_value(target.value)
        timezone = date.config["timezone"]
        rebase = date.config["rebase"]
        on_error = date.config["on_error"]
        if not on_error:
            self.add_error(f"Date function at line {date.keyword.row} missing on_error.")
        else: 
            self.add_explicit_value(on_error.value)

    def check_drop(self, drop):
        tag = drop.config["tag"]

    def check_statedump(self, statedump):
        label = statedump.config["label"]

    def add_explicit_value(self, *args):
        if len(args) == 1:
            try:
                self.explicit_values[args[0].value].append(args[0].row)
            except KeyError:
                self.explicit_values[args[0].value] = [args[0].row]
        elif len(args) == 2:
            try:
                self.explicit_values[args[0]].append(args[1])
            except KeyError:
                self.explicit_values[args[0]] = [args[1]]

    def add_implicit_value(self, *args):
        if len(args) == 1:
            try:
                self.implicit_values[args[0].value].append(args[0].row)
            except KeyError:
                self.implicit_values[args[0].value] = [args[0].row]
        elif len(args) == 2:
            try:
                self.implicit_values[args[0]].append(args[1])
            except KeyError:
                self.implicit_values[args[0]] = [args[1]]

    def remove_value(self, token):
        self.values.remove(token.value)

    def check_value(self, value_name):
        return value_name in self.values_used

    def add_error(self, error_string):
        self.errors.append(error_string)