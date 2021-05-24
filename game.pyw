import internal as game
import settings
import os
import pygame

pygame.init()
screensize = [game.grid_width*settings.tile_width, game.grid_height*settings.tile_height]
screen = pygame.display.set_mode(screensize)
clock = pygame.time.Clock()
done = False

pygame.display.set_caption(settings.title)

file_path = os.path.dirname(os.path.abspath(__file__))
images_path = os.path.join(file_path, "images")

tile_covered = pygame.image.load(os.path.join(images_path, "tile_covered.png")).convert_alpha()
tile_flagged = pygame.image.load(os.path.join(images_path, "tile_flagged.png")).convert_alpha()
tile_mine = pygame.image.load(os.path.join(images_path, "tile_mine.png")).convert_alpha()
tiles_uncovered = [
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

def init():
	global screen, clock, tile_covered
	pygame.display.set_caption(settings.title)
	game.init()

def fullquit():
	global done
	done = True

def handle_events():
	for event in pygame.event.get():
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


def draw():
	for y in range(game.grid_width):
		for x in range(game.grid_height):
			field_accessor = ((y+1)*(game.grid_width+1)+x+1)
			if game.flagged_table >> field_accessor & 1:
				screen.blit(tile_flagged, [x*settings.tile_width, y*settings.tile_height])
				continue
			if game.covered_table >> field_accessor & 1:
				screen.blit(tile_covered, [x*settings.tile_width, y*settings.tile_height])
				continue
			if game.ismine_table >> field_accessor & 1:
				screen.blit(tile_mine, [x*settings.tile_width, y*settings.tile_height])
				continue
			nof_neighbors = (game.neighbors_map >> ((y*game.grid_width+x)*4) ) & 15
			screen.blit(tiles_uncovered[nof_neighbors], [x*settings.tile_width, y*settings.tile_height])
			
	pygame.display.flip()

if __name__ == "__main__":
	init()
	while not done:
		handle_events()
		draw()
		clock.tick(settings.fps)