class Token:
	def __init__(self, line, col, value, kind):
		self.tokenKinds = [
			"FILTER",
			"MUTATE",
			"CONVERT",
			"GSUB",
			"GSUBEXPRESSION",
			"LOWERCASE",
			"MERGE",
			"RENAME",
			"REPLACE",
			"UPPERCASE",
			"DATE",
			"DATEMATCH",
			"REBASE",
			"TIMEZONE",
			"DROP",
			"IF",
			"FIELD",
			"FOR",
			"GROK",
			"GROKPATTERN",
			"MATCH",
			"OVERWRITE",
			"JSON",
			"CSV",
			"KV",
			"COMMA",
			"LBRACE",
			"RBRACE",
			"LBRACKET",
			"RBRACKET",
			"ASSIGN",
			"AND",
			"OR",
			"GT",
			"LT",
			"LTE",
			"GTE",
			"EQ",
			"CONTAINS",
			"NOTCONTAINS",
			"NEQ",
			"IN",
			"LVAL",
			"RVAL",
			"ASSIGNSTATEMENT",
			"QUOTEDVAL",
			"INTEGER",
			"LIST",
			"ONERROR",
			"SOURCE",
			"TARGET",
			"FIELDSPLIT",
			"VALUESPLIT",
			"OPTION",
			"IDENTIFIER",
			"BOOLEAN",
			"NUMBER"
		]
		self.line = line
		self.column = col
		assert kind in self.tokenKinds
		self.kind = kind
		self.value = value

class FunctionToken(Token):
	def __init__(self, line, col, functionName):
		super().__init__(line, col, functionName, "FUNCTION")

class FunctionOptionToken(Token):
	def __init__(self, line, col, functionOptionName):
		super().__init__(line, col, functionOptionName, "OPTION")

class FilterToken(Token):
	def __init__(self, line, col):
		super().__init__(line, col, "filter", "FILTER")

class PluginToken(Token):
	def __init__(self, line, col, pluginName):
		super().__init__(line, col, pluginName, "PLUGIN")

class MutateToken(Token):
	def __init__(self, line, col, token_as_list):
		self.function = []
		self.on_error = None
		for entry in token_as_list:
			if type(entry) != OnErrorToken:
				self.function.append(entry)
			else:
				self.on_error = entry
		super().__init__(line, col, None, "MUTATE")

class ConvertToken(Token):
	def __init__(self, line, col, token_as_list):
		assert token_as_list[0] == "convert"
		self.statements = token_as_list[2:]
		super().__init__(line, col, "convert", "CONVERT")

class GsubToken(Token):
	def __init__(self, line, col, token_as_list):
		assert token_as_list[0] == "gsub"
		self.expressions = token_as_list[2:]
		super().__init__(line, col, None, "GSUB")

class GsubExpressionToken(Token):
	def __init__(self, line, col, token_as_list):
		self.source = token_as_list[0]
		self.pattern = token_as_list[1]
		self.replacement = token_as_list[2]
		super().__init__(line, col, None, "GSUBEXPRESSION")

class LowercaseToken(Token):
	def __init__(self, line, col, token_as_list):
		assert token_as_list[0] == "lowercase"
		self.expressions = token_as_list[2:]
		super().__init__(line, col, "lowercase", "LOWERCASE")

class MergeToken(Token):
	def __init__(self, line, col, token_as_list):
		assert token_as_list[0] == "merge"
		self.statements = token_as_list[2:]
		super().__init__(line, col, None, "MERGE")

class RenameToken(Token):
	def __init__(self, line, col, token_as_list):
		assert token_as_list[0] == "rename"
		self.statements = token_as_list[2:]
		super().__init__(line, col, "rename", "RENAME")

class ReplaceToken(Token):
	def __init__(self, line, col, token_as_list):
		assert token_as_list[0] == "replace"
		self.statements = token_as_list[2:]
		super().__init__(line, col, None, "REPLACE")

class UppercaseToken(Token):
	def __init__(self, line, col, token_as_list):
		assert token_as_list[0] == "uppercase"
		self.statements = token_as_list[2:]
		super().__init__(line, col, None, "UPPERCASE")

class DateToken(Token):
	def __init__(self, line, col, token_as_list):
		self.match = token_as_list[1]
		self.rebase = None
		self.on_error = None
		for option in token_as_list[2:]:
			if type(option) != OnErrorToken:
				if option.name == "rebase":
					self.rebase = option
			else:
				self.on_error = option
		super().__init__(line, col, "date", "DATE")

class DateMatchToken(Token):
	def __init__(self, line, col, token_as_list):
		self.input = token_as_list[1]
		self.patterns = token_as_list[2:]
		super().__init__(line, col, None, "DATEMATCH")

class RebaseToken(Token):
	def __init__(self, line, col):
		super().__init__(line, col, "rebase", "REBASE")

class TimezoneToken(Token):
	def __init__(self, line, col):
		super().__init__(line, col, "timezone", "TIMEZONE")

class DropToken(Token):
	def __init__(self, line, col, token_as_list):
		self.tag = token_as_list[3]
		super().__init__(line, col, None, "DROP")

class IfToken(Token):
	def __init__(self, line, col):
		super().__init__(line, col, "if", "IF")

class ForToken(Token):
	def __init__(self, line, col):
		super().__init__(line, col, "for", "FOR")

class GrokPatternToken(Token):
	def __init__(self, line, col, grok_pattern):
		self.input_field = grok_pattern[0]
		self.assign = grok_pattern[1]
		self.patterns = grok_pattern[2:]
		super().__init__(line, col, None, "GROKPATTERN")

class GrokToken(Token):
	def __init__(self, line, col, grok_code_block):
		self.value = grok_code_block[0]
		self.assign = grok_code_block[1]
		self.patterns = []
		self.overwrite = None
		self.on_error = None
		for entry in grok_code_block[2:]:
			if type(entry) == GrokPatternToken:
				self.patterns.append(entry)
			elif type(entry) == OverwriteToken:
				self.overwrite = entry
			elif type(entry) == OnErrorToken:
				self.on_error = entry
		super().__init__(line, col, None, "GROK")

class MatchToken(Token):
	def __init__(self, line, col):
		super().__init__(line, col, "match", "MATCH")

class OverwriteToken(Token):
	def __init__(self, line, col, token_list):
		self.left = token_list[0]
		self.middle = token_list[1]
		self.right = token_list[2]
		super().__init__(line, col, f"{self.left} {self.middle.value} {self.right}", "OVERWRITE")

class JsonToken(Token):
	def __init__(self, line, col, token_as_list):
		self.options =[]
		self.on_error = None
		for entry in token_as_list:
			if type(entry) != OnErrorToken:
				self.options.append(entry)
			else:
				self.on_error = entry
		super().__init__(line, col, None, "JSON")

class CsvToken(Token):
	def __init__(self, line, col, token_as_list):
		self.options =[]
		self.on_error = None
		for entry in token_as_list:
			if type(entry) != OnErrorToken:
				self.options.append(entry)
			else:
				self.on_error = entry
		super().__init__(line, col, None, "CSV")

class KvToken(Token):
	def __init__(self, line, col, token_as_list):
		self.options =[]
		self.on_error = None
		for entry in token_as_list:
			if type(entry) != OnErrorToken:
				self.options.append(entry)
			else:
				self.on_error = entry
		super().__init__(line, col, None, "KV")

class CommaToken(Token):
	def __init__(self, line, col):
		super().__init__(line, col, ",", "COMMA")

class LbraceToken(Token):
	def __init__(self, line, col):
		super().__init__(line, col, "{", "LBRACE")
		
class RbraceToken(Token):
	def __init__(self, line, col):
		super().__init__(line, col, "}", "RBRACE")

class LbracketToken(Token):
	def __init__(self, line, col):
		super().__init__(line, col, "[", "LBRACKET")
		
class RbracketToken(Token):
	def __init__(self, line, col):
		super().__init__(line, col, "]", "RBRACKET")

class AssignToken(Token):
	def __init__(self, line, col, value):
		super().__init__(line, col, value, "ASSIGN")

class AndToken(Token):
	def __init__(self, line, col):
		super().__init__(line, col, "and", "AND")

class OrToken(Token):
	def __init__(self, line, col):
		super().__init__(line, col, "or", "OR")

class EqToken(Token):
	def __init__(self, line, col):
		super().__init__(line, col, "==", "EQ")

class NeqToken(Token):
	def __init__(self, line, col):
		super().__init__(line, col, "!=", "NEQ")

class RegExMatchToken(Token):
	def __init__(self, line, col):
		super().__init__(line, col, "=~", "CONTAINS")

class RegExNotMatchToken(Token):
	def __init__(self, line, col):
		super().__init__(line, col, "!~", "NOTCONTAINS")

class LtToken(Token):
	def __init__(self, line, col):
		super().__init__(line, col, "<", "LT")

class GtToken(Token):
	def __init__(self, line, col):
		super().__init__(line, col, ">", "GT")

class LteToken(Token):
	def __init__(self, line, col):
		super().__init__(line, col, "<=", "LTE")

class GteToken(Token):
	def __init__(self, line, col):
		super().__init__(line, col, ">=", "GTE")

class InToken(Token):
	def __init__(self, line, col):
		super().__init__(line, col, "in", "IN")

class FieldNameToken(Token):
	def __init__(self, line, col, fieldNameVal):
		super().__init__(line, col, fieldNameVal, "FIELD")

class QuotedValToken(Token):
	def __init__(self, line, col, token):
		super().__init__(line, col, token, "QUOTEDVAL")

class IntegerToken(Token):
	def __init__(self, line, col, intVal):
		super().__init__(line, col, intVal, "INTEGER")

class ListToken(Token):
	def __init__(self, line, col, val_list):
		super().__init__(line, col, val_list, "LIST")

class RValToken(Token):
	def __init__(self, line, col, val):
		super().__init__(line, col, val, "LVAL")

class LValToken(Token):
	def __init__(self, line, col, val):
		super().__init__(line, col, val, "RVAL")

class AssignStatementToken(Token):
	def __init__(self, line, col, token_list):
		self.left = token_list[0]
		self.middle = token_list[1]
		self.right = token_list[2]
		super().__init__(line, col, f"{self.left.value} {self.middle.value} {self.right.value}", "ASSIGNSTATEMENT")

class OnErrorToken(Token):
	def __init__(self, line, col, token_list):
		self.left = token_list[0]
		self.middle = token_list[1]
		self.right = token_list[2]
		super().__init__(line, col, f"{self.left} {self.middle.value} {self.right}", "ONERROR")

class SourceToken(Token):
	def __init__(self, line, col):
		super().__init__(line, col, "source", "SOURCE")

class TargetToken(Token):
	def __init__(self, line, col):
		super().__init__(line, col, "target", "TARGET")

class FieldSplitToken(Token):
	def __init__(self, line, col):
		super().__init__(line, col, "field_split", "FIELDSPLIT")

class ValueSplitToken(Token):
	def __init__(self, line, col):
		super().__init__(line, col, "value_split", "VALUESPLIT")

class OptionToken(Token):
	def __init__(self, line, col, token_as_list):
		self.name = token_as_list[0]
		self.value = token_as_list[1]
		super().__init__(line, col, self.name, "OPTION")

class IdentifierToken(Token):
	def __init__(self, line, col, token):
		super().__init__(line, col, token, "IDENTIFIER")

class BoolToken(Token):
	def __init__(self, line, col, token):
		super().__init__(line, col, token, "BOOLEAN")

class NumToken(Token):
	def __init__(self, line, col, token):
		super().__init__(line, col, token, "NUMBER")

