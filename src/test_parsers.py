import os
from Grammar import Grammar

standard_parsers_dir = "/Users/caleb.bryant/Library/CloudStorage/OneDrive-Cyderes/TelEng/github/cyderes-parsers/standard"
override_parsers_dir = "/Users/caleb.bryant/Library/CloudStorage/OneDrive-Cyderes/TelEng/github/cyderes-parsers/overrides"
default_parsers_dir = "/Users/caleb.bryant/Library/CloudStorage/OneDrive-Cyderes/TelEng/github/chronicle-parsers"

standard_parsers_folders = sorted(os.walk(standard_parsers_dir))
override_parsers_folders = sorted(os.walk(override_parsers_dir))
default_parsers_folders = sorted(os.walk(default_parsers_dir))

results = open('results.txt', 'w')
results.write("Parsing results\n")

language_grammar = Grammar()

for path, folders, filenames in standard_parsers_folders:
    if path[-5:] == '/conf':
        for name in filenames:
            print(f"{path}/{name}")
            results.write(f"{path}/{name}\n")
            parse_attempt = language_grammar.parse_file(f"{path}/{name}")
            if not parse_attempt:
                exit(0)

for path, folders, filenames in override_parsers_folders:
    if path[-5:] == '/conf':
        for name in filenames:
            print(f"{path}/{name}")
            results.write(f"{path}/{name}\n")
            parse_attempt = language_grammar.parse_file(f"{path}/{name}")
            if not parse_attempt:
                exit(0)

for path, folders, filenames in default_parsers_folders:
    if len(folders) == 0:
        for name in filenames:
            print(f"{path}/{name}")
            results.write(f"{path}/{name}\n")
            parse_attempt = language_grammar.parse_file(f"{path}/{name}")
            if not parse_attempt:
                exit(0)
    else:
        for folder in folders:
            for name in filenames:
                print(f"{path}/{name}")
                results.write(f"{path}/{name}\n")
                parse_attempt = language_grammar.parse_file(f"{path}/{folder}/{name}")
                if not parse_attempt:
                    exit(0)