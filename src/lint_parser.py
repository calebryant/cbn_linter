# auther: caleb.bryant@cyderes.com
# created: 2023/04/02

import argparse, re, json
from pyparsing import exceptions
from Grammar import Grammar
from AST import AST

parser = argparse.ArgumentParser(
    prog='lint_parser.py',
    description='Chronicle Parser Config Linting Tool'
)

parser.add_argument('-f', '--config_file')
parser.add_argument('-j', '--json')

args = parser.parse_args()

config_file = args.config_file
json = args.json

if config_file:
    grammar = Grammar()
    try:
        open_file = open(config_file)
        file_string = open_file.read()
        tokens = grammar.parse_string(file_string)
        ast = AST(tokens)
        # print(ast.filter.body[0].config)
    except exceptions.ParseSyntaxException as oopsie:
        match = re.search("found '(.*)'", str(oopsie))
        if match:
            found = match.group(1)
        else:
            found = ''
        char_num = oopsie.loc
        line_num = oopsie.lineno
        col_num = oopsie.col
        print(oopsie.explain())
        # print(oopsie.line)
        # print(" " * (oopsie.column - 1) + "^")
        exit(1)
    if json:
        json_tokens = ast.to_json(tokens)
        with open('tokens.json', 'w') as f:
            json.dump(json_tokens, f)
