import internal as game

def print_to_console():
	def choose_symbol(x,y):
		field_accessor = ((y+1)*(game.grid_width+1)+x+1)
		if game.flagged_table >> field_accessor & 1: return "F "
		if game.covered_table >> field_accessor & 1: return "\u2588 "
		if game.ismine_table >> field_accessor & 1: return "M "
		nof_neighbors = (game.neighbors_map >> ((y*game.grid_width+x)*4) ) & 15
		if nof_neighbors: return str(nof_neighbors)+" "
		return "  "
	
	#x coordinates
	print("   ",end="")
	for i in range(game.grid_width):
		n = str(i)
		n = " "*(2-len(n))+n
		print(n,end="  ")
	#0th row
	print("\n  +" + "---+"*game.grid_width)
	for y in range(0, game.grid_height):
		#y coordinates
		n = str(y)
		n = " "*(2-len(n))+n
		print(n+"| ", end="")
		#field
		for x in range(0, game.grid_width):
			print(choose_symbol(x,y), end="| ")
		#row
		print("\n  +" + "---+"*game.grid_width)

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
	
	#more error checking
	if x < 0:
		print("x ist negativ")
		return False
	if x >= game.grid_width:
		print("x ist zu groß")
		return False
	if y < 0:
		print("y ist negativ")
		return False
	if y >= game.grid_width:
		print("y ist zu groß")
		return False
	
	#flagging
	if len(i) == 3:
		if game.can_flag(x, y):
			game.toggle_flag(x, y)
			return True
		else:
			print(f"kann {x} {y} nicht markieren")
			return False
	
	#uncovering
	if game.can_uncover(x,y):
		game.uncover(x, y)
		return True
	else:
		print(f"kann {x} {y} nicht aufgedecken")
		return False

if __name__ == "__main__":
	game.init()
	while not game.done:
		print_to_console()
		successfull_read = read_from_console()
		while not successfull_read:
			successfull_read = read_from_console()
	if game.won:
		print_to_console()
		print("gewonnen :)")
	else:
		print_to_console()
		print("verloren :(")