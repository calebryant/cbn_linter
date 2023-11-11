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
        # function_token = Keyword("grok") | Keyword("json") | Keyword("xml") | Keyword("kv") | Keyword("csv") | Keyword("mutate") | Keyword("base64") | Keyword("date") | Keyword("drop") | Keyword("statedump")
        # function_token.set_name("function keyword")
        # function_token.set_parse_action(lambda string,position,token: FunctionToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # grok keyword token
        grok_token = Keyword("grok")
        grok_token.set_parse_action(lambda string,position,token: GrokToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # json keyword token
        json_token = Keyword("json")
        json_token.set_parse_action(lambda string,position,token: JsonToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # xml keyword token
        xml_token = Keyword("xml")
        xml_token.set_parse_action(lambda string,position,token: XmlToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # kv keyword token
        kv_token = Keyword("kv")
        kv_token.set_parse_action(lambda string,position,token: KvToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # csv keyword token
        csv_token = Keyword("csv")
        csv_token.set_parse_action(lambda string,position,token: CsvToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # mutate keyword token
        mutate_token = Keyword("mutate")
        mutate_token.set_parse_action(lambda string,position,token: MutateToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # base64 keyword token
        base64_token = Keyword("base64")
        base64_token.set_parse_action(lambda string,position,token: Base64Token(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # date keyword token
        date_token = Keyword("date")
        date_token.set_parse_action(lambda string,position,token: DateToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # drop keyword token
        drop_token = Keyword("drop")
        drop_token.set_parse_action(lambda string,position,token: DropToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # statedump keyword token
        statedump_token = Keyword("statedump")
        statedump_token.set_parse_action(lambda string,position,token: StatedumpToken(position, col(position,string), lineno(position,string), token.as_list()[0]))

        # Function config tokens
        # function_config_token = Keyword("match") | Keyword("overwrite") | Keyword("on_error") | Keyword("source") | Keyword("target") | Keyword("array_function") | Keyword("xpath") | Keyword("field_split") | Keyword("unescape_field_split") | Keyword("value_split") | Keyword("unescape_value_split") | Keyword("whitespace") | Keyword("trim_key") | Keyword("trim_value") | Keyword("separator") | Keyword("unescape_separator") | Keyword("convert") | Keyword("gsub") | Keyword("lowercase") | Keyword("merge") | Keyword("rename") | Keyword("replace") | Keyword("uppercase") | Keyword("remove_field") | Keyword("copy") | Keyword("split") | Keyword("encoding") | Keyword("timezone") | Keyword("rebase") | Keyword("tag") | Keyword("label")
        # function_config_token.set_name("function config option")
        # function_config_token.set_parse_action(lambda string,position,token: FunctionConfigToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        
        # match keyword token
        match_token = Keyword("match")
        match_token.set_name("match")
        match_token.set_parse_action(lambda string,position,token: MatchToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # overwrite keyword token
        overwrite_token = Keyword("overwrite")
        overwrite_token.set_name("overwrite")
        overwrite_token.set_parse_action(lambda string,position,token: OverwriteToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # on_error keyword token
        on_error_token = Keyword("on_error")
        on_error_token.set_name("on_error")
        on_error_token.set_parse_action(lambda string,position,token: OnErrorToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # source keyword token
        source_token = Keyword("source")
        source_token.set_name("source")
        source_token.set_parse_action(lambda string,position,token: SourceToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # target keyword token
        target_token = Keyword("target")
        target_token.set_name("target")
        target_token.set_parse_action(lambda string,position,token: TargetToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # array_function keyword token
        array_function_token = Keyword("array_function")
        array_function_token.set_name("array_function")
        array_function_token.set_parse_action(lambda string,position,token: ArrayFunctionToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # xpath keyword token
        xpath_token = Keyword("xpath")
        xpath_token.set_name("xpath")
        xpath_token.set_parse_action(lambda string,position,token: XpathToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # field_split keyword token
        field_split_token = Keyword("field_split")
        field_split_token.set_name("field_split")
        field_split_token.set_parse_action(lambda string,position,token: FieldSplitToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # unescape_field_split keyword token
        unescape_field_split_token = Keyword("unescape_field_split")
        unescape_field_split_token.set_name("unescape_field_split")
        unescape_field_split_token.set_parse_action(lambda string,position,token: UnescapeFieldSplitToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # value_split keyword token
        value_split_token = Keyword("value_split")
        value_split_token.set_name("value_split")
        value_split_token.set_parse_action(lambda string,position,token: ValueSplitToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # unescape_value_split keyword token
        unescape_value_split_token = Keyword("unescape_value_split")
        unescape_value_split_token.set_name("unescape_value_split")
        unescape_value_split_token.set_parse_action(lambda string,position,token: UnescapeValueSplitToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # whitespace keyword token
        whitespace_token = Keyword("whitespace")
        whitespace_token.set_name("whitespace")
        whitespace_token.set_parse_action(lambda string,position,token: WhitespaceToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # trim_value keyword token
        trim_value_token = Keyword("trim_value")
        trim_value_token.set_name("trim_value")
        trim_value_token.set_parse_action(lambda string,position,token: TrimValueToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # separator keyword token
        separator_token = Keyword("separator")
        separator_token.set_name("separator")
        separator_token.set_parse_action(lambda string,position,token: SeparatorToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # unescape_separator keyword token
        unescape_separator_token = Keyword("unescape_separator")
        unescape_separator_token.set_name("unescape_separator")
        unescape_separator_token.set_parse_action(lambda string,position,token: UnescapeSeparatorToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # convert keyword token
        convert_token = Keyword("convert")
        convert_token.set_name("convert")
        convert_token.set_parse_action(lambda string,position,token: ConvertToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # gsub keyword token
        gsub_token = Keyword("gsub")
        gsub_token.set_name("gsub")
        gsub_token.set_parse_action(lambda string,position,token: GsubToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # lowercase keyword token
        lowercase_token = Keyword("lowercase")
        lowercase_token.set_name("lowercase")
        lowercase_token.set_parse_action(lambda string,position,token: LowercaseToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # merge keyword token
        merge_token = Keyword("merge")
        merge_token.set_name("merge")
        merge_token.set_parse_action(lambda string,position,token: MergeToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # rename keyword token
        rename_token = Keyword("rename")
        rename_token.set_name("rename")
        rename_token.set_parse_action(lambda string,position,token: RenameToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # replace keyword token
        replace_token = Keyword("replace")
        replace_token.set_name("replace")
        replace_token.set_parse_action(lambda string,position,token: ReplaceToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # uppercase keyword token
        uppercase_token = Keyword("uppercase")
        uppercase_token.set_name("uppercase")
        uppercase_token.set_parse_action(lambda string,position,token: UppercaseToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # remove_field keyword token
        remove_field_token = Keyword("remove_field")
        remove_field_token.set_name("remove_field")
        remove_field_token.set_parse_action(lambda string,position,token: RemoveFieldToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # copy keyword token
        copy_token = Keyword("copy")
        copy_token.set_name("copy")
        copy_token.set_parse_action(lambda string,position,token: CopyToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # split keyword token
        split_token = Keyword("split")
        split_token.set_name("split")
        split_token.set_parse_action(lambda string,position,token: SplitToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # encoding keyword token
        encoding_token = Keyword("encoding")
        encoding_token.set_name("encoding")
        encoding_token.set_parse_action(lambda string,position,token: EncodingToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # timezone keyword token
        timezone_token = Keyword("timezone")
        timezone_token.set_name("timezone")
        timezone_token.set_parse_action(lambda string,position,token: TimezoneToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # rebase keyword token
        rebase_token = Keyword("rebase")
        rebase_token.set_name("rebase")
        rebase_token.set_parse_action(lambda string,position,token: RebaseToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # tag keyword token
        tag_token = Keyword("tag")
        tag_token.set_name("tag")
        tag_token.set_parse_action(lambda string,position,token: TagToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
        # label keyword token
        label_token = Keyword("label")
        label_token.set_name("label")
        label_token.set_parse_action(lambda string,position,token: LabelToken(position, col(position,string), lineno(position,string), token.as_list()[0]))

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
        re_match_token = Literal("=~")
        re_match_token.set_name("=~")
        re_match_token.set_parse_action(lambda string,position,token: BoolCompareToken(position, col(position,string), lineno(position,string), token.as_list()[0]))
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
        key_value = (string_token | token_token) + arrow_token - (string_token | token_token | list_value) + Optional(comma_token)
        key_value.set_parse_action(lambda token: KeyValue(token.as_list()))
        # Hash pattern definition, key value pairs surrounded by brackets
        hash_value = lbrace_token - OneOrMore(key_value) + rbrace_token
        hash_value.set_parse_action(lambda token: Hash(token.as_list()))
        # All possible function config options defined below
        # match function config pattern definition
        match_function_config = match_token + arrow_token - (hash_value|list_value)
        match_function_config.set_parse_action(lambda token: Match(token.as_list()))
        # overwrite function config pattern definition
        overwrite_function_config = overwrite_token + arrow_token - (token_token|string_token|list_value)
        overwrite_function_config.set_parse_action(lambda token: Overwrite(token.as_list()))
        # on_error function config pattern definition
        on_error_function_config = on_error_token + arrow_token + (token_token|string_token)
        on_error_function_config.set_parse_action(lambda token: OnError(token.as_list()))
        # source function config pattern definition
        source_function_config = source_token + arrow_token + (token_token|string_token)
        source_function_config.set_parse_action(lambda token: Source(token.as_list()))
        # target function config pattern definition
        target_function_config = target_token + arrow_token + (token_token|string_token)
        target_function_config.set_parse_action(lambda token: Target(token.as_list()))
        # array_function function config pattern definition
        array_function_function_config = array_function_token + arrow_token + string_token
        array_function_function_config.set_parse_action(lambda token: ArrayFunction(token.as_list()))
        # xpath function config pattern definition
        xpath_function_config = xpath_token + arrow_token - hash_value
        xpath_function_config.set_parse_action(lambda token: Xpath(token.as_list()))
        # field_split function config pattern definition
        field_split_function_config = field_split_token + arrow_token + string_token
        field_split_function_config.set_parse_action(lambda token: FieldSplit(token.as_list()))
        # unescape_field_split function config pattern definition
        unescape_field_split_function_config = unescape_field_split_token + arrow_token + string_token
        unescape_field_split_function_config.set_parse_action(lambda token: UnescapeFieldSplit(token.as_list()))
        # value_split function config pattern definition
        value_split_function_config = value_split_token + arrow_token + string_token
        value_split_function_config.set_parse_action(lambda token: ValueSplit(token.as_list()))
        # unescape_value_split function config pattern definition
        unescape_value_split_function_config = unescape_value_split_token + arrow_token + string_token
        unescape_value_split_function_config.set_parse_action(lambda token: UnescapeValueSplit(token.as_list()))
        # whitespace function config pattern definition
        whitespace_function_config = whitespace_token + arrow_token + string_token
        whitespace_function_config.set_parse_action(lambda token: Whitespace(token.as_list()))
        # trim_value function config pattern definition
        trim_value_function_config = trim_value_token + arrow_token + string_token
        trim_value_function_config.set_parse_action(lambda token: TrimValue(token.as_list()))
        # separator function config pattern definition
        separator_function_config = separator_token + arrow_token + string_token
        separator_function_config.set_parse_action(lambda token: Separator(token.as_list()))
        # unescape_separator function config pattern definition
        unescape_separator_function_config = unescape_separator_token + arrow_token + boolean_token
        unescape_separator_function_config.set_parse_action(lambda token: UnescapeSeparator(token.as_list()))
        # convert function config pattern definition
        convert_function_config = convert_token + arrow_token - hash_value
        convert_function_config.set_parse_action(lambda token: Convert(token.as_list()))
        # gsub function config pattern definition
        gsub_function_config = gsub_token + arrow_token - list_value
        gsub_function_config.set_parse_action(lambda token: Gsub(token.as_list()))
        # lowercase function config pattern definition
        lowercase_function_config = lowercase_token + arrow_token - (list_value|token_token|string_token)
        lowercase_function_config.set_parse_action(lambda token: Lowercase(token.as_list()))
        # merge function config pattern definition
        merge_function_config = merge_token + arrow_token - hash_value
        merge_function_config.set_parse_action(lambda token: Merge(token.as_list()))
        # rename function config pattern definition
        rename_function_config = rename_token + arrow_token - hash_value
        rename_function_config.set_parse_action(lambda token: Rename(token.as_list()))
        # replace function config pattern definition
        replace_function_config = replace_token + arrow_token - hash_value
        replace_function_config.set_parse_action(lambda token: Replace(token.as_list()))
        # uppercase function config pattern definition
        uppercase_function_config = uppercase_token + arrow_token - (list_value|token_token|string_token)
        uppercase_function_config.set_parse_action(lambda token: Uppercase(token.as_list()))
        # remove_field function config pattern definition
        remove_field_function_config = remove_field_token + arrow_token - (list_value|token_token|string_token)
        remove_field_function_config.set_parse_action(lambda token: RemoveField(token.as_list()))
        # copy function config pattern definition
        copy_function_config = copy_token + arrow_token - hash_value
        copy_function_config.set_parse_action(lambda token: Copy(token.as_list()))
        # split function config pattern definition
        split_function_config = split_token + arrow_token - hash_value
        split_function_config.set_parse_action(lambda token: Split(token.as_list()))
        # encoding function config pattern definition
        encoding_function_config = encoding_token + arrow_token + string_token
        encoding_function_config.set_parse_action(lambda token: Encoding(token.as_list()))
        # timezone function config pattern definition
        timezone_function_config = timezone_token + arrow_token + string_token
        timezone_function_config.set_parse_action(lambda token: Timezone(token.as_list()))
        # rebase function config pattern definition
        rebase_function_config = rebase_token + arrow_token + boolean_token
        rebase_function_config.set_parse_action(lambda token: Rebase(token.as_list()))
        # tag function config pattern definition
        tag_function_config = tag_token + arrow_token + string_token
        tag_function_config.set_parse_action(lambda token: Tag(token.as_list()))
        # label function config pattern definition
        label_function_config = label_token + arrow_token + string_token
        label_function_config.set_parse_action(lambda token: Label(token.as_list()))
        # Function config option definition, ex. overwrite => [ "message", "day", "time" ]
        function_config = match_function_config|overwrite_function_config|on_error_function_config|source_function_config|target_function_config|array_function_function_config|xpath_function_config|field_split_function_config|unescape_field_split_function_config|value_split_function_config|unescape_value_split_function_config|whitespace_function_config|trim_value_function_config|separator_function_config|unescape_separator_function_config|convert_function_config|gsub_function_config|lowercase_function_config|merge_function_config|rename_function_config|replace_function_config|uppercase_function_config|remove_field_function_config|copy_function_config|split_function_config|encoding_function_config|timezone_function_config|rebase_function_config|tag_function_config|label_function_config
        # grok pattern definition
        grok_function = grok_token + lbrace_token - ZeroOrMore(function_config + Optional(comma_token)) + rbrace_token
        grok_function.set_parse_action(lambda token: Grok(token.as_list()))
        # json pattern definition
        json_function = json_token + lbrace_token - ZeroOrMore(function_config + Optional(comma_token)) + rbrace_token
        json_function.set_parse_action(lambda token: Json(token.as_list()))
        # xml pattern definition
        xml_function = xml_token + lbrace_token - ZeroOrMore(function_config + Optional(comma_token)) + rbrace_token
        xml_function.set_parse_action(lambda token: Xml(token.as_list()))
        # kv pattern definition
        kv_function = kv_token + lbrace_token - ZeroOrMore(function_config + Optional(comma_token)) + rbrace_token
        kv_function.set_parse_action(lambda token: Kv(token.as_list()))
        # csv pattern definition
        csv_function = csv_token + lbrace_token - ZeroOrMore(function_config + Optional(comma_token)) + rbrace_token
        csv_function.set_parse_action(lambda token: Csv(token.as_list()))
        # mutate pattern definition
        mutate_function = mutate_token + lbrace_token - ZeroOrMore(function_config + Optional(comma_token)) + rbrace_token
        mutate_function.set_parse_action(lambda token: Mutate(token.as_list()))
        # base64 pattern definition
        base64_function = base64_token + lbrace_token - ZeroOrMore(function_config + Optional(comma_token)) + rbrace_token
        base64_function.set_parse_action(lambda token: Base64(token.as_list()))
        # date pattern definition
        date_function = date_token + lbrace_token - ZeroOrMore(function_config + Optional(comma_token)) + rbrace_token
        date_function.set_parse_action(lambda token: Date(token.as_list()))
        # drop pattern definition
        drop_function = drop_token + lbrace_token - ZeroOrMore(function_config + Optional(comma_token)) + rbrace_token
        drop_function.set_parse_action(lambda token: Drop(token.as_list()))
        # statedump pattern definition
        statedump_function = statedump_token + lbrace_token - ZeroOrMore(function_config + Optional(comma_token)) + rbrace_token
        statedump_function.set_parse_action(lambda token: Statedump(token.as_list()))
        # Overall function definition
        function = grok_function | json_function | xml_function | kv_function | csv_function | mutate_function | base64_function | date_function | drop_function | statedump_function
        # Any operator that can appear in a statement
        conditional_operators = in_token|and_token|or_token|lte_token|gte_token|eq_token|ne_token|lt_token|gt_token|re_match_token|no_match_token|subtraction_token|addition_token|division_token|multiplication_token|not_token
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
        