# author: caleb.bryant@cyderes.com
# created: 2023/04/02

import argparse
from pyparsing import exceptions
from Parser import Parser

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

    args = parser.parse_args()

    config_file = args.config_file
    show_errors = args.errors
    show_warnings = args.warnings
    print_state = args.print_state
    output = args.output

    if config_file:
        parser = Parser()
        try:
            open_file = open(config_file)
            file_string = open_file.read()
            tokens = parser.parse_string(file_string)
            pass
            # ast = AST(tokens)
            # the_state = ast.state
        except exceptions.ParseSyntaxException as oopsie:
            print(oopsie.explain())
            exit(1)
        
        # if show_errors:
        #     errors = ""
        #     for error in the_state.errors:
        #         errors += f"[ERROR] {config_file}, {error}\n"
        #     print(errors) if not output else None
        
        # if show_warnings:
        #     warnings = ""
        #     for warning in the_state.warnings:
        #         warnings += f"[WARN] {config_file}, {warning}\n"
        #     print(warnings) if not output else None
        
        # if print_state:
        #     state = ""
        #     for value in sorted(the_state.value_table):
        #         for state_value in the_state.value_table[value]:
        #             state += f"{str(state_value)}\n"
        #     print(state) if not output else None

        # if output:
            # TODO

        # if the_state.errors != []:
        #     exit(1)

    else:
        print("No config file provided... Exiting")
        exit(0)

if __name__ == "__main__":
    lint_cbn()