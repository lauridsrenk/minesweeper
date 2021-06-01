import internal

class Settings:
	grid_width = 9
	grid_height = 9
	nof_mines = 10

def print_to_console():
	def choose_symbol(x,y):
		field_accessor = ((y+1)*(internal.grid_width+1)+x+1)
		if internal.flagged_table >> field_accessor & 1: return " F "
		if internal.covered_table >> field_accessor & 1: return " \u2588 "
		if internal.ismine_table >> field_accessor & 1: return " M "
		nof_neighbors = (internal.neighbors_map >> ((y*internal.grid_width+x)*4) ) & 15
		if nof_neighbors: return f" {str(nof_neighbors)} "
		return "   "
	
	#x coordinates
	print("   ",end="")
	for i in range(internal.grid_width):
		n = str(i)
		n = " "*(2-len(n))+n
		print(n,end="  ")
	#0th row
	print("\n  +" + "---+"*internal.grid_width)
	for y in range(0, internal.grid_height):
		#y coordinates
		n = str(y)
		n = " "*(2-len(n))+n
		print(n, end="|")
		#field
		for x in range(0, internal.grid_width):
			print(choose_symbol(x,y), end="|")
		#row
		print("\n  +" + "---+"*internal.grid_width)

def read_from_console():
	i = input("x y [f]: ").split(" ")
	#error checking
	if len(i) < 2:
		print("zu wenige Argumente")
		return False
	if len(i) >= 4:
		print("zu viele Argumente")
		return False
	try:
		x = int(i[0])
	except ValueError:
		print("x ist kein Integer")
		return False
	try:
		y = int(i[1])
	except ValueError:
		print("y ist kein Integer")
		return False
	if x < 0:
		print("x ist negativ")
		return False
	if x >= internal.grid_width:
		print("x ist zu groß")
		return False
	if y < 0:
		print("y ist negativ")
		return False
	if y >= internal.grid_width:
		print("y ist zu groß")
		return False
	
	#flagging
	if len(i) == 3:
		if internal.can_flag(x, y):
			internal.toggle_flag(x, y)
			return True
		else:
			print(f"kann {x} {y} nicht markieren")
			return False
	
	#uncovering
	if internal.can_uncover(x,y):
		internal.uncover(x, y)
		return True
	else:
		print(f"kann {x} {y} nicht aufgedecken")
		return False

if __name__ == "__main__":
	internal.init(Settings.grid_width, Settings.grid_height, Settings.nof_mines)
	while not internal.done:
		print_to_console()
		successfull_read = read_from_console()
		while not successfull_read:
			successfull_read = read_from_console()
	if internal.won:
		print_to_console()
		print("gewonnen :)")
	else:
		print_to_console()
		print("verloren :(")

