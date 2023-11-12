# auther: caleb.bryant@cyderes.com
# created: 2023/04/02

import argparse, re, json
from pyparsing import exceptions
from Grammar import Grammar
from AST import AST
from State import *

parser = argparse.ArgumentParser(
    prog='lint_parser.py',
    description='Chronicle CBN Linting Tool'
)

parser.add_argument('-f', '--config_file', help="Path to the config file to lint")
parser.add_argument('-e', '--errors', action='store_true', help="Print the parser's errors to terminal")
parser.add_argument('-w', '--warnings', action='store_true', help="Print the parser's warnings to terminal")
parser.add_argument('-s', '--print_state', action='store_true', help="Print the parser's state values to the terminal")
parser.add_argument('-o', '--output', help="File path to print terminal output")

args = parser.parse_args()

config_file = args.config_file
show_errors = args.errors
show_warnings = args.warnings
print_state = args.print_state
output = args.output

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
        for errors in the_state.errors:
            print(f"[ERROR] {config_file}, {errors}")
    
    if show_warnings:
        for warning in the_state.warnings:
            print(f"[WARN] {config_file}, {warning}")
    
    if print_state:
        for value in sorted(the_state.value_table):
            for state_value in the_state.value_table[value]:
                print(str(state_value))

    if the_state.errors != []:
        exit(1)

    # if the_state.warnings != []:
    #     exit(2)

else:
    print("No config file provided... Exiting")
    exit(0)
