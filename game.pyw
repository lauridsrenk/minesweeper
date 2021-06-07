import internal
import os
import pygame

class Settings:
	"""
	Static Class
	"""
	grid_width = 25
	grid_height = 20
	nof_mines = 60

	fps = 60
	title = "minesweeper"
	font = "Arial"
	fontsize = 32
	fontcolor = (255,255,255)

	tile_width = 20
	tile_height = 20
	
	header_height = 80
	min_width = 60
	
	x_tile_offset = max((min_width - grid_width*tile_width) // 2, 0)
	y_tile_offset = header_height

	@staticmethod
	def get_dim():
		return (
			max(Settings.grid_width*Settings.tile_width, Settings.min_width),
			Settings.grid_height*Settings.tile_height+Settings.header_height
		)


class Resources:
	def __init__(self):
		self.file_path = os.path.dirname(os.path.abspath(__file__))
		self.images_path = os.path.join(self.file_path, "images")
		
		self.tiles = {}
		self.tiles["covered"] = pygame.image.load(os.path.join(self.images_path, "tile_covered.png")).convert_alpha()
		self.tiles["flagged"] = pygame.image.load(os.path.join(self.images_path, "tile_flagged.png")).convert_alpha()
		self.tiles["mine"] = pygame.image.load(os.path.join(self.images_path, "tile_mine.png")).convert_alpha()
		self.tiles["uncovered"] = [
			pygame.image.load(os.path.join(self.images_path, "tile_0.png")).convert_alpha(),
			pygame.image.load(os.path.join(self.images_path, "tile_1.png")).convert_alpha(),
			pygame.image.load(os.path.join(self.images_path, "tile_2.png")).convert_alpha(),
			pygame.image.load(os.path.join(self.images_path, "tile_3.png")).convert_alpha(),
			pygame.image.load(os.path.join(self.images_path, "tile_4.png")).convert_alpha(),
			pygame.image.load(os.path.join(self.images_path, "tile_5.png")).convert_alpha(),
			pygame.image.load(os.path.join(self.images_path, "tile_6.png")).convert_alpha(),
			pygame.image.load(os.path.join(self.images_path, "tile_7.png")).convert_alpha(),
			pygame.image.load(os.path.join(self.images_path, "tile_8.png")).convert_alpha(),
		]
		
		self.background = pygame.image.load(os.path.join(self.images_path, "background.png")).convert()
		self.background = pygame.transform.scale(self.background, Settings.get_dim())
		
		self.font = pygame.font.SysFont(Settings.font, Settings.fontsize)


class Game_Controller:
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode(Settings.get_dim())
		self.clock = pygame.time.Clock()
		pygame.display.set_caption(Settings.title)
		self.resources = Resources()
		self.game_loop = Game_Loop(self, self.screen, self.clock, self.resources)
		self.between_rounds_loop = Between_Rounds_Loop(self, self.screen, self.clock, self.resources)
		self.done = False
	
	def run(self):
		while not self.done:
			self.game_loop.run()
			self.between_rounds_loop.run()


class Game_Loop:
	def __init__(self, controller, screen, clock, resources):
		self.controller = controller
		self.screen = screen
		self.clock = clock
		self.resources = resources
		
	def fullquit(self):
		self.controller.done = True
		internal.done = True
		
	def handle_events(self):
		evs = pygame.event.get()
		for event in evs:
			#Quit on window closed
			if event.type == pygame.QUIT:
				self.fullquit()

			if event.type == pygame.KEYUP:
				#Quit on Q
				if event.key == pygame.K_q:
					self.fullquit()
					
			if event.type == pygame.MOUSEBUTTONDOWN:
				x, y = self.get_grid_pos(pygame.mouse.get_pos())
				if event.button == 1 and internal.can_uncover(x,y):
					internal.uncover(x,y)
				elif event.button == 3 and internal.can_flag(x,y):
					internal.toggle_flag(x,y)
		return len(evs)

	def draw(self):
		self.screen.blit(self.resources.background, (0,0))
		for y in range(internal.grid_height):
			for x in range(internal.grid_width):
				field_accessor = ((y+1)*(internal.grid_width+1)+x+1)
				tile_coordinates = [
					x*Settings.tile_width + Settings.x_tile_offset,
					y*Settings.tile_height + Settings.y_tile_offset
				]
				if internal.flagged_table >> field_accessor & 1:# if field is flagged
					self.screen.blit(self.resources.tiles["flagged"], tile_coordinates)
				elif internal.covered_table >> field_accessor & 1:# if field is covered
					self.screen.blit(self.resources.tiles["covered"], tile_coordinates)
				elif internal.ismine_table >> field_accessor & 1:# if field is mine
					self.screen.blit(self.resources.tiles["mine"], tile_coordinates)
				else:# display n_of neighboring mines
					nof_neighbors = (internal.neighbors_map >> ((y*internal.grid_width+x)*4) ) & 15
					self.screen.blit(self.resources.tiles["uncovered"][nof_neighbors], tile_coordinates)
				
		pygame.display.flip()

	def run(self):
		internal.init(Settings.grid_width, Settings.grid_height, Settings.nof_mines)
		while not internal.done:
			nof_evs = self.handle_events()
			if nof_evs: self.draw() # only update the screen if an event occurred
			self.clock.tick(Settings.fps)

	def get_grid_pos(self, pos = [0,0]):
		"""
		get the relative position of a mouse coordinate on the grid
		"""
		return (pos[0] - Settings.x_tile_offset) // Settings.tile_width, (pos[1] - Settings.y_tile_offset) // Settings.tile_height


class Between_Rounds_Loop:
	def __init__(self, controller, screen, clock, resources):
		self.controller = controller
		self.screen = screen
		self.clock = clock
		self.resources = resources
		self.done = False
		
		self.text = self.resources.font.render("New Round? [y/n]", True, Settings.fontcolor)
		screen_width, screen_height = Settings.get_dim()
		self.text_pos = (screen_width - self.text.get_rect().width) // 2, (screen_height - self.text.get_rect().height) // 2
		
	def fullquit(self):
		self.controller.done = True
		self.done = True
		
	def handle_events(self):
		evs = pygame.event.get()
		for event in evs:
			#Quit on window closed
			if event.type == pygame.QUIT:
				self.fullquit()

			if event.type == pygame.KEYUP:
				#Quit on Q
				if event.key == pygame.K_q:
					self.fullquit()
					
				if event.key == pygame.K_y:
					self.controller.done = False
					self.done = True
				if event.key == pygame.K_n:
					self.controller.done = True
					self.done = True
		return len(evs)

	def draw(self):
		self.screen.blit(self.text, self.text_pos)
		pygame.display.flip()

	def run(self):
		self.done = self.controller.done
		self.draw()
		while not self.done:
			self.handle_events()
			self.clock.tick(Settings.fps)


if __name__ == "__main__":
	game_controller = Game_Controller()
	game_controller.run()
	pygame.quit()