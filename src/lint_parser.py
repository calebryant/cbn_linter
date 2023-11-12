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
parser.add_argument('-e', '--show_errors', action='store_true', help="Print the parser's errors to terminal")
parser.add_argument('-s', '--print_state', action='store_true', help="Print the parser's state values to the terminal")

args = parser.parse_args()

config_file = args.config_file
show_errors = args.show_errors
print_state = args.print_state

if config_file:
    grammar = Grammar()
    try:
        open_file = open(config_file)
        file_string = open_file.read()
        tokens = grammar.parse_string(file_string)
        ast = AST(tokens)
        the_state = ast.get_state()
        print(f"state: {the_state}")
        state = State(ast)

    except exceptions.ParseSyntaxException as oopsie:
        print(oopsie.explain())
        exit(1)
    
    if show_errors:
        for errors in the_state.errors:
            print(f"{config_file}, {errors}")
    
    if print_state:
        for value in sorted(the_state.values_used):
            print(value)

else:
    print("No config file provided... Exiting")
    exit(0)
