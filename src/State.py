from AST import *

class State:
    def __init__(self, ast):
        self.ast = ast
        self.values_used = []
        # self.functions_used = [] come back to later maybe
        self.value_occurrances = {}
        self.scan_tree(self.ast)

    def scan_tree(self, root):
        for thing in root:
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
        return None
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