import re
from Tokens import *
from pyparsing import (
    Word, alphanums, alphas, nums, Combine,
    Opt, QuotedString, ZeroOrMore, Group,
    OneOrMore, Keyword, Literal, Forward, Optional,
    SkipTo, Dict, LineStart, LineEnd, srange,
    exceptions, Each, lineno, col, line, testing,
    nested_expr, FollowedBy, original_text_for, 
    LineStart, StringEnd, StringStart, trace_parse_action
)

class Grammar:
    def __init__(self):
        #######################################################
        # Define the grammar for Logstash configuration files #
        #######################################################

        ######################
        # Initial defintions #
        ######################
        # Assignment character
        assign = Literal('=>') | Literal('=') | Literal(':')
        assign.set_name("=>")
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
        identifier.set_name("Identifier")
        # Strings surrounded by "" or ''
        string_val = QuotedString('"', escChar='\\') | QuotedString("'", escChar='\\')
        string_val.set_name("string")
        # Boolean value
        boolean = Keyword("true") | Keyword("false")
        boolean.set_name("boolean")
        # Numerical values
        num_val = Word(nums + '.')
        num_val.set_name("number")
        # Values that go on the right side of an expression, 
        # Ex. replace => { "udm_field" => "value" }, "value" is the r_value
        r_value = string_val | num_val | boolean
        # Values that go on the left side of an expression, 
        # Ex. replace => { "udm_field" => "value" }, "udm_field" is the l_value
        l_value = identifier | string_val
        # Strict list definition, used in if/for loop statements, cannot have empty indices
        # Ex. ["1", "2", "3"]
        strict_list = lbracket + r_value + ZeroOrMore(comma + r_value) + rbracket
        strict_list.set_name("strict_list")
        # Lazy list definition, used in filter config options, commas optional and empty indices allowed
        # Ex. ["1" "2", "3", ,]
        lazy_list = lbracket + ZeroOrMore(comma|r_value|identifier) + rbracket
        lazy_list.set_name("lazy_list")
        # Key value pair definition
        # Ex. replace => { "udm_field" => "value" }, '"udm_field" => "value"' is a key_value_pair
        key_value_pair = l_value + assign + r_value + Opt(comma)
        # Hash, a hash is a collection of key value pairs specified in the format "field1" => "value1". Note that multiple key value entries are separated by spaces rather than commas.
        hash_val = lbrace + OneOrMore(key_value_pair) + rbrace
        # Config option, used in filter plugins
        # Ex. on_error => "error"
        config_option = identifier + assign + (string_val|lazy_list|boolean)
        # recursive objects to be defined later on
        statement = Forward()

        ################
        # Grok grammar #
        ################
        # Grok pattern syntax definition
        # Ex. "message" => [ list of grok patterns ]
        grok_key_value_pair = string_val + assign + (lazy_list|string_val) + Opt(comma)
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
        gsub_exression = string_val + comma + string_val + comma + string_val + Opt(comma)
        gsub_keyword = Keyword("gsub")
        gsub = gsub_keyword + assign + lbracket + OneOrMore(gsub_exression) + rbracket
        # Ex. lowercase => [ list of strings ]
        lowercase_keyword = Keyword("lowercase")
        lowercase = lowercase_keyword + assign + lazy_list
        # Ex. uppercase => [ list of strings ]
        uppercase_keyword = Keyword("uppercase")
        uppercase = uppercase_keyword + assign + lazy_list
        # Ex. replace => { key_value_pair }
        replace_keyword = Keyword("replace")
        replace = replace_keyword + assign + hash_val
        # Ex. merge => { key_value_pair }
        merge_keyword = Keyword("merge")
        merge = merge_keyword + assign + hash_val
        # Ex. rename => { key_value_pair }
        rename_keyword = Keyword("rename")
        rename = rename_keyword + assign + hash_val
        # Ex. convert => { key_value_pair }
        convert_keyword = Keyword("convert")
        convert = convert_keyword + assign + hash_val
        # Ex. copy => { key_value_pair }
        copy_keyword = Keyword("copy")
        copy = copy_keyword + assign + hash_val
        # Ex. remove_field => { list of fields }
        remove_field_keyword = Keyword("remove_field")
        remove_field = remove_field_keyword + assign + strict_list
        # Ex. overwrite => { list of fields }
        overwrite_keyword = Keyword("overwrite")
        overwrite = overwrite_keyword + assign + strict_list
        functions = (replace | merge | rename | convert | copy | gsub | lowercase | uppercase | remove_field | overwrite) + ZeroOrMore(config_option)
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
        date = date_keyword + lbrace + date_match + ZeroOrMore(config_option) + rbrace

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
        # binary operators, need a left and right value
        binary_operator = Keyword('not in') ^ Keyword('in') ^ Keyword('=~') ^ Keyword('!~') ^ Keyword('==') ^ Keyword('!=') ^ Keyword('<=') ^ Keyword('>=') ^ Keyword('<') ^ Keyword('>')
        math_operator = Literal('+') ^ Literal('-') ^ Literal('*') ^ Literal('/')
        and_or = Keyword("and") ^ Keyword("or") ^ Keyword('||') ^ Keyword('&&')
        # Unary operators, only need single value
        unary_operator = Literal('!') | Keyword("not")
        unary_operator.set_name("unary operator")
        # Math equation
        math_equation = (if_statement_id | num_val) + math_operator + (num_val | if_statement_id)
        # values can go in an if statement expression
        if_statement_val = string_val | identifier | math_equation | if_statement_id | strict_list | regex_vals
        # Has a left and right val separated by an binary_operator, can be surrounded by parentheses
        binary_expression = if_statement_val + binary_operator + if_statement_val
        # Boolean statement
        # Ex. ![identifier]
        unary_expression = Opt(unary_operator) + if_statement_id
        expression = binary_expression | unary_expression
        statement <<= expression + Optional(and_or + statement)
        statement.ignore(Word('()'))
        # Ex. if [if_statement_comparisons] and/or [if_statement_comparisons] { [body] }
        if_keyword = Keyword("if")
        if_statement = if_keyword + statement + original_text_for(nested_expr('{', '}', ignore_expr=string_val))
        # Ex. else if [if_statement_comparisons] [binary_operator] [if_statement_comparisons] { [body] }
        elif_keyword = Keyword("else if")
        elif_statement = elif_keyword + statement + original_text_for(nested_expr('{', '}', ignore_expr=string_val))
        # Ex. else { [body] }
        else_keyword = Keyword("else")
        else_statement = else_keyword + original_text_for(nested_expr('{', '}', ignore_expr=string_val))

        #########################
        # For statement grammar #
        #########################
        # in keyword
        in_keyword = Keyword("in")
        # Ex. for index, value in [identifier] { [body] }
        for_keyword = Keyword("for")
        for_statement = for_keyword + Opt(identifier + comma) + identifier + in_keyword + (identifier|strict_list) + original_text_for(nested_expr('{', '}', ignore_expr=string_val))

        # filter keyword
        filter_keyword = Keyword("filter")

        #######################################################
        # Chronicle Logstash context-free language definition #
        #######################################################
        # These are valid code blocks to see inside of a nested expression
        blocks = if_statement | elif_statement | else_statement | for_statement | mutate | grok | json | csv | kv | date | drop | copy
        blocks.set_name("code blocks")
        self.one_or_more_blocks = OneOrMore(blocks)
        self.language = StringStart() + filter_keyword + lbrace + self.one_or_more_blocks + rbrace + StringEnd()
        # Ignore commented statements
        self.comment = Literal('#') + ... + LineEnd()
        self.language.ignore(self.comment)

        ##########################
        # Parse action functions #
        ##########################
        @trace_parse_action
        def nested_expr_parse_action(string, position, token):
            parsed_data = token.as_list() + recursive_parse_string(token[-1])
            removed_strings = [entry for entry in parsed_data if type(entry) != str]
            return [removed_strings]

        def recursive_parse_string(string_to_parse):
            as_string = self.one_or_more_blocks
            as_string.ignore(self.comment)
            as_string.set_debug()
            list_to_return = []
            parsed_nested_exp = as_string.parse_string(string_to_parse[1:-1])
            for parsed_data in parsed_nested_exp:
                if type(parsed_data) == str:
                    list_to_return += recursive_parse_string(parsed_data)
                else:
                    list_to_return.append(parsed_data)
            return list_to_return

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
        string_val.set_parse_action(lambda string,position,token: StringToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
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
        binary_operator.set_parse_action(lambda string,position,token: BoolCompareToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        and_or.set_parse_action(lambda string,position,token: BoolOpToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        unary_operator.set_parse_action(lambda string,position,token: BoolNegateToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        if_keyword.set_parse_action(lambda string,position,token: IfToken(position, col(position,string), lineno(position,string)))
        elif_keyword.set_parse_action(lambda string,position,token: ElseIfToken(position, col(position,string), lineno(position,string)))
        else_keyword.set_parse_action(lambda string,position,token: ElseToken(position, col(position,string), lineno(position,string)))
        in_keyword.set_parse_action(lambda string,position,token: InToken(position, col(position,string), lineno(position,string)))
        for_keyword.set_parse_action(lambda string,position,token: ForToken(position, col(position,string), lineno(position,string)))
        filter_keyword.set_parse_action(lambda string,position,token: FilterToken(position, col(position,string), lineno(position,string)))
        if_statement.set_parse_action(nested_expr_parse_action)
        elif_statement.set_parse_action(nested_expr_parse_action)
        else_statement.set_parse_action(nested_expr_parse_action)
        for_statement.set_parse_action(nested_expr_parse_action)
    
    def handle_parsing_error(self, file_string, err):
        patterns = [
            "^Expected nested {} expression, found end of text  \(at char (\d+)\), \(line:(\d+), col:(\d+)\)$",
            "^Expected nested {} expression, found '(.*)'  \(at char (\d+)\), \(line:(\d+), col:(\d+)\)$"
        ]
        for index, pattern in enumerate(patterns):
            match = re.match(pattern, str(err))
            if match and index == 0:
                position = match.group(1)
                line_number = match.group(2)
                col_number = match.group(3)
                print(err.explain())
                print("This is likely due to a mismatched curly brace {}")
                exit(1)
            elif match and index == 1:
                print(err.explain())

    def gen_tokens(self, file_path):
        config = open(file_path)
        file_string = config.read()
        try:
            tokens = self.language.parse_string(file_string)
            return tokens
        except exceptions.ParseException as oopsie:
            print(oopsie.explain())
            # self.handle_parsing_error(file_string, oopsie)
            
parser_language = Grammar()
tokens = parser_language.gen_tokens('/Users/caleb.bryant/Library/CloudStorage/OneDrive-Cyderes/TelEng/github/parser-linting/test/test.conf')
# for token in tokens:
#     print(token)