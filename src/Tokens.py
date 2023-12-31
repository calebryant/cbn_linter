# Created 2023/07/12
# Author: Caleb Bryant
# Title: Tokens.py
# Description: This file defines a Token class that represent all the valid syntax tokens allowed in a Chronicle parser config file. This allows us to check for syntactical errors easier.
# References: https://www.geeksforgeeks.org/introduction-of-lexical-analysis/

class Token:
	def __init__(self, position, column, row, token_value=None):
		self.pos = position
		self.col = column
		self.row = row
		self.value = token_value
    
	def print_location(self):
		return [ self.pos, self.col, self.row ]

	def coordinates(self):
		return [ self.row, self.col]

	def __int__(self):
		return self.row

	def __str__(self):
		return self.value

class LBraceToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = '{'

class RBraceToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = '}'

class LBracketToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = '['

class RBracketToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = ']'

class LParenToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = '('

class RParenToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = ')'

class CommaToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = ','

class ArrowToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = token_value

class TokenToken(Token):
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

# class FunctionToken(Token):
# 	def __init__(self, position, column, row, token_value):
# 		super().__init__(position, column, row)
# 		self.value = token_value

class GrokToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = "grok"

class JsonToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = "json"

class XmlToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = "xml"

class KvToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = "kv"

class CsvToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = "csv"

class MutateToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = "mutate"

class Base64Token(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = "base64"

class DateToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = "date"

class DropToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = "drop"

class StatedumpToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = "statedump"

class FunctionConfigToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = token_value

class MatchToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class OverwriteToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class OnErrorToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class SourceToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class TargetToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class ArrayFunctionToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class XpathToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class FieldSplitToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class UnescapeFieldSplitToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class ValueSplitToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class UnescapeValueSplitToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class WhitespaceToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class TrimValueToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class SeparatorToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class UnescapeSeparatorToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class ConvertToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class GsubToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class LowercaseToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class MergeToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class RenameToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class ReplaceToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class UppercaseToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class RemoveFieldToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class CopyToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class SplitToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class EncodingToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class TimezoneToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class RebaseToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class TagToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class LabelToken(Token):
    def __init__(self, position, column, row, token_value):
        super().__init__(position, column, row)
        self.value = token_value

class RegexToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = token_value

class MathOpToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = token_value

class BoolCompareToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = token_value

class BoolOpToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = token_value

class IfToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = "if"

class ElseIfToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = "else if"

class ElseToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = "else"

class InToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = "in"

class ForToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = "for"

class FilterToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.value = "filter"