import global_variables as GV
import code_run as CR
import text_engine as TE
import os


################################
# global variables
################################

FILE_PATH = GV.FILE_PATH
FILE_EXTENSION = GV.FILE_EXTENSION
SHELL_OPERATION_LIST = GV.SHELL_OPERATION_LIST
SHELL_OPERATION_LIST_GROUPED = GV.SHELL_OPERATION_LIST_GROUPED
INTERPRETER_OPERATION_LIST = GV.INTERPRETER_OPERATION_LIST


################################
# Shell
################################

class shell:
	def __init__(self):
		self.lexer   = CR.lexer(SHELL_OPERATION_LIST)
		self.program = CR.interpreter()
		self.program.enable_messages = False
		self.program.instruction_set = self.instruction_set

	# Executes code

	def execute(self, code):
		self.lexer.import_commands(code)
		try:
			self.program.group_token_list(self.lexer)
			self.program.execute()
		except Exception as e:		#not good
			print(e)

	# Help instruction, just prints descriptions of other instructions

	def help_(self, arg=None):
		if arg == 'me':
			TE.fprint(f'\\t\\\\clc\\Just type command name, or ask question on discord server\\ce\\\\n\\')
			return
		if arg != None:
			for category in SHELL_OPERATION_LIST_GROUPED:
				if SHELL_OPERATION_LIST_GROUPED[category].get(arg):
					description = SHELL_OPERATION_LIST_GROUPED[category][arg]
					TE.fprint(f'\\cg\\{arg} -\\clg\\ {description}\\ce\\\\n\\')
					return
			TE.fprint(f'\\clr\\unknows instruction \'{arg}\'\\ce\\\\n\\')
			return
		for category in SHELL_OPERATION_LIST_GROUPED:
			TE.fprint(f'\\clc\\[{category}]\\ce\\\\n\\')
			for command in SHELL_OPERATION_LIST_GROUPED[category]:
				description = SHELL_OPERATION_LIST_GROUPED[category][command]
				TE.fprint(f'\\t\\\\cg\\{command} -\\clg\\ {description}\\n\\')
		TE.fprint('\\ce\\')

	# Instruciton set, describes what each instruciton do

	def instruction_set(self, instruction):
		op, args = instruction['op'], instruction['args']

		if op in SHELL_OPERATION_LIST_GROUPED['misc']:
			if op == 'exit':
				raise SystemExit
			elif op == 'help':
				if len(args) > 0:
					self.help_(args[0].value)
				else:
					self.help_()
			elif op == 'setil':
				if (var := self.program.get_value(args[0])) == 0:
					CR.INTERPRETER_EXEC_LIMIT = 2**64
				else:
					CR.INTERPRETER_EXEC_LIMIT = var
			elif op == 'ilim':
				print('Current instruction limit is '+str(CR.INTERPRETER_EXEC_LIMIT))
			elif op == 'clear':
				command = 'cls' if os.name in ['nt', 'dos'] else 'clear'
				os.system(command)
		elif op in SHELL_OPERATION_LIST_GROUPED['file']:
			if args[0].type != 'str':
				self.program.raise_dtype_error(args[0])

			if op == 'create':
				if os.path.isfile(FILE_PATH+args[0].value+FILE_EXTENSION):
					raise Exception(f'file \'{args[0].value}{FILE_EXTENSION}\' already does exit')
				print('File created at: '+FILE_PATH+args[0].value+FILE_EXTENSION)
				open(FILE_PATH+args[0].value+FILE_EXTENSION, 'w').close()
			elif op == 'edit':
				if os.path.isfile(FILE_PATH+args[0].value+FILE_EXTENSION):
					os.startfile(FILE_PATH+args[0].value+FILE_EXTENSION)
				else:
					raise FileNotFoundError(f'file \'{args[0].value}{FILE_EXTENSION}\' doesn\'t exist')
			elif op == 'del':
				if os.path.isfile(FILE_PATH+args[0].value+FILE_EXTENSION):
					print('File deleted from: '+FILE_PATH+args[0].value+FILE_EXTENSION)
					os.remove(FILE_PATH+args[0].value+FILE_EXTENSION)
				else:
					raise FileNotFoundError(f'file \'{args[0].value}{FILE_EXTENSION}\' doesn\'t exist')
		elif op in SHELL_OPERATION_LIST_GROUPED['interpreter']:
			if args[0].type != 'str':
				self.program.raise_dtype_error(args[0])

			if op == 'run':
				if os.path.isfile(FILE_PATH+args[0].value+FILE_EXTENSION):
					with open(FILE_PATH+args[0].value+FILE_EXTENSION, 'r') as code:
						lexer = CR.lexer(INTERPRETER_OPERATION_LIST)
						lexer.import_commands(code.read())
						program = CR.interpreter()
						try:
							program.group_token_list(lexer)
							program.execute()
						except Exception as e:		#not good
							print(e)
				else:
					raise FileNotFoundError(f'file \'{args[0].value}{FILE_EXTENSION}\' doesn\'t exist')
			elif op == 'compile':
				pass
		elif op in SHELL_OPERATION_LIST_GROUPED['info']:
			if op == 'version':
				TE.fprint('Current version of the shell is \\clw\\4.0.0\\ce\\\\n\\')
			elif op == 'discord':
				TE.fprint('English comunity \\clw\\https://discord.gg/VXzcE9jKCy\\ce\\\\n\\')
				TE.fprint('Russian comunity \\clw\\https://discord.gg/VUNynpQW5v\\ce\\\\n\\')
				TE.fprint('Creator\'s discord \\clw\\Qbik#3628\\ce\\\\n\\')



# Executes given code

def execute(code):
	shell().execute(code)


def main():
	while True:
		execute(input('>>> '))

if __name__ == '__main__':
	main()