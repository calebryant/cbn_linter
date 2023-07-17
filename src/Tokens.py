import re
from pyparsing import (
    Word, alphanums, alphas, nums, Combine,
    Opt, QuotedString, ZeroOrMore, Group,
    OneOrMore, Keyword, Literal, Forward, SkipTo,
    Dict, LineStart, LineEnd, srange, exceptions,
    Each, lineno, col, line, testing
)

class Token:
	def __init__(self, position, column, row):
		self.pos = position
		self.col = column
		self.row = row

class LBraceToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = '{'

class RBraceToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = '}'

class LBracketToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = '['

class RBracketToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = ']'

class LParenToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = '('

class RParenToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = ')'

class CommaToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = ','

class AssignToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = token_value

class IDToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = token_value

class StringToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = token_value

class BoolToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = token_value

class NumberToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = token_value

class GrokMatchToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = "match"

class GrokToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = "grok"

class GsubToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = "gsub"

class LowercaseToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = "lowercase"

class UppercaseToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = "uppercase"

class ReplaceToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = "replace"

class MergeToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = "Merge"

class RenameToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = "rename"

class ConvertToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = "convert"

class CopyToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = "copy"

class MutateToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = "mutate"

class JsonToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = "json"

class CsvToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = "csv"

class KvToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = "kv"

class DateMatchToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = "match"

class DateToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = "date"

class DropToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = "drop"

class RegexToken(Token):
	def __init__(self, position, column, row, value):
		super().__init__(position, column, row)
		self.value = value

class MathOpToken(Token):
	def __init__(self, position, column, row, value):
		super().__init__(position, column, row)
		self.value = value

class BoolCompareToken(Token):
	def __init__(self, position, column, row, value):
		super().__init__(position, column, row)
		self.value = value

class BoolOpToken(Token):
	def __init__(self, position, column, row, value):
		super().__init__(position, column, row)
		self.value = value

class BoolNegateToken(Token):
	def __init__(self, position, column, row, value):
		super().__init__(position, column, row)
		self.value = value

class IfToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = "if"

class ElseIfToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = "else if"

class ElseToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = "else"

class InToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = "in"

class ForToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = "for"

class FilterToken(Token):
	def __init__(self, position, column, row):
		super().__init__(position, column, row)
		self.value = "filter"

def createTokens(config_file):
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
    identifier = Word(srange("[a-zA-Z0-9_.\-@]"))
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
    lazy_list = lbracket + ZeroOrMore(comma|r_value|identifier) + rbracket
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
    if_else_chain = Forward()
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
    # Ex. copy => { [key_value_pair] }
    copy_keyword = Keyword("copy")
    copy = convert_keyword + assign + hash_val
    functions = (replace | merge | rename | convert | copy | gsub | lowercase | uppercase) + ZeroOrMore(config_option)
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
    # bracketed identifier in if statement
    if_statement_id = OneOrMore(lbracket + identifier + rbracket)
    # Regex values surrounded by / /
    regex_vals = Combine((Opt('\\') + Literal('/')) + ... + (Opt('\\') + Literal('/')))
    # Math operators
    math_operator = Literal('+') | Literal('-') | Literal('*') | Literal('/')
    # Math equation
    math_equation = if_statement_id + math_operator + (num_val | if_statement_id)
    # values can go in an if statement expression
    if_statement_val = quoted_string | identifier | math_equation | if_statement_id | strict_list | regex_vals
    # valid evaluators
    evaluator = Keyword('not in') | Keyword('in') | Keyword('=~') | Keyword('!~') | Keyword('==') | Keyword('!=') | Keyword('<=') | Keyword('>=') | Keyword('<') | Keyword('>')
    # Boolean operators
    and_or = Keyword("and") | Keyword("or") | Keyword('||') | Keyword('&&')
    # Evaluation statement, has a left and right val separated by an evaluator, can be surrounded by parentheses
    eval_expression = (if_statement_val + evaluator + if_statement_val) | (lparen + if_statement_id + evaluator + if_statement_val + lparen)
    # Boolean negate literal
    bool_neg = Literal('!') | Keyword("not")
    # Boolean statement
    # Ex. ![identifier]
    bool_expression = Opt(bool_neg) + (if_statement_id | (lparen + if_statement_id + rparen))
    expression = eval_expression | bool_expression
    statement <<= (expression + ZeroOrMore(and_or + statement)) | ((lparen + expression + ZeroOrMore(and_or + statement) + rparen) + ZeroOrMore(and_or + statement))
    # Ex. if [if_statement_comparisons] and/or [if_statement_comparisons] { [body] }
    if_keyword = Keyword("if")
    if_statement <<= if_keyword + statement + lbrace + OneOrMore(if_else_chain|for_statement|mutate|grok|json|csv|kv|date|drop|copy) + rbrace
    # Ex. else if [if_statement_comparisons] [and_or] [if_statement_comparisons] { [body] }
    elif_keyword = Keyword("else if")
    elif_statement <<= elif_keyword + statement + lbrace + OneOrMore(if_else_chain|for_statement|mutate|grok|json|csv|kv|date|drop|copy) + rbrace
    # Ex. else { [body] }
    else_keyword = Keyword("else")
    else_statement <<= else_keyword + lbrace + OneOrMore(if_else_chain|for_statement|mutate|grok|json|csv|kv|date|drop|copy) + rbrace
    if_else_chain <<= if_statement + ZeroOrMore(elif_statement) + Opt(else_statement)

    #########################
    # For statement grammar #
    #########################
    # in keyword
    in_keyword = Keyword("in")
    # Ex. for index, value in [identifier] { [body] }
    for_keyword = Keyword("for")
    for_statement <<= for_keyword + Opt(identifier + comma) + identifier + in_keyword + identifier + lbrace + OneOrMore(if_else_chain|for_statement|mutate|grok|json|csv|kv|date|drop|copy) + rbrace

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
    copy_keyword.set_parse_action(lambda string,position,token: ConvertToken(position, col(position,string), lineno(position,string)))
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
    parser_language = filter_keyword + lbrace + OneOrMore(if_else_chain|for_statement|mutate|grok|json|csv|kv|date|drop|copy) + rbrace
    # Ignore commented statements
    comment = Literal('#') + ... + LineEnd()
    parser_language.ignore(comment)

    # Recursive function to find and print the exact position of a parser error to the terminal
    # Breaks the string down into smaller bits and attempts to re-parse
    def drilldown_parser_error(position, message):
        match = re.search("found '(.+)'", message)
        if match:
            found = match.group(1)
            try:
                if found == 'else':
                    elif_match = re.search('else if', file_string[position:])
                    if elif_match:
                        elif_statement.ignore(comment)
                        data = elif_statement.parseString(file_string[position:])
                    else:
                        else_statement.ignore(comment)
                        data = else_statement.parseString(file_string[position:])
                elif found == 'if':
                    if_statement.ignore(comment)
                    data = if_statement.parseString(file_string[position:])
                elif found == 'for':
                    for_statement.ignore(comment)
                    data = for_statement.parseString(file_string[position:])
                elif found == 'mutate':
                    mutate.ignore(comment)
                    data = mutate.parseString(file_string[position:])
                elif found == 'gsub':
                    gsub.ignore(comment)
                    data = gsub.parseString(file_string[position:])
                elif found == 'replace':
                    replace.ignore(comment)
                    data = replace.parseString(file_string[position:])
                elif found == 'merge':
                    merge.ignore(comment)
                    data = merge.parseString(file_string[position:])
                elif found == 'rename':
                    rename.ignore(comment)
                    data = rename.parseString(file_string[position:])
                elif found == 'convert':
                    convert.ignore(comment)
                    data = convert.parseString(file_string[position:])
                elif found == 'uppercase':
                    uppercase.ignore(comment)
                    data = uppercase.parseString(file_string[position:])
                elif found == 'lowercase':
                    lowercase.ignore(comment)
                    data = lowercase.parseString(file_string[position:])
                elif found == 'copy':
                    copy.ignore(comment)
                    data = copy.parseString(file_string[position:])
                elif found == 'grok':
                    grok.ignore(comment)
                    data = grok.parseString(file_string[position:])
                elif found == 'match':
                    match.ignore(comment)
                    data = match.parseString(file_string[position:])
                elif found == 'overwrite':
                    overwrite.ignore(comment)
                    data = overwrite.parseString(file_string[position:])
                elif found == 'date':
                    date.ignore(comment)
                    data = date.parseString(file_string[position:])
                elif found == 'date_match':
                    date_match.ignore(comment)
                    data = date_match.parseString(file_string[position:])
                elif found == 'csv':
                    csv.ignore(comment)
                    data = csv.parseString(file_string[position:])
                elif found == 'json':
                    json.ignore(comment)
                    data = json.parseString(file_string[position:])
                elif found == 'kv':
                    kv.ignore(comment)
                    data = kv.parseString(file_string[position:])
                elif found == 'drop':
                    drop.ignore(comment)
                    data = drop.parseString(file_string[position:])
                else:
                    return (position, message)
                return (position, message)
            except exceptions.ParseException as oopsie:
                new_location = position + oopsie.loc
                return drilldown_parser_error(new_location, str(oopsie))
    try:
        return parser_language.parseFile(config_file)
    except exceptions.ParseException as oopsie:
        file_string = open(config_file).read()
        error = drilldown_parser_error(oopsie.loc, str(oopsie))
        pos, msg = error
        msg = re.sub('char [\d]+', f'char {pos}', msg)
        msg = re.sub('line:[\d]+', f'line:{lineno(pos, file_string)}', msg)
        msg = re.sub('column:[\d]+', f'col:{col(pos, file_string)}', msg)
        msg = re.sub('^,', 'Expected unknown,', msg)
        print(line(pos, file_string))
        print(" " * (col(pos, file_string) - 1) + "^")
        print(msg)

