import numpy as np
import os, sys


## Integer ##

INT  = np.int16
UINT = np.uint16
INTEGER_BASE_DIGITS = {
	2 : '01',
	8 : '01234567',
	10: '0123456789',
	16: '0123456789abcdef'
}
INTEGER_BASES = {
	'0b': 2,
	'0o': 8,
	'0d': 10,
	'0x': 16
}


## Interpreter ##

INTERPRETER_EXEC_LIMIT = 2**32
INTERPRETER_OPERATION_LIST = {
	'load'   : [1]  ,
	'store'  : [1,2],
	'call'   : [1]  ,
	'return' : [0,1],
	'jump'   : [1]  ,
	'jmpp'   : [1]  ,
	'jmpz'   : [1]  ,
	'jmpn'   : [1]  ,
	'and'    : [1]  ,
	'or'     : [1]  ,
	'xor'    : [1]  ,
	'not'    : [0]  ,
	'lst'    : [1]  ,
	'rst'    : [1]  ,
	'add'    : [1]  ,
	'sub'    : [1]  ,
	'mul'    : [1]  ,
	'div'    : [1]  ,
	'mod'    : [1]  ,
	'sgn'    : [1]  ,
	'abs'    : [1]  ,
	'inc'    : [0]  ,
	'dec'    : [0]  ,
	'cmp'    : [1]  ,
	'strout' : [-1] ,
	'plot'   : [2]  ,
	'update' : [0]  ,
	'sleep'  : [1]  ,
	'cls'    : [0]  ,
	'uo'     : [0]  ,
	'ui'     : [0]  ,
	'halt'   : [0]
}
INTERPRETER_OPERATION_LIST_GROUPED = {
	'memory': [
		'load'  ,
		'store' ,
		'call'  ,
		'return',
		'jump'  ,
		'jmpp'  ,
		'jmpz'  ,
		'jmpn'
	],
	'boolean': [
		'and',
		'or' ,
		'xor',
		'not',
		'lst',
		'rst',
	],
	'math': [
		'add',
		'sub',
		'mul',
		'div',
		'mod',
		'sgn',
		'abs',
		'inc',
		'dec',
		'cmp'
	],
	'special': [
		'strout',
		'sleep' ,
		'uo'    ,
		'ui'    ,
		'halt'
	],
	'display': [
		'update',
		'plot'  ,
		'cls'
	]
}


## Shell ##

SHELL_OPERATION_LIST = {
	'version': [0]  ,
	'discord': [0]  ,
	'exit'   : [0]  ,
	'help'   : [0,1],
	'setil'  : [1]  ,
	'ilim'   : [0]  ,
	'clear'  : [0]  ,
	'create' : [1]  ,
	'edit'   : [1]  ,
	'del'    : [1]  ,
	'run'    : [1]  ,
	'compile': [1]
}
SHELL_OPERATION_LIST_GROUPED = {
	'info': {
		'version': 'Gives current version of the shell',
		'discord': 'Gives link to community discord servers'
	},
	'misc': {
		'exit'   : 'Exits terminal',
		'help'   : 'Shows this list',
		'setil'  : 'Changes instruction limit',
		'ilim'   : 'Shows current instruction limit',
		'clear'  : 'Clears the terminal'
	},
	'file': {
		'create' : 'Creates code file',
		'edit'   : 'Opens default text editor with code file opened',
		'del'    : 'Deletes code file'
	},
	'interpreter': {
		'run'    : 'Executes code',
		'compile': 'Compiles code'
	}
}


## Misc ##

TOKEN_ARG_TYPES = [
	'var',
	'int',
	'str'
]
FILE_EXTENSION = '.txt'
FILE_PATH = ''
if getattr(sys, 'frozen', False):
	FILE_PATH = os.path.dirname(sys.executable) + '\\'
else:
	FILE_PATH = os.path.dirname(os.path.abspath(__file__)) + '\\'