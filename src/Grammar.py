# Created 2023/07/12
# Author: Caleb Bryant
# Title: Grammar.py
# Description: This file defines a Grammar class that contains the grammar definitions of a Chronicle parser config file.
# References:
    # https://pyparsing-docs.readthedocs.io/en/latest/HowToUsePyparsing.html, 
    # https://www.geeksforgeeks.org/introduction-to-grammar-in-theory-of-computation/


from Tokens import *
from AST import *
from pyparsing import (
    Word, alphanums, alphas, nums, Combine,
    Opt, QuotedString, ZeroOrMore, Group,
    OneOrMore, Keyword, Literal, Forward, SkipTo,
    LineStart, LineEnd, srange, Each, lineno, 
    col, line, StringStart, StringEnd, Suppress,
    Optional
)

class Grammar:
    def __init__(self):
        #######################################################
        # Define the grammar for Logstash configuration files #
        #######################################################

        ####################
        # Token defintions #
        ####################
        # Punctuation tokens
        # Arrow charater
        arrow_token = Literal('=>') | Literal('=') | Literal(':')
        arrow_token.set_name('=>')
        arrow_token.set_parse_action(lambda string,position,token: ArrowToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # Left brace character
        lbrace_token = Literal('{')
        lbrace_token.set_name('{')
        lbrace_token.set_parse_action(lambda string,position,token: LBraceToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # Right brace character
        rbrace_token = Literal('}')
        rbrace_token.set_name('}')
        rbrace_token.set_parse_action(lambda string,position,token: RBraceToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # Left bracket character
        lbracket_token = Literal('[')
        lbracket_token.set_name('[')
        lbracket_token.set_parse_action(lambda string,position,token: LBracketToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # Right bracket character
        rbracket_token = Literal(']')
        rbracket_token.set_name(']')
        rbracket_token.set_parse_action(lambda string,position,token: RBracketToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # Left parentheses
        lparen_token = Literal('(')
        lparen_token.set_name('(')
        lparen_token.set_parse_action(lambda string,position,token: LParenToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # Right parentheses
        rparen_token = Literal(')')
        rparen_token.set_name(')')
        rparen_token.set_parse_action(lambda string,position,token: RParenToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # Comma character
        comma_token = Literal(',')
        comma_token.set_name(',')
        comma_token.set_parse_action(lambda string,position,token: CommaToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        comment_token = Literal('#') + ... + LineEnd()

        # Keyword tokens
        # filter keyword token
        filter_token = Keyword("filter")
        filter_token.set_name("filter")
        filter_token.set_parse_action(lambda string,position,token: FilterToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # Function keyword tokens
        function_token = Keyword("grok") | Keyword("json") | Keyword("xml") | Keyword("kv") | Keyword("csv") | Keyword("mutate") | Keyword("base64") | Keyword("date") | Keyword("drop") | Keyword("statedump")
        function_token.set_name("function keyword")
        function_token.set_parse_action(lambda string,position,token: FunctionToken(position, col(position,string), lineno(position,string), token.as_list()[0]))

        # Function config tokens
        function_config_token = Keyword("match") | Keyword("overwrite") | Keyword("on_error") | Keyword("source") | Keyword("target") | Keyword("array_function") | Keyword("xpath") | Keyword("field_split") | Keyword("unescape_field_split") | Keyword("value_split") | Keyword("unescape_value_split") | Keyword("whitespace") | Keyword("trim_key") | Keyword("trim_value") | Keyword("separator") | Keyword("unescape_separator") | Keyword("convert") | Keyword("gsub") | Keyword("lowercase") | Keyword("merge") | Keyword("rename") | Keyword("replace") | Keyword("uppercase") | Keyword("remove_field") | Keyword("copy") | Keyword("split") | Keyword("encoding") | Keyword("timezone") | Keyword("rebase") | Keyword("tag") | Keyword("label")
        function_config_token.set_name("function config option")
        function_config_token.set_parse_action(lambda string,position,token: FunctionConfigToken(position, col(position,string), lineno(position,string), token.as_list()[0]))

        # Conditional statement tokens
        # if keyword token
        if_token = Keyword("if")
        if_token.set_name("if")
        if_token.set_parse_action(lambda string,position,token: IfToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # else if keyword token
        elseif_token = Keyword("else if")
        elseif_token.set_name("else if")
        elseif_token.set_parse_action(lambda string,position,token: ElseIfToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # else keyword token
        else_token = Keyword("else")
        else_token.set_name("else")
        else_token.set_parse_action(lambda string,position,token: ElseToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # Boolean evaluator tokens
        eq_token = Literal("==")
        eq_token.set_name("==")
        eq_token.set_parse_action(lambda string,position,token: BoolCompareToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        ne_token = Literal("!=")
        ne_token.set_name("!=")
        ne_token.set_parse_action(lambda string,position,token: BoolCompareToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        lt_token = Literal("<")
        lt_token.set_name("<")
        lt_token.set_parse_action(lambda string,position,token: BoolCompareToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        gt_token = Literal(">")
        gt_token.set_name(">")
        gt_token.set_parse_action(lambda string,position,token: BoolCompareToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        lte_token = Literal("<=")
        lte_token.set_name("<=")
        lte_token.set_parse_action(lambda string,position,token: BoolCompareToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        gte_token = Literal(">=")
        gte_token.set_name(">=")
        gte_token.set_parse_action(lambda string,position,token: BoolCompareToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        match_token = Literal("=~")
        match_token.set_name("=~")
        match_token.set_parse_action(lambda string,position,token: BoolCompareToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        no_match_token = Literal("!~")
        no_match_token.set_name("!~")
        no_match_token.set_parse_action(lambda string,position,token: BoolCompareToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # Boolean operator tokens
        and_token = Literal("&&") | Keyword("and")
        and_token.set_name("and")
        and_token.set_parse_action(lambda string,position,token: BoolOpToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        or_token = Literal("||") | Keyword("or")
        or_token.set_name("or")
        or_token.set_parse_action(lambda string,position,token: BoolOpToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        not_token = Literal("!") | Keyword("not")
        not_token.set_name("not")
        not_token.set_parse_action(lambda string,position,token: BoolOpToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # Math operator tokens
        subtraction_token = Literal("-")
        subtraction_token.set_name("-")
        subtraction_token.set_parse_action(lambda string,position,token: MathOpToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        addition_token = Literal("+")
        addition_token.set_name("+")
        addition_token.set_parse_action(lambda string,position,token: MathOpToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        division_token = Literal("/")
        division_token.set_name("/")
        division_token.set_parse_action(lambda string,position,token: MathOpToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        multiplication_token = Literal("*")
        multiplication_token.set_name("*")
        multiplication_token.set_parse_action(lambda string,position,token: MathOpToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # If statement token, values that can appear inside brakets in if statement tokens ex. [message][value] has 2 tokens, message and value
        if_token_token = Word(srange("[a-zA-Z0-9_.\-@]"))
        if_token_token.set_name("bracketed token")
        if_token_token.set_parse_action(lambda string,position,token: TokenToken(position, col(position,string), lineno(position,string), token.as_list()[0]))

        # Loop statement tokens
        # for keyword token
        for_token = Keyword("for")
        for_token.set_name("for")
        for_token.set_parse_action(lambda string,position,token: ForToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # in keyword token, also allowed in conditional statements
        in_token = Keyword("in")
        in_token.set_name("in")
        in_token.set_parse_action(lambda string,position,token: InToken(position, col(position,string), lineno(position,string), token.as_list()[0]))


        # Literal value tokens
        # Token token, Chronicle calls state value field names tokens in their docs
        token_token = Word(srange("[a-zA-Z0-9_.\-@]"))
        token_token.set_name("token")
        token_token.set_parse_action(lambda string,position,token: TokenToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # String token, strings can be surrounded by "" or ''
        string_token = QuotedString('"', escChar='\\') | QuotedString("'", escChar='\\')
        string_token.set_name("string")
        string_token.set_parse_action(lambda string,position,token: StringToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # Boolean token
        boolean_token = Keyword("true") | Keyword("false")
        boolean_token.set_name("boolean")
        boolean_token.set_parse_action(lambda string,position,token: BoolToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # Numerical tokens
        number_token = Combine(Optional(Optional(Word(nums)) + Literal(".")) + Word(nums))
        number_token.set_name("number")
        number_token.set_parse_action(lambda string,position,token: NumberToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # Regex tokens
        # regex_token = Combine((Opt('\\') + Literal('/')) + ... + (Opt('\\') + Literal('/')))
        regex_token = QuotedString('/', escChar='\\')
        regex_token.set_name("regex")
        regex_token.set_parse_action(lambda string,position,token: RegexToken(position, col(position,string), lineno(position,string), token.as_list()[0]))

        #######################
        # Pattern definitions #
        #######################
        # recursive pattern initialization
        if_block = Forward()
        elseif_block = Forward()
        else_block = Forward()
        conditional = Forward()
        loop = Forward()
        # Lazy list definition, used in filter config options, commas optional and empty indices allowed
        list_value = lbracket_token - ZeroOrMore(string_token | number_token | boolean_token | token_token | comma_token) + rbracket_token
        list_value.set_parse_action(lambda token: List(token.as_list()))
        # Key value pair pattern definition, used as values of a hash
        key_value = (string_token | token_token) + arrow_token + (string_token | token_token | list_value) + Optional(comma_token)
        key_value.set_parse_action(lambda token: KeyValue(token.as_list()))
        # Hash pattern definition, key value pairs surrounded by brackets
        hash_value = lbrace_token - OneOrMore(key_value) + rbrace_token
        hash_value.set_parse_action(lambda token: Hash(token.as_list()))
        # Function config option definition, ex. overwrite => [ "message", "day", "time" ]
        function_config = function_config_token + arrow_token + (list_value | hash_value | boolean_token | string_token | token_token)
        function_config.set_parse_action(lambda token: FunctionConfig(token.as_list()))
        # Function definition, ex. json { ... }
        function = function_token + lbrace_token - ZeroOrMore(function_config + Optional(comma_token)) + rbrace_token
        function.set_parse_action(lambda token: Function(token.as_list()))
        # Conditional statement pattern definition
        # Any operator that can appear in a statement
        conditional_operators = in_token|and_token|or_token|lte_token|gte_token|eq_token|ne_token|lt_token|gt_token|match_token|no_match_token|subtraction_token|addition_token|division_token|multiplication_token|not_token
        conditional_operators.set_name("operators")
        # Used for state data field names in conditional statements, ex. [message][value]
        conditional_token = OneOrMore(lbracket_token + token_token + rbracket_token)
        conditional_token.set_name("conditional token")
        conditional_token.set_parse_action(lambda token: ConditionalToken(token.as_list()))
        # Lists used in conditional statements cannot contain tokens to avoid ambiguity with a bracketed token
        conditional_list_value = lbracket_token - ZeroOrMore(string_token | number_token | boolean_token | comma_token) + rbracket_token
        conditional_list_value.set_name("list")
        conditional_list_value.set_parse_action(lambda token: List(token.as_list()))
        # Any value that can appear in a statement
        conditional_value = number_token|string_token|regex_token|boolean_token|conditional_token|token_token|conditional_list_value
        # Conditional expressions are difficult to parse and are not really necessary to fully evaluate so we don't care what order the tokens are in as long as they are valid conditional statement grammar
        statement = OneOrMore(lparen_token|rparen_token|conditional_value|conditional_operators)
        statement.set_parse_action(lambda token: ConditionalStatement(token.as_list()))

        if_block <<= if_token - statement + lbrace_token - ZeroOrMore(function|conditional|loop) + rbrace_token
        if_block.set_parse_action(lambda token: If(token.as_list()))

        elseif_block <<= elseif_token + statement + lbrace_token - ZeroOrMore(function|conditional|loop) + rbrace_token
        elseif_block.set_parse_action(lambda token: ElseIf(token.as_list()))

        else_block <<= else_token + lbrace_token - ZeroOrMore(function|conditional|loop) + rbrace_token
        else_block.set_parse_action(lambda token: Else(token.as_list()))

        conditional <<= if_block - ZeroOrMore(elseif_block) + Optional(else_block)

        loop_statement = Optional(token_token + comma_token) + token_token + in_token + token_token
        loop_statement.set_parse_action(lambda token: LoopStatement(token.as_list()))
        loop <<= for_token + loop_statement + lbrace_token - ZeroOrMore(function|conditional|loop) + rbrace_token
        loop.set_parse_action(lambda token: For(token.as_list()))

        filter_block = filter_token + lbrace_token - OneOrMore(function|conditional|loop) + rbrace_token
        filter_block.set_parse_action(lambda token: Filter(token.as_list()))

        comment = Literal('#') + ... + LineEnd()
        self.grammars = StringStart() + filter_block + StringEnd()
        # Ignore commented statements
        self.grammars.ignore(comment_token) # may not want to ignore comments if we want to be able to re-write the parser after taking it in

    def parse_file(self, file_name):
        return self.grammars.parse_file(file_name).as_list()[0]

    def parse_string(self, string):
        return self.grammars.parse_string(string).as_list()[0]

    def test(self):
        return self.grammars.parse_file("/Users/caleb.bryant/Library/CloudStorage/OneDrive-Cyderes/TelEng/test.conf").as_list()[0]
        