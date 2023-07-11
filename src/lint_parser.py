# auther: caleb.bryant@cyderes.com
# created: 2023/04/02

import sys, re
from Tokens import *
from pyparsing import (
    Word, alphanums, alphas, nums, Combine, Group,
    Opt, QuotedString, Suppress, ZeroOrMore,
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
assign = Literal('=>') | Literal('=')
assign.set_parse_action(lambda s,loc,token: AssignToken(lineno(loc,s), col(loc,s), token.as_list()[0]))
# Variable names, not quoted
identifier = Word(srange("[@A-Za-z0-9_.\-]"))
# Strings surrounded by "" or ''
quoted_string = QuotedString('"', escChar='\\') | QuotedString("'", escChar='\\')
# Values that go on the right side of an expression, 
# Ex. replace => { "udm_field" => "value" }, "value" is the r_value
r_value = quoted_string | Word(nums + '.') | "true" | "false"
r_value.set_parse_action(lambda s,loc,token: RValToken(lineno(loc,s), col(loc,s), token.as_list()[0]))
# Values that go on the left side of an expression, 
# Ex. replace => { "udm_field" => "value" }, "udm_field" is the l_value
l_value = identifier | quoted_string
l_value.set_parse_action(lambda s,loc,token: LValToken(lineno(loc,s), col(loc,s), token.as_list()[0]))
# Definition of an expression, 
# Ex. replace => { "udm_field" => "value" }, '"udm_field" => "value"' is a key_value_pair
key_value_pair = l_value + assign + r_value + Suppress(Opt(','))
key_value_pair.set_parse_action(lambda s,loc,token: AssignStatementToken(lineno(loc,s), col(loc,s), token.as_list()))
# on_error statements
# Ex. on_error => quoted_string
on_error_keyword = Keyword("on_error")
on_error_keyword.set_parse_action(lambda s,loc,token: LValToken(lineno(loc,s), col(loc,s), "on_error"))
on_error_name = QuotedString('"', escChar='\\') | QuotedString("'", escChar='\\')
on_error_name.set_parse_action(lambda s,loc,token: QuotedValToken(lineno(loc,s), col(loc,s), token.as_list()))
on_error = on_error_keyword + assign + on_error_name
on_error.set_parse_action(lambda s,loc,token: OnErrorToken(lineno(loc,s), col(loc,s), token.as_list()))
# recursive objects to be defined later on
if_statement = Forward()
elif_statement = Forward()
else_statement = Forward()
for_statement = Forward()
statement = Forward()

################
# Grok grammar #
################
# Overwrite statements
# Ex. overwrite => [ list of strings ]
overwrite_keyword = Keyword("overwrite")
overwrite_keyword.set_parse_action(lambda s,loc,token: LValToken(lineno(loc,s), col(loc,s), "overwrite"))
overwrite_list = Suppress('[') + ZeroOrMore(Each(quoted_string|Suppress(','))) + Suppress(']')
overwrite_list.set_parse_action(lambda s,loc,token: ListToken(lineno(loc,s), col(loc,s), token.as_list()))
overwrite = overwrite_keyword + assign + overwrite_list
overwrite.set_parse_action(lambda s,loc,token: OverwriteToken(lineno(loc,s), col(loc,s), token.as_list()))
# Grok pattern syntax definition
# Ex. "message" => [ list of grok patterns ]
grok_key_value_pair = quoted_string + (assign|Suppress(':')) + Suppress(Opt('[')) + OneOrMore(quoted_string + Opt(',')) + Suppress(Opt(']'))
grok_key_value_pair.set_parse_action(lambda s,loc,token: GrokPatternToken(lineno(loc,s), col(loc,s), token.as_list()))
# Match function definition
# Ex. match => { grok key value pairs } overwrite on_error
match = Suppress(Keyword("match")) + assign + Suppress('{') + OneOrMore(grok_key_value_pair) + Suppress('}') + (Opt(overwrite) & Opt(on_error))
# Overall grok filter definition
# Ex. grok { match statement }
grok = Keyword("grok") + Suppress('{') + match + Suppress('}')
grok.set_parse_action(lambda s,loc,token: GrokToken(lineno(loc,s), col(loc,s), token.as_list()))

##################################
# Mutate plugin function grammar #
##################################
# Ex. gsub => [ gsub expressions ]
gsub_exression = quoted_string + Suppress(',') + quoted_string + Suppress(',') + quoted_string + Suppress(Opt(','))
gsub_exression.set_parse_action(lambda s,loc,token: GsubExpressionToken(lineno(loc,s), col(loc,s), token.as_list()))
gsub = Keyword("gsub") + assign + Suppress('[') + OneOrMore(gsub_exression) + Suppress(']')
gsub.set_parse_action(lambda s,loc,token: GsubToken(lineno(loc,s), col(loc,s), token.as_list()))
# Ex. lowercase => [ list of strings ]
lowercase = Keyword("lowercase") + assign + Suppress('[') + OneOrMore(quoted_string + Suppress(Opt(','))) + Suppress(']')
lowercase.set_parse_action(lambda s,loc,token: LowercaseToken(lineno(loc,s), col(loc,s), token.as_list()))
# Ex. uppercase => [ list of strings ]
uppercase = Keyword("uppercase") + assign + Suppress('[') + OneOrMore(quoted_string + Suppress(Opt(','))) + Suppress(']')
uppercase.set_parse_action(lambda s,loc,token: UppercaseToken(lineno(loc,s), col(loc,s), token.as_list()))
# Ex. replace => { [key_value_pair] }
replace = Keyword("replace") + assign + Suppress('{') + OneOrMore(key_value_pair) + Suppress('}')
replace.set_parse_action(lambda s,loc,token: ReplaceToken(lineno(loc,s), col(loc,s), token.as_list()))
# Ex. merge => { [key_value_pair] }
merge = Keyword("merge") + assign + Suppress('{') + OneOrMore(key_value_pair) + Suppress('}')
merge.set_parse_action(lambda s,loc,token: MergeToken(lineno(loc,s), col(loc,s), token.as_list()))
# Ex. rename => { [key_value_pair] }
rename = Keyword("rename") + assign + Suppress('{') + OneOrMore(key_value_pair) + Suppress('}')
rename.set_parse_action(lambda s,loc,token: RenameToken(lineno(loc,s), col(loc,s), token.as_list()))
# Ex. convert => { [key_value_pair] }
convert = Keyword("convert") + assign + Suppress('{') + OneOrMore(key_value_pair) + Suppress('}')
convert.set_parse_action(lambda s,loc,token: ConvertToken(lineno(loc,s), col(loc,s), token.as_list()))
functions = replace | merge | rename | convert | gsub | lowercase | uppercase
# Ex. mutate { [functions] on_error }
mutate = Suppress(Keyword("mutate")) + Suppress('{') + OneOrMore(functions + Opt(on_error)) + Suppress('}')
mutate.set_parse_action(lambda s,loc,token: MutateToken(lineno(loc,s), col(loc,s), token.as_list()))

################
# Json grammar #
################
# Ex. source => "json_message"
options = identifier + Suppress("=>") + r_value
options.set_parse_action(lambda s,loc,token: OptionToken(lineno(loc,s), col(loc,s), token.as_list()))
# Ex. json => { options list }
json = Keyword("json") + Suppress('{') + OneOrMore(on_error|options) + Suppress('}')
json.set_parse_action(lambda s,loc,token: JsonToken(lineno(loc,s), col(loc,s), token.as_list()))

###############
# Csv grammar #
###############
# Ex. csv => { options list }
csv = Keyword("csv") + Suppress('{') + OneOrMore(on_error|options) + Suppress('}')
csv.set_parse_action(lambda s,loc,token: CsvToken(lineno(loc,s), col(loc,s), token.as_list()))

##############
# Kv grammar #
##############
# Ex. kv => { options list }
kv = Keyword("kv") + Suppress('{') + OneOrMore(on_error|options) + Suppress('}')
kv.set_parse_action(lambda s,loc,token: KvToken(lineno(loc,s), col(loc,s), token.as_list()))

################
# Date grammar #
################
# Ex. match => [ list of quoted strings ]
date_match = Keyword("match") + Suppress("=>") + Suppress('[') + OneOrMore(quoted_string + Suppress(Opt(','))) + Suppress("]")
date_match.set_parse_action(lambda s,loc,token: DateMatchToken(lineno(loc,s), col(loc,s), token.as_list()))
# Ex. date { match statement and options }
date = Keyword("date") + Suppress('{') + date_match + OneOrMore(on_error|options) + Suppress('}')
date.set_parse_action(lambda s,loc,token: DateToken(lineno(loc,s), col(loc,s), token.as_list()))

################
# Drop grammar #
################
# Ex. drop { tag => "MALFORMED" }
drop = Keyword("drop") + Suppress('{') + Keyword("tag") + assign + quoted_string + Suppress('}')
drop.set_parse_action(lambda s,loc,token: DropToken(lineno(loc,s), col(loc,s), token.as_list()))

################################
# If/if else statement grammar #
################################
# values that go on the left side of the evaluator in an if or if else statement
if_statement_lval = Combine(OneOrMore('[' + identifier + ']'))
# Regex values surrounded by / /
regex_vals = (Opt('\\') + Literal('/')) + ... + (Opt('\\') + Literal('/'))
# Ex. ["1", "2", "3"]
list_literal = Suppress('[') + r_value + ZeroOrMore(Suppress(',') + r_value) + Suppress(']')
# Math operators
math_operator = Literal('+') | Literal('-') | Literal('*') | Literal('/')
# Math equation
math_equation = if_statement_lval + math_operator + (Word(nums) | if_statement_lval)
# values that go on the right side of the evaluator in an if or if else statement
if_statement_rval = quoted_string | identifier | math_equation | if_statement_lval | list_literal | regex_vals
# valid evaluators
evaluator = Keyword('not in') | Keyword('in') | Keyword('=~') | Keyword('!~') | Keyword('==') | Keyword('!=') | Keyword('<=') | Keyword('>=') | Keyword('<') | Keyword('>')
# Boolean operators
and_or = Keyword("and") | Keyword("or") | Keyword('||') | Keyword('&&')
# Evaluation statement, has a left and right val separated by an evaluator, can be surrounded by parentheses
eval_expression = (if_statement_lval + evaluator + if_statement_rval) | (Suppress('(') + if_statement_lval + evaluator + if_statement_rval + Suppress(')'))
# Boolean statement
# Ex. ![identifier]
bool_expression = Opt(Literal('!') | Keyword("not")) + (if_statement_lval | (Suppress('(') + if_statement_lval + Suppress(')')))
expression = eval_expression | bool_expression
statement <<= (expression + ZeroOrMore(and_or + statement)) | Group(Suppress('(') + expression + ZeroOrMore(and_or + statement) + Suppress(')'))
# Ex. if [if_statement_comparisons] and/or [if_statement_comparisons] { [body] }
if_statement <<= Keyword("if") + statement + Suppress('{') + OneOrMore(if_statement|elif_statement|else_statement|for_statement|mutate|grok|json|csv|kv|date|drop) + Suppress('}')
# Ex. else if [if_statement_comparisons] [and_or] [if_statement_comparisons] { [body] }
elif_statement <<= Keyword("else if") + statement + Suppress('{') + OneOrMore(if_statement|elif_statement|else_statement|for_statement|mutate|grok|json|csv|kv|date|drop) + Suppress('}')
# Ex. else { [body] }
else_statement <<= Keyword("else") + Suppress('{') + OneOrMore(if_statement|elif_statement|else_statement|for_statement|mutate|grok|json|csv|kv|date|drop) + Suppress('}')

#########################
# For statement grammar #
#########################
# Ex. for index, value in [identifier] { [body] }
for_statement <<= Keyword("for") + Opt(identifier + ',') + identifier + Suppress("in") + identifier + Suppress('{') + OneOrMore(if_statement|elif_statement|else_statement|for_statement|mutate|grok|json|csv|kv|date|drop) + Suppress('}')

#######################################################
# Chronicle Logstash context-free language definition #
#######################################################
parser_language = Suppress("filter") + Suppress('{') + OneOrMore(if_statement|elif_statement|else_statement|for_statement|mutate|grok|json|csv|kv|date|drop) + Suppress('}')
# parser_language.set_parse_action(lambda s,l,t: (l,t))
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
            