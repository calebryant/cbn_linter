# Created 2023/07/12
# Author: Caleb Bryant
# Title: Tokens.py
# Description: This file defines a Token class that represent all the valid syntax tokens allowed in a Chronicle parser config file. This allows us to check for syntactical errors easier.
# References: https://www.geeksforgeeks.org/introduction-of-lexical-analysis/

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

class PluginToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.valid_plugins = [
			"base64",
			"clone",
			"csv",
			"date",
			"drop",
			"grok",
			"json",
			"kv",
			"mutate",
			"xml"
		]
		if token_value in self.valid_plugins:
			self.value = token_value
		else:
			print(f"WARN: Unknown plugin '{token_value}' used at line:{row} col:{column}")

class FunctionToken(Token):
	def __init__(self, position, column, row, token_value):
		super().__init__(position, column, row)
		self.valid_functions = [
			"convert",
			"copy",
			"gsub",
			"join",
			"lowercase",
			"match",
			"merge",
			"coerce",
			"rename",
			"replace",
			"split",
			"strip",
			"update",
			"uppercase",
			"capitalize",
			"xpath"
		]
		if token_value in self.valid_functions:
			self.value = token_value
		else:
			print(f"WARN: Unknown function '{token_value}' used at line:{row} col:{column}")

# class GrokMatchToken(Token):
# 	def __init__(self, position, column, row):
# 		super().__init__(position, column, row)
# 		self.value = "match"

# class GrokToken(Token):
# 	def __init__(self, position, column, row):
# 		super().__init__(position, column, row)
# 		self.value = "grok"

# class GsubToken(Token):
# 	def __init__(self, position, column, row):
# 		super().__init__(position, column, row)
# 		self.value = "gsub"

# class LowercaseToken(Token):
# 	def __init__(self, position, column, row):
# 		super().__init__(position, column, row)
# 		self.value = "lowercase"

# class UppercaseToken(Token):
# 	def __init__(self, position, column, row):
# 		super().__init__(position, column, row)
# 		self.value = "uppercase"

# class ReplaceToken(Token):
# 	def __init__(self, position, column, row):
# 		super().__init__(position, column, row)
# 		self.value = "replace"

# class MergeToken(Token):
# 	def __init__(self, position, column, row):
# 		super().__init__(position, column, row)
# 		self.value = "Merge"

# class RenameToken(Token):
# 	def __init__(self, position, column, row):
# 		super().__init__(position, column, row)
# 		self.value = "rename"

# class ConvertToken(Token):
# 	def __init__(self, position, column, row):
# 		super().__init__(position, column, row)
# 		self.value = "convert"

# class CopyToken(Token):
# 	def __init__(self, position, column, row):
# 		super().__init__(position, column, row)
# 		self.value = "copy"

# class MutateToken(Token):
# 	def __init__(self, position, column, row):
# 		super().__init__(position, column, row)
# 		self.value = "mutate"

# class JsonToken(Token):
# 	def __init__(self, position, column, row):
# 		super().__init__(position, column, row)
# 		self.value = "json"

# class CsvToken(Token):
# 	def __init__(self, position, column, row):
# 		super().__init__(position, column, row)
# 		self.value = "csv"

# class KvToken(Token):
# 	def __init__(self, position, column, row):
# 		super().__init__(position, column, row)
# 		self.value = "kv"

# class DateMatchToken(Token):
# 	def __init__(self, position, column, row):
# 		super().__init__(position, column, row)
# 		self.value = "match"

# class DateToken(Token):
# 	def __init__(self, position, column, row):
# 		super().__init__(position, column, row)
# 		self.value = "date"

# class DropToken(Token):
# 	def __init__(self, position, column, row):
# 		super().__init__(position, column, row)
# 		self.value = "drop"

# class RegexToken(Token):
# 	def __init__(self, position, column, row, value):
# 		super().__init__(position, column, row)
# 		self.value = value

# class MathOpToken(Token):
# 	def __init__(self, position, column, row, value):
# 		super().__init__(position, column, row)
# 		self.value = value

# class BoolCompareToken(Token):
# 	def __init__(self, position, column, row, value):
# 		super().__init__(position, column, row)
# 		self.value = value

# class BoolOpToken(Token):
# 	def __init__(self, position, column, row, value):
# 		super().__init__(position, column, row)
# 		self.value = value

# class BoolNegateToken(Token):
# 	def __init__(self, position, column, row, value):
# 		super().__init__(position, column, row)
# 		self.value = value

class IfStatementToken(Token):
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
        

