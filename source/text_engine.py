import os

os.system('')		#init


text_color = {
	'red'           : '\033[31m',
	'green'         : '\033[32m',
	'blue'          : '\033[34m',
	'yellow'        : '\033[33m',
	'cyan'          : '\033[36m',
	'magenta'       : '\033[35m',

	'light_red'     : '\033[91m',
	'light_green'   : '\033[92m',
	'light_blue'    : '\033[94m',
	'light_yellow'  : '\033[93m',
	'light_cyan'    : '\033[96m',
	'light_magenta' : '\033[95m',

	'light_white'   : '\033[97m',
	'white'         : '\033[37m',
	'light_black'   : '\033[90m',
	'black'         : '\033[30m',

	'reset'         : '\033[39m'
}
on_color = {
	'red'           : '\033[41m',
	'green'         : '\033[42m',
	'blue'          : '\033[44m',
	'yellow'        : '\033[43m',
	'cyan'          : '\033[46m',
	'magenta'       : '\033[45m',

	'light_red'     : '\033[101m',
	'light_green'   : '\033[102m',
	'light_blue'    : '\033[104m',
	'light_yellow'  : '\033[103m',
	'light_cyan'    : '\033[106m',
	'light_magenta' : '\033[105m',

	'light_white'   : '\033[107m',
	'white'         : '\033[47m',
	'light_black'   : '\033[100m',
	'black'         : '\033[40m',

	'reset'         : '\033[49m'
}
attrs = {
	'bold'          : '\033[1m',
	'underline'     : '\033[4m',
	'reverse'       : '\033[7m',

	'reset_all'     : '\033[0m'
}
short_names = {
	'r': 'red',
	'g': 'green',
	'b': 'blue',
	'y': 'yellow',
	'c': 'cyan',
	'm': 'magenta',
	'w': 'white',
	'k': 'black'
}

# Applies command to the text
# Returns modified text
def apply_command(command, text):
	if len(command) < 1:
		return text

	prefix = command[0]
	data   = command[1:]

	if prefix == 'n':
		text += '\n'
	elif prefix == 't':
		text += '\t'
	elif prefix == 's':
		text += '\\'
	elif prefix == 'r':
		command = 'cls' if os.name in ['nt', 'dos'] else 'clear'
		os.system(command)
	elif prefix == 'c':
		color, background = '', False
		for char in data:
			if char == 'l':
				color = 'light_'
			elif char == 'e':
				color = 'reset'
			elif char == 'd':
				background = True
			elif char in short_names:
				color += short_names[char]
		text += on_color.get(color, '') if background else text_color.get(color, '')
	else:
		text += command

	return text

# Fancy print function
def fprint(text):
	if type(text) != str:
		print(text, end='')
		return
	elif text.find('\\') < 0:
		print(text, end='')
		return

	command, is_command = '', False
	final = ''
	for char in text:
		if char == '\\':
			if is_command:
				final = apply_command(command, final)
				command, is_command = '', False
			else:
				is_command = True
		else:
			if is_command:
				command += char
			else:
				final += char
	print(final, end='')


class display:
	def __init__(self, width, height):
		self.width = width
		self.height = height

		self.matrix = [('  ' * width) for _ in range(height)]

	def in_bounds(self, x,y):
		if self.width > x > -1 and self.height > y > -1:
			return True
		return False

	def plot(self, x, y):
		if self.in_bounds(x,y):
			self.matrix[y] = self.matrix[y][0:x*2] + '██' + self.matrix[y][x*2+2:]

	def clear(self):
		self.matrix = [('  ' * self.width) for _ in range(self.height)]

	def update(self):
		screen = ''
		for row in self.matrix:
			screen += row + '\n'
		print(screen, end='')

	def __str__(self):
		return f'display - {self.width}x{self.height}'

	def __repr__(self):
		return f'{self.width}x{self.height}'