class State:
    def __init__(self):
        self.values_used = []
        # self.functions_used = [] come back to later maybe
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

            print(f"+ adding {current_var} to state")
            self.values_used.append(current_var)
            try:
                self.value_occurrances[current_var] += 1
            except KeyError as e:
                self.value_occurrances[current_var] = 1

    def add_value(self, value):
        self.add_variable(value)

    def remove_value(self, token):
        self.values_used.remove(token.value)
        self.value_occurrances[token.value] -= 1

    def check_value(self, value_name):
        return value_name in self.values_used

    def __str__(self):
        return f"I am a state with {len(self.value_occurrances.keys())} values"
