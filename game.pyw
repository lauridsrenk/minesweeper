import internal
import os
import pygame

class Settings:
	grid_width = 25
	grid_height = 20
	nof_mines = 60

	fps = 60
	title = "minesweeper"

	tile_width = 20
	tile_height = 20

	@staticmethod
	def get_dim():
		return Settings.grid_width*Settings.tile_width, Settings.grid_height*Settings.tile_height

screen = None 
clock = None 
done = False

file_path = os.path.dirname(os.path.abspath(__file__))
images_path = os.path.join(file_path, "images")

tiles = {}

def init():
	global screen, clock, tiles
	
	pygame.init()
	screen = pygame.display.set_mode(Settings.get_dim())
	clock = pygame.time.Clock()
	pygame.display.set_caption(Settings.title)
	
	tiles["covered"] = pygame.image.load(os.path.join(images_path, "tile_covered.png")).convert_alpha()
	tiles["flagged"] = pygame.image.load(os.path.join(images_path, "tile_flagged.png")).convert_alpha()
	tiles["mine"] = pygame.image.load(os.path.join(images_path, "tile_mine.png")).convert_alpha()
	tiles["uncovered"] = [
		pygame.image.load(os.path.join(images_path, "tile_0.png")).convert_alpha(),
		pygame.image.load(os.path.join(images_path, "tile_1.png")).convert_alpha(),
		pygame.image.load(os.path.join(images_path, "tile_2.png")).convert_alpha(),
		pygame.image.load(os.path.join(images_path, "tile_3.png")).convert_alpha(),
		pygame.image.load(os.path.join(images_path, "tile_4.png")).convert_alpha(),
		pygame.image.load(os.path.join(images_path, "tile_5.png")).convert_alpha(),
		pygame.image.load(os.path.join(images_path, "tile_6.png")).convert_alpha(),
		pygame.image.load(os.path.join(images_path, "tile_7.png")).convert_alpha(),
		pygame.image.load(os.path.join(images_path, "tile_8.png")).convert_alpha(),
	]

def fullquit():
	global done
	done = True
	internal.done = True

def handle_events():
	evs = pygame.event.get()
	for event in evs:
		#Quit on window closed
		if event.type == pygame.QUIT:
			fullquit()

		if event.type == pygame.KEYUP:
			#Quit on Q
			if event.key == pygame.K_q:
				fullquit()
				
		if event.type == pygame.MOUSEBUTTONDOWN:
			x, y = pygame.mouse.get_pos()
			x //= Settings.tile_width
			y //= Settings.tile_height
			if event.button == 1 and internal.can_uncover(x,y):
				internal.uncover(x,y)
			elif event.button == 3 and internal.can_flag(x,y):
				internal.toggle_flag(x,y)
	return len(evs)


def draw():
	for y in range(internal.grid_height):
		for x in range(internal.grid_width):
			field_accessor = ((y+1)*(internal.grid_width+1)+x+1)
			if internal.flagged_table >> field_accessor & 1:
				screen.blit(tiles["flagged"], [x*Settings.tile_width, y*Settings.tile_height])
			elif internal.covered_table >> field_accessor & 1:
				screen.blit(tiles["covered"], [x*Settings.tile_width, y*Settings.tile_height])
			elif internal.ismine_table >> field_accessor & 1:
				screen.blit(tiles["mine"], [x*Settings.tile_width, y*Settings.tile_height])
			else:
				nof_neighbors = (internal.neighbors_map >> ((y*internal.grid_width+x)*4) ) & 15
				screen.blit(tiles["uncovered"][nof_neighbors], [x*Settings.tile_width, y*Settings.tile_height])
			
	pygame.display.flip()

def run():
	while not done:
		internal.init(Settings.grid_width, Settings.grid_height, Settings.nof_mines)
		while not internal.done:
			nof_evs = handle_events()
			if nof_evs: draw() # only update the screen if an event occurred
			clock.tick(Settings.fps)

if __name__ == "__main__":
	init()
	run()
	pygame.quit()