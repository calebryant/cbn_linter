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
    LineStart, LineEnd, srange, Each, lineno, 
    col, line, StringStart, StringEnd, Suppress
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
        # Lazy list definition, used in filter config options, commas optional and empty indices allowed
        # Ex. ["1" "2", "3", ,]
        list_val = lbracket - ZeroOrMore(Suppress(comma) | string_val | num_val | boolean | identifier) + rbracket
        list_val.set_name("list_val")
        # Values that go on the right side of an expression, 
        # Ex. replace => { "udm_field" => "value" }, "value" is the r_value
        r_value = string_val | num_val | boolean | identifier | list_val
        r_value.set_name("kv_rvalue")
        # Values that go on the left side of an expression, 
        # Ex. replace => { "udm_field" => "value" }, "udm_field" is the l_value
        l_value = identifier | string_val
        l_value.set_name("kv_lvalue")
        # Key value pair definition
        # Ex. replace => { "udm_field" => "value" }, '"udm_field" => "value"' is a key_value_pair
        key_value_pair = l_value + assign + r_value + Suppress(Opt(comma))
        key_value_pair.set_name("key_value_pair")
        key_value_pair.set_results_name("key_value_pair")
        # Hash, a hash is a collection of key value pairs specified in the format "field1" => "value1". Note that multiple key value entries are separated by spaces rather than commas.
        hash_val = lbrace - Group(OneOrMore(key_value_pair)) + rbrace
        hash_val.set_name("hash_val")
        hash_val.set_results_name("hash_val")
        # Config option, used in filter plugins
        # Ex. on_error => "error"
        # config_option = l_value + assign + (identifier|string_val|list_val|boolean) + Opt(comma)
        # config_option.set_name("config_option")
        # recursive objects to be defined later on
        if_statement = Forward()
        if_statement.set_name("if_statement")
        elif_statement = Forward()
        elif_statement.set_name("elif_statement")
        else_statement = Forward()
        else_statement.set_name("else_statement")
        for_statement = Forward()
        for_statement.set_name("for_statement")

        ####################
        # Function grammar #
        ####################
        function_id = Word(alphanums) | (Suppress(Literal("'")) + Word(alphanums) + Suppress(Literal("'"))) | (Suppress(Literal('"')) + Word(alphanums) + Suppress(Literal('"')))
        function = function_id + assign + hash_val

        ##################
        # Plugin grammar #
        ##################
        plugin_id = Word(alphanums) | (Suppress(Literal("'")) + Word(alphanums) + Suppress(Literal("'"))) | (Suppress(Literal('"')) + Word(alphanums) + Suppress(Literal('"')))
        plugin = plugin_id + lbrace - ZeroOrMore(Group(function ^ key_value_pair)) + rbrace

        code_blocks = Group(if_statement|elif_statement|else_statement|for_statement|plugin)

        ################################
        # If/if else statement grammar #
        ################################
        # # bracketed identifier in if statement
        # if_statement_id = OneOrMore(lbracket + identifier + rbracket)
        # if_statement_id.set_name("if_statement_id")
        # # Regex values surrounded by / /
        regex_vals = Combine((Opt('\\') + Literal('/')) + ... + (Opt('\\') + Literal('/')))
        regex_vals.set_name("regex_vals")
        # # Math operators
        # math_operator = Literal('+') | Literal('-') | Literal('*') | Literal('/')
        # math_operator.set_name("math_operator")
        # # Math equation
        # math_equation = if_statement_id + math_operator + (num_val | if_statement_id)
        # math_equation.set_name("math_equation")
        # # values can go in an if statement expression
        # if_statement_val = string_val | identifier | math_equation | if_statement_id | list_val | regex_vals
        # if_statement_val.set_name("if_statement_val")
        # # valid evaluators
        # binary_operator = Keyword('not in') | Keyword('in') | Keyword('=~') | Keyword('!~') | Keyword('==') | Keyword('!=') | Keyword('<=') | Keyword('>=') | Keyword('<') | Keyword('>')
        # binary_operator.set_name("binary_operator")
        # # Boolean operators
        # and_or = Keyword("and") | Keyword("or") | Keyword('||') | Keyword('&&')
        # and_or.set_name("and_or")
        # # Evaluation statement, has a left and right val separated by an binary_operator, can be surrounded by parentheses
        # eval_expression = (if_statement_val + binary_operator + if_statement_val) | (lparen + if_statement_id + binary_operator + if_statement_val + lparen)
        # eval_expression.set_name("eval_expression")
        # # Boolean negate literal
        # unary_operator = Literal('!') | Keyword("not")
        # unary_operator.set_name("unary_operator")
        # # Boolean statement
        # # Ex. ![identifier]
        # bool_expression = (unary_operator + eval_expression) | (Opt(unary_operator) + if_statement_id)
        # bool_expression.set_name("bool_expression")
        # expression = eval_expression | bool_expression
        # expression.set_name("expression")
        statement = SkipTo(lbrace, ignore=string_val|regex_vals)
        statement.set_name("statement")
        # Ex. if [if_statement_comparisons] and/or [if_statement_comparisons] { [body] }
        if_keyword = Keyword("if")
        if_statement <<= if_keyword + statement + lbrace - ZeroOrMore(code_blocks) + rbrace
        # Ex. else if [if_statement_comparisons] [and_or] [if_statement_comparisons] { [body] }
        elif_keyword = Keyword("else if")
        elif_statement <<= elif_keyword - statement + lbrace - ZeroOrMore(code_blocks) + rbrace
        # Ex. else { [body] }
        else_keyword = Keyword("else")
        else_statement <<= else_keyword - lbrace - ZeroOrMore(code_blocks) - rbrace

        #########################
        # For statement grammar #
        #########################
        # in keyword
        in_keyword = Keyword("in")
        # Ex. for index, value in [identifier] { [body] }
        for_keyword = Keyword("for")
        for_statement <<= for_keyword - Opt(identifier + comma) + identifier + in_keyword + (identifier|list_val) + lbrace - ZeroOrMore(code_blocks) + rbrace

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
        plugin_id.set_parse_action(lambda string,position,token: PluginToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        function_id.set_parse_action(lambda string,position,token: FunctionToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # regex_vals.set_parse_action(lambda string,position,token: RegexToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # math_operator.set_parse_action(lambda string,position,token: MathOpToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # binary_operator.set_parse_action(lambda string,position,token: BoolCompareToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # and_or.set_parse_action(lambda string,position,token: BoolOpToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # unary_operator.set_parse_action(lambda string,position,token: BoolNegateToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        if_keyword.set_parse_action(lambda string,position,token: IfToken(position, col(position,string), lineno(position,string)))
        elif_keyword.set_parse_action(lambda string,position,token: ElseIfToken(position, col(position,string), lineno(position,string)))
        statement.set_parse_action(lambda string,position,token: IfStatementToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        else_keyword.set_parse_action(lambda string,position,token: ElseToken(position, col(position,string), lineno(position,string)))
        in_keyword.set_parse_action(lambda string,position,token: InToken(position, col(position,string), lineno(position,string)))
        for_keyword.set_parse_action(lambda string,position,token: ForToken(position, col(position,string), lineno(position,string)))
        filter_keyword.set_parse_action(lambda string,position,token: FilterToken(position, col(position,string), lineno(position,string)))

        #######################################################
        # Chronicle Logstash context-free language definition #
        #######################################################
        self.grammars = StringStart() + filter_keyword + lbrace - OneOrMore(code_blocks) + rbrace + StringEnd()
        # Ignore commented statements
        comment = Literal('#') + ... + LineEnd()
        self.grammars.ignore(comment)

    def parse_file(self, file_name):
        return self.grammars.parse_file(file_name)

    def parse_string(self, string):
        return self.grammars.parse_string(string)
