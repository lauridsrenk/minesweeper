import internal as game
import settings
import os
import pygame

screen = None 
clock = None 
done = False

file_path = os.path.dirname(os.path.abspath(__file__))
images_path = os.path.join(file_path, "images")

tiles = {}

def init():
	global screen, clock, tiles
	
	pygame.init()
	screen = pygame.display.set_mode(settings.get_dim())
	clock = pygame.time.Clock()
	pygame.display.set_caption(settings.title)
	
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
	game.done = True

def handle_events():
	evs = pygame.event.get()
	for event in evs:
		#Quit on window closed
		if event.type == pygame.QUIT:
			fullquit()

		if event.type == pygame.KEYUP:
			#"Quit on Q
			if event.key == pygame.K_q:
				fullquit()
				
		if event.type == pygame.MOUSEBUTTONDOWN:
			x, y = pygame.mouse.get_pos()
			x //= settings.tile_width
			y //= settings.tile_height
			if event.button == 1 and game.can_uncover(x,y):
				game.uncover(x,y)
			elif event.button == 3 and game.can_flag(x,y):
				game.toggle_flag(x,y)
	return len(evs)


def draw():
	for y in range(game.grid_height):
		for x in range(game.grid_width):
			field_accessor = ((y+1)*(game.grid_width+1)+x+1)
			if game.flagged_table >> field_accessor & 1:
				screen.blit(tiles["flagged"], [x*settings.tile_width, y*settings.tile_height])
				continue
			if game.covered_table >> field_accessor & 1:
				screen.blit(tiles["covered"], [x*settings.tile_width, y*settings.tile_height])
				continue
			if game.ismine_table >> field_accessor & 1:
				screen.blit(tiles["mine"], [x*settings.tile_width, y*settings.tile_height])
				continue
			nof_neighbors = (game.neighbors_map >> ((y*game.grid_width+x)*4) ) & 15
			screen.blit(tiles["uncovered"][nof_neighbors], [x*settings.tile_width, y*settings.tile_height])
			
	pygame.display.flip()

def run():
	while not done:
		game.init(settings.grid_width, settings.grid_height, settings.nof_mines)
		while not game.done:
			nof_evs = handle_events()
			if nof_evs: draw() # only update the screen if an event occurred
			clock.tick(settings.fps)

if __name__ == "__main__":
	init()
	run()
	pygame.quit()