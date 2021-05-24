import random

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
	#assert can_flag(x, y)
	flagged_table ^= 1 << ((y+1)*(grid_width+1)+x+1)

def can_uncover(x,y):
	return	((0 <= x < grid_width) and (0 <= y < grid_height) and
			(covered_table >> ((y+1)*(grid_width+1)+x+1) & 1) and 
			not (flagged_table >> ((y+1)*(grid_width+1)+x+1) & 1))

def uncover(x, y):
	global covered_table,flagged_table, done, won
	#assert can_uncover(x,y)
	#check if mine
	if ismine_table >> ((y+1)*(grid_width+1)+x+1) & 1:
		covered_table ^= ismine_table
		flagged_table &= ~ismine_table
		won = False
		done = True
		return False
		
	covered_table ^= 1 << ((y+1)*(grid_width+1)+x+1)
	#check if won
	if covered_table == ismine_table or flagged_table == ismine_table:
		won = True
		done = True
		return True
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

