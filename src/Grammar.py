# Created 2023/07/12
# Author: Caleb Bryant
# Title: Grammar.py
# Description: This file defines a Grammar class that contains the grammar definitions of a Chronicle parser config file.
# References:
    # https://pyparsing-docs.readthedocs.io/en/latest/HowToUsePyparsing.html, 
    # https://www.geeksforgeeks.org/introduction-to-grammar-in-theory-of-computation/


from Tokens import *
from pyparsing import (
    Word, alphanums, alphas, nums, Combine,
    Opt, QuotedString, ZeroOrMore, Group,
    OneOrMore, Keyword, Literal, Forward, SkipTo,
    Dict, LineStart, LineEnd, srange, exceptions,
    Each, lineno, col, line, testing, StringStart,
    StringEnd
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
        assign.set_name('=>')
        # Left brace character
        lbrace = Literal('{')
        lbrace.set_name("{")
        # Right brace character
        rbrace = Literal('}')
        rbrace.set_name("}")
        # Left bracket character
        lbracket = Literal('[')
        lbracket.set_name("[")
        # Right bracket character
        rbracket = Literal(']')
        rbracket.set_name("]")
        # Left parentheses
        lparen = Literal('(')
        lparen.set_name("(")
        # Right parentheses
        rparen = Literal(')')
        rparen.set_name(")")
        # Comma character
        comma = Literal(',')
        comma.set_name(",")
        # Variable names, not quoted
        identifier = Word(srange("[a-zA-Z0-9_.\-@]"))
        identifier.set_name("identifier")
        # Strings surrounded by "" or ''
        string_val = QuotedString('"', escChar='\\') | QuotedString("'", escChar='\\')
        string_val.set_name("string_val")
        # Boolean value
        boolean = Keyword("true") | Keyword("false")
        boolean.set_name("boolean_val")
        # Numerical values
        num_val = Word(nums + '.')
        num_val.set_name("num_val")
        # Values that go on the right side of an expression, 
        # Ex. replace => { "udm_field" => "value" }, "value" is the r_value
        r_value = string_val | num_val | boolean
        r_value.set_name("r_value")
        # Values that go on the left side of an expression, 
        # Ex. replace => { "udm_field" => "value" }, "udm_field" is the l_value
        l_value = identifier | string_val
        l_value.set_name("l_value")
        # Strict list definition, used in if/for loop statements, cannot have empty indices
        # Ex. ["1", "2", "3"]
        strict_list = lbracket - r_value - ZeroOrMore(comma + r_value) - rbracket
        strict_list.set_name("strict_list")
        # Lazy list definition, used in filter config options, commas optional and empty indices allowed
        # Ex. ["1" "2", "3", ,]
        lazy_list = lbracket - ZeroOrMore(comma|r_value|identifier) - rbracket
        lazy_list.set_name("lazy_list")
        # Key value pair definition
        # Ex. replace => { "udm_field" => "value" }, '"udm_field" => "value"' is a key_value_pair
        key_value_pair = l_value - assign - r_value - Opt(comma)
        key_value_pair.set_name("key_value_pair")
        # Hash, a hash is a collection of key value pairs specified in the format "field1" => "value1". Note that multiple key value entries are separated by spaces rather than commas.
        hash_val = lbrace - OneOrMore(key_value_pair) + rbrace
        hash_val.set_name("hash_val")
        # Config option, used in filter plugins
        # Ex. on_error => "error"
        config_option = identifier - assign - (string_val|lazy_list|boolean)
        config_option.set_name("config_option")
        # recursive objects to be defined later on
        if_statement = Forward()
        if_statement.set_name("if_statement")
        elif_statement = Forward()
        elif_statement.set_name("elif_statement")
        else_statement = Forward()
        else_statement.set_name("else_statement")
        for_statement = Forward()
        for_statement.set_name("for_statement")
        statement = Forward()
        statement.set_name("statement")

        ################
        # Grok grammar #
        ################
        # Grok pattern syntax definition
        # Ex. "message" => [ list of grok patterns ]
        grok_key_value_pair = string_val - assign - (lazy_list|string_val) - Opt(comma)
        grok_key_value_pair.set_name("grok_key_value_pair")
        # Match keyword
        match_keyword = Keyword("match")
        match_keyword.set_name("match_keyword")
        # Match function definition
        # Ex. match => { grok key value pairs } overwrite on_error
        match = match_keyword - assign - lbrace - OneOrMore(grok_key_value_pair) - rbrace - ZeroOrMore(config_option)
        match.set_name("match")
        # Grok keyword
        grok_keyword = Keyword("grok")
        grok_keyword.set_name("grok_keyword")
        # Overall grok filter definition
        # Ex. grok { match statement }
        grok = grok_keyword + lbrace + match + rbrace
        grok.set_name("grok")

        ##################################
        # Mutate plugin function grammar #
        ##################################
        # Ex. gsub => [ gsub expressions ]
        gsub_exression = string_val + comma + string_val + comma + string_val + Opt(comma)
        gsub_exression.set_name("gsub_exression")
        gsub_keyword = Keyword("gsub")
        gsub_keyword.set_name("gsub_keyword")
        gsub = gsub_keyword + assign + lbracket - OneOrMore(gsub_exression) + rbracket
        gsub.set_name("gsub")
        # Ex. lowercase => [ list of strings ]
        lowercase_keyword = Keyword("lowercase")
        lowercase_keyword.set_name("lowercase_keyword")
        lowercase = lowercase_keyword + assign + lazy_list
        lowercase.set_name("lowercase")
        # Ex. uppercase => [ list of strings ]
        uppercase_keyword = Keyword("uppercase")
        uppercase_keyword.set_name("uppercase_keyword")
        uppercase = uppercase_keyword + assign + lazy_list
        uppercase.set_name("uppercase")
        # Ex. replace => { [key_value_pair] }
        replace_keyword = Keyword("replace")
        replace_keyword.set_name("replace_keyword")
        replace = replace_keyword + assign + hash_val
        replace.set_name("replace")
        # Ex. merge => { [key_value_pair] }
        merge_keyword = Keyword("merge")
        merge_keyword.set_name("merge_keyword")
        merge = merge_keyword + assign + hash_val
        merge.set_name("merge")
        # Ex. rename => { [key_value_pair] }
        rename_keyword = Keyword("rename")
        rename_keyword.set_name("rename_keyword")
        rename = rename_keyword + assign + hash_val
        rename.set_name("rename")
        # Ex. convert => { [key_value_pair] }
        convert_keyword = Keyword("convert")
        convert_keyword.set_name("convert_keyword")
        convert = convert_keyword + assign + hash_val
        convert.set_name("convert")
        # Ex. copy => { [key_value_pair] }
        copy_keyword = Keyword("copy")
        copy_keyword.set_name("copy_keyword")
        copy = convert_keyword + assign + hash_val
        copy.set_name("copy")
        functions = (replace | merge | rename | convert | copy | gsub | lowercase | uppercase) - ZeroOrMore(config_option)
        functions.set_name("functions")
        # Ex. mutate { [functions] on_error }
        mutate_keyword = Keyword("mutate")
        mutate_keyword.set_name("mutate_keyword")
        mutate = mutate_keyword + lbrace - OneOrMore(functions) + rbrace
        mutate.set_name("mutate")

        #########################
        # CSV, KV, JSON grammar #
        #########################
        # Ex. json => { options list }
        json_keyword = Keyword("json")
        json_keyword.set_name("json_keyword")
        json = json_keyword + lbrace - OneOrMore(config_option) + rbrace
        json.set_name("json")
        # Ex. csv => { options list }
        csv_keyword = Keyword("csv")
        csv_keyword.set_name("csv_keyword")
        csv = csv_keyword + lbrace - OneOrMore(config_option) + rbrace
        csv.set_name("csv")
        # Ex. kv => { options list }
        kv_keyword = Keyword("kv")
        kv_keyword.set_name("kv_keyword")
        kv = kv_keyword + lbrace - OneOrMore(config_option) + rbrace
        kv.set_name("kv")

        ################
        # Date grammar #
        ################
        # Ex. match => [ list of quoted strings ]
        date_match = match_keyword + assign + lazy_list
        date_match.set_name("date_match")
        # Ex. date { match statement and options }
        date_keyword = Keyword("date")
        date_keyword.set_name("date_keyword")
        date = date_keyword + lbrace + date_match - OneOrMore(config_option) + rbrace
        date.set_name("date")

        ################
        # Drop grammar #
        ################
        # Ex. drop { tag => "MALFORMED" }
        drop_keyword = Keyword("drop")
        drop_keyword.set_name("drop_keyword")
        drop = drop_keyword + lbrace + Opt(config_option) + rbrace
        drop.set_name("drop")

        ################################
        # If/if else statement grammar #
        ################################
        # bracketed identifier in if statement
        if_statement_id = OneOrMore(lbracket + identifier + rbracket)
        if_statement_id.set_name("if_statement_id")
        # Regex values surrounded by / /
        regex_vals = Combine((Opt('\\') + Literal('/')) + ... + (Opt('\\') + Literal('/')))
        regex_vals.set_name("regex_vals")
        # Math operators
        math_operator = Literal('+') | Literal('-') | Literal('*') | Literal('/')
        math_operator.set_name("math_operator")
        # Math equation
        math_equation = if_statement_id + math_operator + (num_val | if_statement_id)
        math_equation.set_name("math_equation")
        # values can go in an if statement expression
        if_statement_val = string_val | identifier | math_equation | if_statement_id | strict_list | regex_vals
        if_statement_val.set_name("if_statement_val")
        # valid evaluators
        binary_operator = Keyword('not in') | Keyword('in') | Keyword('=~') | Keyword('!~') | Keyword('==') | Keyword('!=') | Keyword('<=') | Keyword('>=') | Keyword('<') | Keyword('>')
        binary_operator.set_name("binary_operator")
        # Boolean operators
        and_or = Keyword("and") | Keyword("or") | Keyword('||') | Keyword('&&')
        and_or.set_name("and_or")
        # Evaluation statement, has a left and right val separated by an binary_operator, can be surrounded by parentheses
        eval_expression = (if_statement_val + binary_operator + if_statement_val) | (lparen + if_statement_id + binary_operator + if_statement_val + lparen)
        eval_expression.set_name("eval_expression")
        # Boolean negate literal
        unary_operator = Literal('!') | Keyword("not")
        unary_operator.set_name("unary_operator")
        # Boolean statement
        # Ex. ![identifier]
        bool_expression = Opt(unary_operator) + (if_statement_id | (lparen + if_statement_id + rparen))
        bool_expression.set_name("bool_expression")
        expression = eval_expression | bool_expression
        expression.set_name("expression")
        statement <<= (expression + ZeroOrMore(and_or + statement)) | ((lparen + expression + ZeroOrMore(and_or + statement) + rparen) + ZeroOrMore(and_or + statement))
        # Ex. if [if_statement_comparisons] and/or [if_statement_comparisons] { [body] }
        if_keyword = Keyword("if")
        if_keyword.set_name("if_keyword")
        if_statement <<= if_keyword - statement + lbrace - OneOrMore(Group(if_statement|elif_statement|else_statement|for_statement|mutate|grok|json|csv|kv|date|drop|copy)) + rbrace
        # Ex. else if [if_statement_comparisons] [and_or] [if_statement_comparisons] { [body] }
        elif_keyword = Keyword("else if")
        elif_keyword.set_name("elif_keyword")
        elif_statement <<= elif_keyword - statement + lbrace - OneOrMore(Group(if_statement|elif_statement|else_statement|for_statement|mutate|grok|json|csv|kv|date|drop|copy)) + rbrace
        # Ex. else { [body] }
        else_keyword = Keyword("else")
        else_keyword.set_name("else_keyword")
        else_statement <<= else_keyword - lbrace - OneOrMore(Group(if_statement|elif_statement|else_statement|for_statement|mutate|grok|json|csv|kv|date|drop|copy)) - rbrace

        #########################
        # For statement grammar #
        #########################
        # in keyword
        in_keyword = Keyword("in")
        in_keyword.set_name("in_keyword")
        # Ex. for index, value in [identifier] { [body] }
        for_keyword = Keyword("for")
        for_keyword.set_name("for_keyword")
        for_statement <<= for_keyword - Opt(identifier + comma) + identifier + in_keyword + (identifier|strict_list) + lbrace - OneOrMore(Group(if_statement|elif_statement|else_statement|for_statement|mutate|grok|json|csv|kv|date|drop|copy)) + rbrace
        for_statement.set_name("for_statement")

        # filter keyword
        filter_keyword = Keyword("filter")
        filter_keyword.set_name("filter_keyword")

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

        #######################################################
        # Chronicle Logstash context-free language definition #
        #######################################################
        self.grammars = StringStart() + filter_keyword + lbrace - OneOrMore(Group(if_statement|elif_statement|else_statement|for_statement|mutate|grok|json|csv|kv|date|drop)) + rbrace + StringEnd()
        # Ignore commented statements
        comment = Literal('#') + ... + LineEnd()
        self.grammars.ignore(comment)

    def parse_file(self, file_name):
        return self.grammars.parse_file(file_name)

    def parse_string(self, string):
        return self.grammars.parse_string(string)
