# Created 2023/07/14
# Author: Caleb Bryant
# Title: Grammar.py
# Description: Loops through standard, override, and default parsers and attempts to parse them using the language defined in Grammar.py

import os, re, json
from Grammar import Grammar
from pyparsing import exceptions

root_dir = "/Users/tyler.slijboom/Library/CloudStorage/OneDrive - Cyderes/teleng"
standard_parsers_dir = "/Users/caleb.bryant/Library/CloudStorage/OneDrive-Cyderes/TelEng/github/cyderes-parsers/standard"
override_parsers_dir = "/Users/caleb.bryant/Library/CloudStorage/OneDrive-Cyderes/TelEng/github/cyderes-parsers/overrides"

standard_parsers_folders = sorted(os.walk(standard_parsers_dir))
override_parsers_folders = sorted(os.walk(override_parsers_dir))

language_grammar = Grammar()
failures = {}
for path, folders, filenames in standard_parsers_folders:
    if path[-5:] == '/conf':
        for name in filenames:
            print(f"{path}/{name}")
            try:
                language_grammar.parse_file(f"{path}/{name}")
            except exceptions.ParseSyntaxException as oopsie:
                failures[f"{path}/{name}"] = str(oopsie)
            except exceptions.ParseException as oopsie:
                failures[f"{path}/{name}"] = str(oopsie)
f = open("standard_failures.json", "w")
json.dump(failures, f)
f.close()
failures = {}
for path, folders, filenames in override_parsers_folders:
    if path[-5:] == '/conf':
        for name in filenames:
            print(f"{path}/{name}")
            try:
                language_grammar.parse_file(f"{path}/{name}")
            except exceptions.ParseSyntaxException as oopsie:
                failures[f"{path}/{name}"] = str(oopsie)
            except exceptions.ParseException as oopsie:
                failures[f"{path}/{name}"] = str(oopsie)
f = open("overrides_failures.json", "w")
json.dump(failures, f)
f.close()
failures = {}

# except exceptions.ParseSyntaxException as oopsie:
#     match = re.search("found '(.*)'", str(oopsie))
#     if match:
#         found = match.group(1)
#     else:
#         found = ''
#     char_num = oopsie.loc
#     line_num = oopsie.lineno
#     col_num = oopsie.col
#     print(oopsie.explain())
#     print(f"ParseSyntaxException: Found unexpected token '{found}' at (line:{line_num}, col:{col_num}), char: {char_num}")
#     print(oopsie.line)
#     print(" " * (oopsie.column - 1) + "^")
#     exit(1)

# except exceptions.ParseException as oopsie:
#     match = re.search("found '(.*)'", str(oopsie))
#     if match:
#         found = match.group(1)
#     else:
#         found = ''
#     char_num = oopsie.loc
#     line_num = oopsie.lineno
#     col_num = oopsie.col
#     print(oopsie.explain())
#     print(f"ParseSyntaxException: Found unexpected token '{found}' at (line:{line_num}, col:{col_num}), char: {char_num}")
#     print(oopsie.line)
#     print(" " * (oopsie.column - 1) + "^")
#     exit(1)
