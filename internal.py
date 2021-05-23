import random
import math

#default settings
grid_width = 9
grid_height = 9
nof_mines = 10

covered_table = 0	# stores which fields are still covered 
flagged_table = 0	# stores which fields are flagged 
ismine_table = 0	# stores wich fields are mines
# A table is (grid_height+1)*(grid_width+1) bits large.
# each (grid_width + 1) bits represents a row of fields.
# the first row is unused (0).
# the first bit of each row is unused.
# this makes calculations regarding neighboring fields easier.
# a single field can be accessed with: "table >> ((y+1)*(grid_width+1)+x+1) & 1"

neighbors_map = 0 # uses 4 bits each to store how many of the neighboring fields are mines
# a single field can be accessed with: "map >> ((y*grid_width+x)*4) & 15"
done = False
won = False


def init():
	global covered_table, flagged_table, ismine_table, neighbors_map, done, won
	_row_covered = 0
	for i in range(0, grid_height):
		covered_table |= ((1 << (grid_width + 1)) - 2)
		covered_table <<= (grid_width + 1)
	flagged_table = 0
	ismine_table = 0
	done = False

	#spread mines
	def choose_field():
		return [random.randrange(grid_width), random.randrange(grid_height)]
	
	for i in range(0, nof_mines):
		x,y = choose_field()
		while ismine_table >> ((y+1)*(grid_width+1)+x+1) & 1:
			x,y = choose_field()
		ismine_table |= (1 << ((y+1)*(grid_width+1)+x+1) )
		
	#update neighbors map
	for y in range(0, grid_height):
		for x in range(0, grid_width):
			nof_neighbors = 0
			nof_neighbors += (ismine_table >> ((y+1)*(grid_width+1)+x+2) ) & 1	# left
			nof_neighbors += ismine_table >> ((y+1)*(grid_width+1)+x) & 1		# right
			nof_neighbors += ismine_table >> ((y+2)*(grid_width+1)+x+1) & 1		# top
			nof_neighbors += ismine_table >> ((y)*(grid_width+1)+x+1) & 1		# bottom
			nof_neighbors += ismine_table >> ((y+2)*(grid_width+1)+x+2) & 1		# top left
			nof_neighbors += ismine_table >> ((y+2)*(grid_width+1)+x) & 1		# top right
			nof_neighbors += ismine_table >> ((y)*(grid_width+1)+x+2) & 1		# bottom left
			nof_neighbors += ismine_table >> ((y)*(grid_width+1)+x) & 1			# bottom right
			
			neighbors_map |= nof_neighbors << ((y*grid_width+x)*4)

def can_flag(x, y):
	return	((0 <= x < grid_width) and (0 <= y < grid_height) and 
			(covered_table >> ((y+1)*(grid_width+1)+x+1) & 1))

def toggle_flag(x, y):
	global flagged_table
	assert can_flag(x, y)
	flagged_table ^= 1 << ((y+1)*(grid_width+1)+x+1)

def can_uncover(x,y):
	return	((0 <= x < grid_width) and (0 <= y < grid_height) and
			(covered_table >> ((y+1)*(grid_width+1)+x+1) & 1) and 
			not (flagged_table >> ((y+1)*(grid_width+1)+x+1) & 1))

def uncover(x, y):
	global covered_table, done, won
	assert can_uncover(x,y)
	covered_table ^= 1 << ((y+1)*(grid_width+1)+x+1)
	#check if mine
	if ismine_table >> ((y+1)*(grid_width+1)+x+1) & 1:
		won = False
		done = True
		print(x,y)
		return False
	#uncover safe fields algorithm
	if (neighbors_map >> ((y*grid_width+x)*4) & 15) == 0:
		if can_uncover(x, y-1): uncover(x,y-1)		# top
		if can_uncover(x, y+1): uncover(x,y+1)		# bottom
		if can_uncover(x-1, y): uncover(x-1,y)		# right
		if can_uncover(x+1, y): uncover(x+1,y)		# left
		if can_uncover(x-1, y-1): uncover(x-1,y-1)	# top right
		if can_uncover(x+1, y-1): uncover(x+1,y-1)	# top left
		if can_uncover(x-1, y+1): uncover(x-1,y+1)	# bottom right
		if can_uncover(x+1, y+1): uncover(x+1,y+1)	# bottom left
	
def run_on_console():
	def print_to_console():
		def choose_symbol(x,y):
			field_accessor = ((y+1)*(grid_width+1)+x+1)
			if flagged_table >> field_accessor & 1: return "F "
			if covered_table >> field_accessor & 1: return "\u2588 "
			if ismine_table >> field_accessor & 1: return "M "
			nof_neighbors = (neighbors_map >> ((y*grid_width+x)*4) ) & 15
			if nof_neighbors: return str(nof_neighbors)+" "
			return "  "
		
		#x coordinates
		print("   ",end="")
		for i in range(grid_width):
			n = str(i)
			n = " "*(2-len(n))+n
			print(n,end="  ")
		#0th row
		print("\n  +" + "---+"*grid_width)
		for y in range(0, grid_height):
			#y coordinates
			n = str(y)
			n = " "*(2-len(n))+n
			print(n+"| ", end="")
			#field
			for x in range(0, grid_width):
				print(choose_symbol(x,y), end="| ")
			#row
			print("\n  +" + "---+"*grid_width)

	def read_from_console():
		def is_int(I):
			try:
				int(I)
				return True
			except ValueError:
				return False
		
		i = input("x y [f]: ").split(" ")
		#error checking
		if len(i) < 2:
			print("zu wenige Argumente")
			return False
		if len(i) >= 4:
			print("zu viele Argumente")
			return False
		if not is_int(i[0]):
			print("x ist kein Integer")
			return False
		if not is_int(i[1]):
			print("y ist kein Integer")
			return False
			
		x = int(i[0])
		y = int(i[1])
		
		#more error checking
		if x < 0:
			print("x ist negativ")
			return False
		if x >= grid_width:
			print("x ist zu groß")
			return False
		if y < 0:
			print("y ist negativ")
			return False
		if y >= grid_width:
			print("y ist zu groß")
			return False
		
		#flagging
		if len(i) == 3:
			if can_flag(x, y):
				toggle_flag(x, y)
				return True
			else:
				print(f"kann {x} {y} nicht markieren")
				return False
		
		#uncovering
		if can_uncover(x,y):
			uncover(x, y)
			return True
		else:
			print(f"kann {x} {y} nicht aufgedecken")
			return False

	init()
	while not done:
		print_to_console()
		successfull_read = read_from_console()
		while not successfull_read:
			successfull_read = read_from_console()
	if won:
		print_to_console()
		print("gewonnen :)")
	else:
		print_to_console()
		print("verloren :(")
if __name__ == "__main__":
	run_on_console()