# auther: caleb.bryant@cyderes.com
# created: 2023/04/02

import argparse
from pyparsing import exceptions
from Grammar import Grammar
from AST import AST
from State import State
import re

def lint_cbn():
    parser = argparse.ArgumentParser(
        prog='lint_parser.py',
        description='Chronicle CBN Linting Tool'
    )

    parser.add_argument('-f', '--config_file', help="Path to the config file to lint", required=True)
    parser.add_argument('-e', '--errors', action='store_true', help="Print the parser's errors to terminal")
    parser.add_argument('-w', '--warnings', action='store_true', help="Print the parser's warnings to terminal")
    parser.add_argument('-s', '--print_state', action='store_true', help="Print the parser's state values to the terminal")
    parser.add_argument('-o', '--output', help="File path to print terminal output")
    parser.add_argument('-u', '--udm', action="store_true", help="Output a summary of all UDM fields set by the parser")

    args = parser.parse_args()

    config_file = args.config_file
    show_errors = args.errors
    show_warnings = args.warnings
    print_state = args.print_state
    output = args.output
    udm = args.udm

    if config_file:
        grammar = Grammar()
        try:
            open_file = open(config_file)
            file_string = open_file.read()
            tokens = grammar.parse_string(file_string)
            ast = AST(tokens)
            the_state = ast.state
        except exceptions.ParseSyntaxException as oopsie:
            print(oopsie.explain())
            exit(1)
        
        if show_errors:
            errors = ""
            for error in the_state.errors:
                errors += f"[ERROR] {config_file}, {error}\n"
            print(errors) if not output else None
            if the_state.errors != []:
                exit(1)
        
        if show_warnings:
            warnings = ""
            for warning in the_state.warnings:
                warnings += f"[WARN] {config_file}, {warning}\n"
            print(warnings) if not output else None
        
        if print_state:
            state = ""
            for value in sorted(the_state.value_table):
                for state_value in the_state.value_table[value]:
                    state += f"{str(state_value)}\n"
            print(state) if not output else None

        def traverse_udm(udm_dict, parent):
            for key,value in udm_dict.items():
                if isinstance(value, dict):
                    new_parent = f"{parent}.{key}" if parent != "" else key
                    traverse_udm(value, new_parent)
                elif isinstance(value, list):
                    # field_name = f"{parent}.{key}" if parent != "" else key
                    # print(field_name, [str(val) for val in value])
                    new_val = None
                    field_name = ""
                    for index in value:
                        new_val = None
                        if new_val := the_state.get_value(str(index).split('.'), the_state.value_table):
                            new_parent = f"{parent}.{key}" if parent != "" else key
                            if isinstance(new_val, list):
                                field_name = f"{parent}.{key}" if parent != "" else key
                                print(field_name, [str(val) for val in new_val])
                            else:
                                traverse_udm(new_val, new_parent)
                        # else:
                        #     field_name = f"{parent}.{key}" if parent != "" else key
                        #     print(field_name, [str(val) for val in value])

        if udm:
            udm_fields = {}
            try:
                events = the_state.value_table["@output"]
                for event in events:
                    event = str(event) + ".idm.read_only_udm"
                    if value := the_state.get_value(event.split('.'), the_state.value_table):
                        traverse_udm(value, "")
            except KeyError:
                exit(0)

    else:
        print("No config file provided... Exiting")
        exit(0)

if __name__ == "__main__":
    lint_cbn()