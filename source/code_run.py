import global_variables as GV
import text_engine as TE
import numpy as np
import time, sys, os

np.warnings.filterwarnings('ignore')


################################
# global variables
################################

INTEGER_BASE_DIGITS = GV.INTEGER_BASE_DIGITS
INTEGER_BASES = GV.INTEGER_BASES
INTERPRETER_OPERATION_LIST = GV.INTERPRETER_OPERATION_LIST
INTERPRETER_OPERATION_LIST_GROUPED = GV.INTERPRETER_OPERATION_LIST_GROUPED
TOKEN_ARG_TYPES = GV.TOKEN_ARG_TYPES
INT  = GV.INT
UINT = GV.UINT
INTERPRETER_EXEC_LIMIT = GV.INTERPRETER_EXEC_LIMIT


################################
# Integer conversion
################################

# Checks if given input is a number
# Returns bool
def isNumber(number, baseN=None):
	if type(number) == int:
		return True
	elif type(number) != str:
		return False

	if not baseN:
		baseN = inBases(number)
	number = number[2:] if baseN != 0 else number
	baseN = 10 if baseN == 0 else baseN

	for digit in number:
		if not (digit in INTEGER_BASE_DIGITS[baseN] or digit == '-'):
			return False
	return True

# Checks if given input is baseN
# Returns base, 0 if base is not specified
def inBases(number):
	baseN = 10
	for base in INTEGER_BASES:
		if number[0:len(base)] == base:
			return INTEGER_BASES[base]
	return 0

# Converts string to number
# Returns np int
def toInt(number):
	baseN = inBases(number)
	number = number[2:] if baseN != 0 else number
	baseN = 10 if baseN == 0 else baseN
	if isNumber(number, baseN) and number != '':
		return INT(int(number, baseN))
	raise ValueError(f'unable convert given number \'{number}\' to string')


################################
# Token
################################

# Token, has type and value
class token:
	def __init__(self, type_, value=None):
		self.type  = type_
		self.value = value

	def __repr__(self):
		if self.value != None: return f'({self.type}: \'{self.value}\')'
		return f'({self.type})'


################################
# Lexer
################################

# Lexer, splits commands into tokens
class lexer:
	def __init__(self, opl):
		self.operation_list = opl

	# Imports user's code
	def import_commands(self, commands):
		self.commands = commands

		self.current_char = None
		self.char_pointer = -1
		self.advance()

	# Advances one character fordwars
	# Returns None if there is no character next
	def advance(self):
		self.char_pointer += 1
		self.current_char = self.commands[self.char_pointer] if self.char_pointer < len(self.commands) else None

	# Defines token type
	def give_token(self, value):
		if value[-1] == ':':
			return token('addr', value[0:-1])
		elif value[0] == '$':
			return token('var', value[1:])
		elif self.operation_list.get(value):
			return token('op', value.lower())
		elif isNumber(value):
			return token('int', toInt(value))
		raise TypeError(f'unable to define token for value \'{value}\'')

	# Splits user's code into tokens
	def make_tokens(self):
		value      = ''
		token_list = []

		isString, stringType = False, None

		while self.current_char != None:
			if self.current_char == '\n':
				if value:
					token_list.append(self.give_token(value))
					value = ''
				isString, stringType = False, None
				token_list.append(token('next'))
				self.advance()
			elif self.current_char == '\t':
				if isString:
					value += self.current_char
				else:
					token_list.append(token('indent'))
				self.advance()
			elif self.current_char == ';':
				if isString:
					value += self.current_char
				else:
					if value:
						token_list.append(self.give_token(value))
						value = ''
					token_list.append(token('next'))
				self.advance()
			elif self.current_char in '\'\"':
				if isString:
					if self.current_char == stringType:
						isString, stringType = False, None
						token_list.append(token('str', value))
						value = ''
					else:
						value += self.current_char
				else:
					isString, stringType = True, self.current_char
				self.advance()
			elif self.current_char == ' ':
				if isString:
					value += self.current_char
				else:
					if value:
						token_list.append(self.give_token(value))
						value = ''
				self.advance()
			elif self.current_char == '#':
				if isString:
					value += self.current_char
					self.advance()
				else:
					while self.current_char != '\n' and self.current_char:
						self.advance()
			else:
				value += self.current_char
				self.advance()

		if value:
			token_list.append(self.give_token(value))
		token_list.append(token('next'))

		return token_list


################################
# Interpreter
################################

class interpreter:
	def __init__(self):
		self.variables     = {'global': {}}
		self.addr_pointers = {'global': {}}
		self.in_function   = 'global'

		self.addr_stack    = np.zeros(0xffff, UINT)
		self.func_stack    = []
		self.stack_pointer = UINT(0)

		self.accumulator   = INT(0)
		self.display       = TE.display(32,32)

		self.enable_messages = True

	# Groups all tokens into instructions
	# Removes unnecessary spaces and indents
	# Makes address pointers (only global for now)
	def group_token_list(self, lexer_):
		self.instructions   = []
		current_instruction = {'indent': 0, 'op': None, 'args': []}
		line = 0

		isOp = False

		for tok in lexer_.make_tokens():
			if tok.type == 'indent':
				if not isOp:
					current_instruction['indent'] += 1
			elif tok.type == 'addr':
				if not isOp:
					self.addr_pointers['global'][tok.value] = line
					self.variables[tok.value] = {}
				else:
					current_instruction['args'].append(token('var', tok.value[1:]))
			elif tok.type == 'op':
				if not isOp:
					current_instruction['op'] = tok.value
					isOp = True
			elif tok.type in TOKEN_ARG_TYPES:
				if isOp:
					current_instruction['args'].append(tok)
			elif tok.type == 'next':
				if current_instruction['op']:
					if not (len(current_instruction['args']) in lexer_.operation_list[current_instruction['op']] or lexer_.operation_list[current_instruction['op']][0] == -1):
						raise TypeError('instruction \'{}\' requires {} arguments {} were(was) given\n\tline - {};\n\t{}'.format( current_instruction['op'], str(lexer_.operation_list[current_instruction['op']])[1:-1], len(current_instruction['args']),line+1, str(current_instruction)[1:-1].replace("'",'') ))
					self.instructions.append(current_instruction)
					line += 1
				current_instruction = {'indent': 0, 'op': None, 'args': []}
				isOp = False

	# Raises error when token with incorrect data type is given
	def raise_dtype_error(self, tok):
		raise TypeError('incorrect data type \'{}\'\n\tline - {};\n\t{}'.format(tok.type,self.program_counter,self.cinst_to_str()))

	# Returns string of current instruction
	# Mostly used in errors
	def cinst_to_str(self):
		return str(self.current_instruction)[1:-1].replace('\'','')

	# Searches for a variable with a given name
	# Returns location of the given variable
	def search_variable(self, name):
		if self.variables[self.in_function].get(name) != None:
			return self.in_function
		elif self.variables['global'].get(name) != None:
			return 'global'
		for func in reversed(self.func_stack):
			if self.variables[func].get(name) != None:
				return func

	# Writes a variable to memory
	def write_variable(self, name):
		if (var := self.search_variable(name)):
			self.variables[var][name] = self.accumulator
		else:
			self.variables[self.in_function][name] = self.accumulator

	# Reads the variable with the given name
	# Returns int
	def read_variable(self, name):
		if (var := self.search_variable(name)):
			return self.variables[var][name]
		raise NameError(f'name \'{name}\' is not defined')

	# Always returns int
	def get_value(self, value):
		if isinstance(value, token):
			if value.type == 'int':
				return value.value
			elif value.type == 'var':
				return self.read_variable(value.value)
			else:
				self.raise_dtype_error(value)
		else:
			return INT(value)

	# Writes given token to program counter
	def write_pc(self, tok):
		if tok.type == 'int':
			self.program_counter = tok.value
		elif tok.type == 'var':
			if (var := self.addr_pointers['global'].get(tok.value)) != None:
				self.program_counter = var
			else:
				raise KeyError('name \'{}\' is not defined\n\tline - {};\n\t{}'.format(tok.value,self.program_counter,self.cinst_to_str()))
		else:
			self.raise_dtype_error(tok)

	# Instruciton set, describes what each instruciton do
	def instruction_set(self, instruction):
		op, args = instruction['op'], instruction['args']

		if op in INTERPRETER_OPERATION_LIST_GROUPED['memory']:
			if op == 'load':
				self.accumulator = self.get_value(args[0])
			elif op == 'store':
				if len(args) > 1:
					self.accumulator = self.get_value(args[0])
					self.write_variable(args[1].value)
				else:
					self.write_variable(args[0].value)
			elif op == 'call':
				if self.stack_pointer+1 < len(self.addr_stack):
					self.addr_stack[self.stack_pointer] = self.program_counter
					self.stack_pointer += 1
				else:
					raise RecursionError('stack overflow\n\tline - {};\n\t{}'.format(self.cinst_to_str(),self.program_counter))

				self.func_stack.append(args[0].value)
				self.write_pc(args[0])
			elif op == 'return':
				if self.stack_pointer > 0:
					self.stack_pointer -= 1
					self.program_counter = self.addr_stack[self.stack_pointer]
				else:
					raise SyntaxError('\'return\' outside the function\n\tline - {};\n\t{}'.format(self.program_counter,self.cinst_to_str()))

				self.accumulator = self.get_value(args[0]) if len(args) > 0 else self.accumulator
				self.variables[self.func_stack[-1]] = {}
				self.func_stack.pop()
			elif op == 'jump':
				self.write_pc(args[0])
			elif op == 'jmpp' and self.accumulator > 0:
				self.write_pc(args[0])
			elif op == 'jmpz' and self.accumulator == 0:
				self.write_pc(args[0])
			elif op == 'jmpn' and self.accumulator < 0:
				self.write_pc(args[0])
		elif op in INTERPRETER_OPERATION_LIST_GROUPED['boolean']:
			if not args[0].type in ['int','var']:
				self.raise_data_type_error(token)

			if op == 'and':
				self.accumulator = self.accumulator & self.get_value(args[0])
			elif op == 'or':
				self.accumulator = self.accumulator | self.get_value(args[0])
			elif op == 'xor':
				self.accumulator = self.accumulator ^ self.get_value(args[0])
			elif op == 'not':
				self.accumulator = ~self.accumulator
			elif op == 'lst':
				self.accumulator = (self.accumulator & ~UINT(0)) << self.get_value(args[0])
			elif op == 'rst':
				self.accumulator = (self.accumulator & ~UINT(0)) >> self.get_value(args[0])

			if self.accumulator & ~(UINT(-1)>>1) > 0:
				self.flags['carry'] = 1
			self.accumulator = INT(self.accumulator)
		elif op in INTERPRETER_OPERATION_LIST_GROUPED['math']:
			if len(args) > 0:
				if not args[0].type in ['int','var']:
					self.raise_data_type_error(token)

			if op == 'add':
				self.accumulator = self.accumulator + self.get_value(args[0])
			elif op == 'sub':
				self.accumulator = self.accumulator - self.get_value(args[0])
			elif op == 'mul':
				self.accumulator = self.accumulator * self.get_value(args[0])
			elif op == 'div':
				if (var := self.get_value(args[0])) != 0:
					self.accumulator = self.accumulator // var
				else:
					raise ZeroDivisionError('division by zero\n\tline - {};\n\t{}'.format(self.program_counter,self.cinst_to_str()))
			elif op == 'mod':
				self.accumulator = self.accumulator % self.get_value(args[0])
			elif op == 'inc':
				self.accumulator = self.accumulator + 1
			elif op == 'dec':
				self.accumulator = self.accumulator - 1
			elif op == 'sgn':
				self.accumulator = min(1, max(-1, self.get_value(args[0])))
			elif op == 'cmp':
				self.accumulator = min(1, max(-1, self.accumulator - self.get_value(args[0])))
			elif op == 'abs':
				self.accumulator = abs(self.get_value(args[0]))
		elif op in INTERPRETER_OPERATION_LIST_GROUPED['special']:
			if op == 'uo':
				TE.fprint(self.accumulator)
			elif op == 'ui':
				self.accumulator = toInt(input(''))
			elif op == 'sleep':
				time.sleep(self.get_value(args[0])/1000)
			elif op == 'strout':
				end_string = ''
				for arg in args:
					if arg.type == 'str':
						end_string += arg.value
					else:
						end_string += str(self.get_value(arg))
				TE.fprint(end_string)
			elif op == 'halt':
				self.program_counter = len(self.instructions)
		elif op in INTERPRETER_OPERATION_LIST_GROUPED['display']:
			if op == 'plot':
				x = self.get_value(args[0])
				y = self.get_value(args[1])
				self.display.plot(x,y)
			elif op == 'update':
				self.display.update()
			elif op == 'cls':
				self.display.clear()

	# Executes given instructions
	def execute(self):
		self.program_counter = UINT(0)
		self.current_instruction = None

		self.flags = {'carry': 0}

		starting_time = time.perf_counter()

		executed = 0

		while self.program_counter < len(self.instructions) and executed < INTERPRETER_EXEC_LIMIT:
			self.current_instruction = self.instructions[self.program_counter]
			self.program_counter += 1
			if self.current_instruction['op']:
				self.in_function = 'global' if len(self.func_stack) < 1 else self.func_stack[-1]
				self.instruction_set(self.current_instruction)
				executed += 1
		if self.enable_messages:
			end_time = str(round(time.perf_counter() - starting_time, 5))
			TE.fprint(f'\\n\\\\clc\\Finished in\\clw\\ {end_time} \\n\\\\clc\\Executed instructions\\clw\\ {executed}\\ce\\\\n\\')