# auther: caleb.bryant@cyderes.com
# created: 2023/04/02

import sys, re
from Tokens import *
from pyparsing import (
    Word, alphanums, alphas, nums, Combine, Group,
    Opt, QuotedString, ZeroOrMore,
    OneOrMore, Keyword, Literal, Forward, SkipTo,
    Dict, LineStart, LineEnd, srange, exceptions,
    Each, lineno, col
)

#######################################################
# Define the grammar for Logstash configuration files #
#######################################################

######################
# Initial defintions #
######################
# Assignment character
assign = Literal('=>') | Literal('=') | Literal(':')
# Left brace character
lbrace = Literal('{')
# Right brace character
rbrace = Literal('}')
# Left bracket character
lbracket = Literal('[')
# Right bracket character
rbracket = Literal(']')
# Left parentheses
lparen = Literal('(')
# Right parentheses
rparen = Literal(')')
# Comma character
comma = Literal(',')
# Variable names, not quoted
identifier = Word(srange("[@A-Za-z0-9_.\-]"))
# Strings surrounded by "" or ''
quoted_string = QuotedString('"', escChar='\\') | QuotedString("'", escChar='\\')
# Boolean value
boolean = Keyword("true") | Keyword("false")
# Numerical values
num_val = Word(nums + '.')
# Values that go on the right side of an expression, 
# Ex. replace => { "udm_field" => "value" }, "value" is the r_value
r_value = quoted_string | num_val | boolean
# Values that go on the left side of an expression, 
# Ex. replace => { "udm_field" => "value" }, "udm_field" is the l_value
l_value = identifier | quoted_string
# Strict list definition, used in if/for loop statements, cannot have empty indices
# Ex. ["1", "2", "3"]
strict_list = lbracket + r_value + ZeroOrMore(comma + r_value) + rbracket
# Lazy list definition, used in filter config options, commas optional and empty indices allowed
# Ex. ["1" "2", "3", ,]
lazy_list = lbracket + ZeroOrMore(comma|r_value) + rbracket
# Key value pair definition
# Ex. replace => { "udm_field" => "value" }, '"udm_field" => "value"' is a key_value_pair
key_value_pair = l_value + assign + r_value + Opt(comma)
# Hash, a hash is a collection of key value pairs specified in the format "field1" => "value1". Note that multiple key value entries are separated by spaces rather than commas.
hash_val = lbrace + OneOrMore(key_value_pair) + rbrace
# Config option, used in filter plugins
# Ex. on_error => "error"
config_option = identifier + assign + (quoted_string|lazy_list|boolean)
# recursive objects to be defined later on
if_statement = Forward()
elif_statement = Forward()
else_statement = Forward()
for_statement = Forward()
statement = Forward()

################
# Grok grammar #
################
# Grok pattern syntax definition
# Ex. "message" => [ list of grok patterns ]
grok_key_value_pair = quoted_string + assign + (lazy_list|quoted_string) + Opt(comma)
# Match function definition
# Ex. match => { grok key value pairs } overwrite on_error
match = Keyword("match") + assign + lbrace + OneOrMore(grok_key_value_pair) + rbrace + ZeroOrMore(config_option)
# Overall grok filter definition
# Ex. grok { match statement }
grok = Keyword("grok") + lbrace + match + rbrace

##################################
# Mutate plugin function grammar #
##################################
# Ex. gsub => [ gsub expressions ]
gsub_exression = quoted_string + comma + quoted_string + comma + quoted_string + Opt(comma)
gsub = Keyword("gsub") + assign + lbracket + OneOrMore(gsub_exression) + rbracket
# Ex. lowercase => [ list of strings ]
lowercase = Keyword("lowercase") + assign + lazy_list
# Ex. uppercase => [ list of strings ]
uppercase = Keyword("uppercase") + assign + lazy_list
# Ex. replace => { [key_value_pair] }
replace = Keyword("replace") + assign + hash_val
# Ex. merge => { [key_value_pair] }
merge = Keyword("merge") + assign + hash_val
# Ex. rename => { [key_value_pair] }
rename = Keyword("rename") + assign + hash_val
# Ex. convert => { [key_value_pair] }
convert = Keyword("convert") + assign + hash_val
functions = (replace | merge | rename | convert | gsub | lowercase | uppercase) + ZeroOrMore(config_option)
# Ex. mutate { [functions] on_error }
mutate = Keyword("mutate") + lbrace + OneOrMore(functions) + rbrace

#########################
# CSV, KV, JSON grammar #
#########################
# Ex. json => { options list }
json = Keyword("json") + lbrace + OneOrMore(config_option) + rbrace
# Ex. csv => { options list }
csv = Keyword("csv") + lbrace + OneOrMore(config_option) + rbrace
# Ex. kv => { options list }
kv = Keyword("kv") + lbrace + OneOrMore(config_option) + rbrace

################
# Date grammar #
################
# Ex. match => [ list of quoted strings ]
date_match = Keyword("match") + assign + lazy_list
# Ex. date { match statement and options }
date = Keyword("date") + lbrace + date_match + OneOrMore(config_option) + rbrace

################
# Drop grammar #
################
# Ex. drop { tag => "MALFORMED" }
drop = Keyword("drop") + lbrace + Opt(config_option) + rbrace

################################
# If/if else statement grammar #
################################
# values that go on the left side of the evaluator in an if or if else statement
if_statement_lval = Combine(OneOrMore(lbracket + identifier + rbracket))
# Regex values surrounded by / /
regex_vals = (Opt('\\') + Literal('/')) + ... + (Opt('\\') + Literal('/'))
# Math operators
math_operator = Literal('+') | Literal('-') | Literal('*') | Literal('/')
# Math equation
math_equation = if_statement_lval + math_operator + (Word(nums) | if_statement_lval)
# values that go on the right side of the evaluator in an if or if else statement
if_statement_rval = quoted_string | identifier | math_equation | if_statement_lval | strict_list | regex_vals
# valid evaluators
evaluator = Keyword('not in') | Keyword('in') | Keyword('=~') | Keyword('!~') | Keyword('==') | Keyword('!=') | Keyword('<=') | Keyword('>=') | Keyword('<') | Keyword('>')
# Boolean operators
and_or = Keyword("and") | Keyword("or") | Keyword('||') | Keyword('&&')
# Evaluation statement, has a left and right val separated by an evaluator, can be surrounded by parentheses
eval_expression = (if_statement_lval + evaluator + if_statement_rval) | (lparen + if_statement_lval + evaluator + if_statement_rval + lparen)
# Boolean statement
# Ex. ![identifier]
bool_expression = Opt(Literal('!') | Keyword("not")) + (if_statement_lval | (lparen + if_statement_lval + lparen))
expression = eval_expression | bool_expression
statement <<= (expression + ZeroOrMore(and_or + statement)) | Group(lparen + expression + ZeroOrMore(and_or + statement) + lparen)
# Ex. if [if_statement_comparisons] and/or [if_statement_comparisons] { [body] }
if_statement <<= Keyword("if") + statement + lbrace + OneOrMore(if_statement|elif_statement|else_statement|for_statement|mutate|grok|json|csv|kv|date|drop) + rbrace
# Ex. else if [if_statement_comparisons] [and_or] [if_statement_comparisons] { [body] }
elif_statement <<= Keyword("else if") + statement + lbrace + OneOrMore(if_statement|elif_statement|else_statement|for_statement|mutate|grok|json|csv|kv|date|drop) + rbrace
# Ex. else { [body] }
else_statement <<= Keyword("else") + lbrace + OneOrMore(if_statement|elif_statement|else_statement|for_statement|mutate|grok|json|csv|kv|date|drop) + rbrace

#########################
# For statement grammar #
#########################
# Ex. for index, value in [identifier] { [body] }
for_statement <<= Keyword("for") + Opt(identifier + ',') + identifier + "in" + identifier + lbrace + OneOrMore(if_statement|elif_statement|else_statement|for_statement|mutate|grok|json|csv|kv|date|drop) + rbrace

#######################################################
# Chronicle Logstash context-free language definition #
#######################################################
parser_language = "filter" + lbrace + OneOrMore(if_statement|elif_statement|else_statement|for_statement|mutate|grok|json|csv|kv|date|drop) + rbrace
# Ignore commented statements
comment = Literal('#') + ... + LineEnd()
parser_language.ignore(comment)

# Testing string
test_string = '''
overwrite => ["global_protect"]
'''

# test_parse = overwrite.parseString(test_string)
# print(test_parse)

# Recursive function to find and print the exact position of a parser error to the terminal
def drilldown_parser_error(parser_error_message, verbose=True):
    match = re.search("found '(.*)'  \(at char ([\d]+)\), \(line:([\d]+), col:([\d]+)\)", parser_error_message)
    if verbose:
        print(parser_error_message)
    if match:
        found = match.group(1)
        char = int(match.group(2))
        line = int(match.group(3))
        col = int(match.group(4))
        file_lines = entire_file_lines[line-1:]
        file_content = ''.join(file_lines)
        # print(file_content[:1000]) # uncomment to view file partitions used in recursive calls
        try:
            if found == 'else':
                elif_match = re.search('else if', file_lines[0])
                if elif_match:
                    elif_statement.ignore(comment)
                    data = elif_statement.parseString(file_content)
                else:
                    else_statement.ignore(comment)
                    data = else_statement.parseString(file_content)
            elif found == 'if':
                if_statement.ignore(comment)
                data = if_statement.parseString(file_content)
            elif found == 'for':
                for_statement.ignore(comment)
                data = for_statement.parseString(file_content)
            elif found == 'mutate':
                mutate.ignore(comment)
                data = mutate.parseString(file_content)
            elif found == 'gsub':
                gsub.ignore(comment)
                data = gsub.parseString(file_content)
            elif found == 'replace':
                replace.ignore(comment)
                data = replace.parseString(file_content)
            elif found == 'merge':
                merge.ignore(comment)
                data = merge.parseString(file_content)
            elif found == 'rename':
                rename.ignore(comment)
                data = rename.parseString(file_content)
            elif found == 'convert':
                convert.ignore(comment)
                data = convert.parseString(file_content)
            elif found == 'uppercase':
                uppercase.ignore(comment)
                data = uppercase.parseString(file_content)
            elif found == 'lowercase':
                lowercase.ignore(comment)
                data = lowercase.parseString(file_content)
            elif found == 'grok':
                grok.ignore(comment)
                data = grok.parseString(file_content)
            elif found == 'match':
                match.ignore(comment)
                data = match.parseString(file_content)
            elif found == 'overwrite':
                overwrite.ignore(comment)
                data = overwrite.parseString(file_content)
            elif found == 'date':
                date.ignore(comment)
                data = date.parseString(file_content)
            elif found == 'date_match':
                date_match.ignore(comment)
                data = date_match.parseString(file_content)
            elif found == 'csv':
                csv.ignore(comment)
                data = csv.parseString(file_content)
            elif found == 'json':
                json.ignore(comment)
                data = json.parseString(file_content)
            elif found == 'kv':
                kv.ignore(comment)
                data = kv.parseString(file_content)
            elif found == 'drop':
                drop.ignore(comment)
                data = drop.parseString(file_content)
            else:
                return parser_error_message
            return parser_error_message
        except exceptions.ParseException as oopsie:
            new_error_message = str(oopsie)
            # check the error message for a line number
            new_match = re.search("\(at char ([\d]+)\), \(line:([\d]+)", new_error_message)
            # if there's a match, continue to recurse
            if new_match:
                new_char = int(new_match.group(1))
                new_line = int(new_match.group(2))
                char_num = char+new_char
                line_num = line+new_line-1
                new_error_message = re.sub("\(line:([\d]+)", f"(line:{line_num}", new_error_message)
                new_error_message = re.sub("\(at char ([\d]+)\)", f"(at char {char_num})", new_error_message)
                return drilldown_parser_error(new_error_message)

# Parse the Logstash configuration using the defined grammar
try:
    entire_file_lines = open(sys.argv[1]).readlines()
    parsed_data = parser_language.parseFile(sys.argv[1])
    # parsed_data = parser_language.parseString(logstash_config)
    print(parsed_data)
except exceptions.ParseException as oopsie:
    drilldown_parser_error(str(oopsie))
            