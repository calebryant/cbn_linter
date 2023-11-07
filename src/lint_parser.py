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

parser.add_argument('-f', '--config_file')
parser.add_argument('-e', '--show_errors')

args = parser.parse_args()

config_file = args.config_file
show_errors = args.show_errors

if config_file:
    grammar = Grammar()
    try:
        open_file = open(config_file)
        file_string = open_file.read()
        tokens = grammar.parse_string(file_string)
        ast = AST(tokens)
        #ast2 = AST(None)
        the_state = ast.get_state()
        print(f" state: {the_state}")
        print(f"The {len(the_state.errors)} errors of the state are:")
        print("\n".join(the_state.errors))
        #state = State(ast)

    except exceptions.ParseSyntaxException as oopsie:
        print(oopsie.explain())
        exit(1)
    
    if show_errors:
        for err in the_state.errors:
            print(err)

else:
    print("No config file provided... Exiting")
    exit(0)
