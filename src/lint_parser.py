# auther: caleb.bryant@cyderes.com
# created: 2023/04/02

import sys, argparse
from Grammar import parserGrammar, drilldown_parser_error

# Testing string
test_string = '''
overwrite => ["global_protect"]
'''

# test_parse = overwrite.parseString(test_string)
# print(test_parse)

# Parse the Logstash configuration using the defined grammar
try:
    entire_file_lines = open(sys.argv[1]).readlines()
    parser_language = parserGrammar()
    parsed_data = parser_language.parseFile(sys.argv[1])
    print(parsed_data)
except exceptions.ParseException as oopsie:
    drilldown_parser_error(str(oopsie))
            