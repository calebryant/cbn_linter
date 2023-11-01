class ConfigState:
    def __init__(self):
        self.values_used = []
        # self.functions_used = [] come back to later maybe
        self.value_occurrances = {}

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