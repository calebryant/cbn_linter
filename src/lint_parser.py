# auther: caleb.bryant@cyderes.com
# created: 2023/04/02

import sys, re
from Tokens import *
from pyparsing import (
    Word, alphanums, alphas, nums, Combine,
    Opt, QuotedString, ZeroOrMore, Group,
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
# Match keyword
match_keyword = Keyword("match")
# Match function definition
# Ex. match => { grok key value pairs } overwrite on_error
match = match_keyword + assign + lbrace + OneOrMore(grok_key_value_pair) + rbrace + ZeroOrMore(config_option)
# Grok keyword
grok_keyword = Keyword("grok")
# Overall grok filter definition
# Ex. grok { match statement }
grok = grok_keyword + lbrace + match + rbrace

##################################
# Mutate plugin function grammar #
##################################
# Ex. gsub => [ gsub expressions ]
gsub_exression = quoted_string + comma + quoted_string + comma + quoted_string + Opt(comma)
gsub_keyword = Keyword("gsub")
gsub = gsub_keyword + assign + lbracket + OneOrMore(gsub_exression) + rbracket
# Ex. lowercase => [ list of strings ]
lowercase_keyword = Keyword("lowercase")
lowercase = lowercase_keyword + assign + lazy_list
# Ex. uppercase => [ list of strings ]
uppercase_keyword = Keyword("uppercase")
uppercase = uppercase_keyword + assign + lazy_list
# Ex. replace => { [key_value_pair] }
replace_keyword = Keyword("replace")
replace = replace_keyword + assign + hash_val
# Ex. merge => { [key_value_pair] }
merge_keyword = Keyword("merge")
merge = merge_keyword + assign + hash_val
# Ex. rename => { [key_value_pair] }
rename_keyword = Keyword("rename")
rename = rename_keyword + assign + hash_val
# Ex. convert => { [key_value_pair] }
convert_keyword = Keyword("convert")
convert = convert_keyword + assign + hash_val
functions = (replace | merge | rename | convert | gsub | lowercase | uppercase) + ZeroOrMore(config_option)
# Ex. mutate { [functions] on_error }
mutate_keyword = Keyword("mutate")
mutate = mutate_keyword + lbrace + OneOrMore(functions) + rbrace

#########################
# CSV, KV, JSON grammar #
#########################
# Ex. json => { options list }
json_keyword = Keyword("json")
json = json_keyword + lbrace + OneOrMore(config_option) + rbrace
# Ex. csv => { options list }
csv_keyword = Keyword("csv")
csv = csv_keyword + lbrace + OneOrMore(config_option) + rbrace
# Ex. kv => { options list }
kv_keyword = Keyword("kv")
kv = kv_keyword + lbrace + OneOrMore(config_option) + rbrace

################
# Date grammar #
################
# Ex. match => [ list of quoted strings ]
date_match = match_keyword + assign + lazy_list
# Ex. date { match statement and options }
date_keyword = Keyword("date")
date = date_keyword + lbrace + date_match + OneOrMore(config_option) + rbrace

################
# Drop grammar #
################
# Ex. drop { tag => "MALFORMED" }
drop_keyword = Keyword("drop")
drop = drop_keyword + lbrace + Opt(config_option) + rbrace

################################
# If/if else statement grammar #
################################
# values that go on the left side of the evaluator in an if or if else statement
if_statement_lval = OneOrMore(lbracket + identifier + rbracket)
# Regex values surrounded by / /
regex_vals = Combine((Opt('\\') + Literal('/')) + ... + (Opt('\\') + Literal('/')))
# Math operators
math_operator = Literal('+') | Literal('-') | Literal('*') | Literal('/')
# Math equation
math_equation = if_statement_lval + math_operator + (num_val | if_statement_lval)
# values that go on the right side of the evaluator in an if or if else statement
if_statement_rval = quoted_string | identifier | math_equation | if_statement_lval | strict_list | regex_vals
# valid evaluators
evaluator = Keyword('not in') | Keyword('in') | Keyword('=~') | Keyword('!~') | Keyword('==') | Keyword('!=') | Keyword('<=') | Keyword('>=') | Keyword('<') | Keyword('>')
# Boolean operators
and_or = Keyword("and") | Keyword("or") | Keyword('||') | Keyword('&&')
# Evaluation statement, has a left and right val separated by an evaluator, can be surrounded by parentheses
eval_expression = (if_statement_lval + evaluator + if_statement_rval) | (lparen + if_statement_lval + evaluator + if_statement_rval + lparen)
# Boolean negate literal
bool_neg = Literal('!') | Keyword("not")
# Boolean statement
# Ex. ![identifier]
bool_expression = Opt(bool_neg) + (if_statement_lval | (lparen + if_statement_lval + rparen))
expression = eval_expression | bool_expression
statement <<= (expression + ZeroOrMore(and_or + statement)) | lparen + expression + ZeroOrMore(and_or + statement) + rparen
# Ex. if [if_statement_comparisons] and/or [if_statement_comparisons] { [body] }
if_keyword = Keyword("if")
if_statement <<= if_keyword + statement + lbrace + OneOrMore(if_statement|elif_statement|else_statement|for_statement|mutate|grok|json|csv|kv|date|drop) + rbrace
# Ex. else if [if_statement_comparisons] [and_or] [if_statement_comparisons] { [body] }
elif_keyword = Keyword("else if")
elif_statement <<= elif_keyword + statement + lbrace + OneOrMore(if_statement|elif_statement|else_statement|for_statement|mutate|grok|json|csv|kv|date|drop) + rbrace
# Ex. else { [body] }
else_keyword = Keyword("else")
else_statement <<= else_keyword + lbrace + OneOrMore(if_statement|elif_statement|else_statement|for_statement|mutate|grok|json|csv|kv|date|drop) + rbrace

#########################
# For statement grammar #
#########################
# in keyword
in_keyword = Keyword("in")
# Ex. for index, value in [identifier] { [body] }
for_keyword = Keyword("for")
for_statement <<= for_keyword + Opt(identifier + comma) + identifier + in_keyword + identifier + lbrace + OneOrMore(if_statement|elif_statement|else_statement|for_statement|mutate|grok|json|csv|kv|date|drop) + rbrace

# filter keyword
filter_keyword = Keyword("filter")

#####################
# Set parse actions #
#####################
# Creates a token for each match
assign.set_parse_action(lambda string,position,token: AssignToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
lbrace.set_parse_action(lambda string,position,token: LBraceToken(position, col(position,string), lineno(position,string)))
rbrace.set_parse_action(lambda string,position,token: RBraceToken(position, col(position,string), lineno(position,string)))
lbracket.set_parse_action(lambda string,position,token: LBracketToken(position, col(position,string), lineno(position,string)))
rbracket.set_parse_action(lambda string,position,token: RBracketToken(position, col(position,string), lineno(position,string)))
lparen.set_parse_action(lambda string,position,token: LParenToken(position, col(position,string), lineno(position,string)))
rparen.set_parse_action(lambda string,position,token: RParenToken(position, col(position,string), lineno(position,string)))
comma.set_parse_action(lambda string,position,token: CommaToken(position, col(position,string), lineno(position,string)))
identifier.set_parse_action(lambda string,position,token: IDToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
quoted_string.set_parse_action(lambda string,position,token: StringToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
boolean.set_parse_action(lambda string,position,token: BoolToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
num_val.set_parse_action(lambda string,position,token: NumberToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
match_keyword.set_parse_action(lambda string,position,token: GrokMatchToken(position, col(position,string), lineno(position,string)))
grok_keyword.set_parse_action(lambda string,position,token: GrokMatchToken(position, col(position,string), lineno(position,string)))
gsub_keyword.set_parse_action(lambda string,position,token: GsubToken(position, col(position,string), lineno(position,string)))
lowercase_keyword.set_parse_action(lambda string,position,token: LowercaseToken(position, col(position,string), lineno(position,string)))
uppercase_keyword.set_parse_action(lambda string,position,token: UppercaseToken(position, col(position,string), lineno(position,string)))
replace_keyword.set_parse_action(lambda string,position,token: ReplaceToken(position, col(position,string), lineno(position,string)))
merge_keyword.set_parse_action(lambda string,position,token: MergeToken(position, col(position,string), lineno(position,string)))
rename_keyword.set_parse_action(lambda string,position,token: RenameToken(position, col(position,string), lineno(position,string)))
convert_keyword.set_parse_action(lambda string,position,token: ConvertToken(position, col(position,string), lineno(position,string)))
mutate_keyword.set_parse_action(lambda string,position,token: MutateToken(position, col(position,string), lineno(position,string)))
json_keyword.set_parse_action(lambda string,position,token: JsonToken(position, col(position,string), lineno(position,string)))
csv_keyword.set_parse_action(lambda string,position,token: CsvToken(position, col(position,string), lineno(position,string)))
kv_keyword.set_parse_action(lambda string,position,token: KvToken(position, col(position,string), lineno(position,string)))
date_keyword.set_parse_action(lambda string,position,token: DateToken(position, col(position,string), lineno(position,string)))
drop_keyword.set_parse_action(lambda string,position,token: DropToken(position, col(position,string), lineno(position,string)))
regex_vals.set_parse_action(lambda string,position,token: RegexToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
math_operator.set_parse_action(lambda string,position,token: MathOpToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
evaluator.set_parse_action(lambda string,position,token: BoolCompareToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
and_or.set_parse_action(lambda string,position,token: BoolOpToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
bool_neg.set_parse_action(lambda string,position,token: BoolNegateToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
if_keyword.set_parse_action(lambda string,position,token: IfToken(position, col(position,string), lineno(position,string)))
elif_keyword.set_parse_action(lambda string,position,token: ElseIfToken(position, col(position,string), lineno(position,string)))
else_keyword.set_parse_action(lambda string,position,token: ElseToken(position, col(position,string), lineno(position,string)))
in_keyword.set_parse_action(lambda string,position,token: InToken(position, col(position,string), lineno(position,string)))
for_keyword.set_parse_action(lambda string,position,token: ForToken(position, col(position,string), lineno(position,string)))
filter_keyword.set_parse_action(lambda string,position,token: FilterToken(position, col(position,string), lineno(position,string)))

#######################################################
# Chronicle Logstash context-free language definition #
#######################################################
parser_language = filter_keyword + lbrace + OneOrMore(if_statement|elif_statement|else_statement|for_statement|mutate|grok|json|csv|kv|date|drop) + rbrace
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
    for token in parsed_data:
        if not issubclass(type(token), Token):
            print(token)
except exceptions.ParseException as oopsie:
    drilldown_parser_error(str(oopsie))
            