#Handles I/O, adds reset, etc.
import internal
import os
import pygame

class Settings:
	"""
	Static Class
	"""
	grid_width = 9
	grid_height = 9
	nof_mines = 10

	fps = 60
	title = "minesweeper"

	tile_width = 20
	tile_height = 20
	
	header_height = 40
	min_width = 100
	
	x_tile_offset = max((min_width - (grid_width*tile_width)) // 2, 0)
	y_tile_offset = header_height

	@staticmethod
	def get_dim():
		return (
			max(Settings.grid_width*Settings.tile_width, Settings.min_width),
			Settings.grid_height*Settings.tile_height+Settings.header_height
		)
		
	@staticmethod
	def set_easy():
		Settings.grid_width = 9
		Settings.grid_height = 9
		Settings.nof_mines = 10
		Settings.x_tile_offset = max((Settings.min_width - (Settings.grid_width*Settings.tile_width)) // 2, 0)
		Settings.y_tile_offset = Settings.header_height
		
	@staticmethod
	def set_medium():
		Settings.grid_width = 16
		Settings.grid_height = 16
		Settings.nof_mines = 40
		Settings.x_tile_offset = max((Settings.min_width - (Settings.grid_width*Settings.tile_width)) // 2, 0)
		Settings.y_tile_offset = Settings.header_height
		
	@staticmethod
	def set_difficult():
		Settings.grid_width = 30
		Settings.grid_height = 16
		Settings.nof_mines = 99
		Settings.x_tile_offset = max((Settings.min_width - (Settings.grid_width*Settings.tile_width)) // 2, 0)
		Settings.y_tile_offset = Settings.header_height

#Settings.set_easy()
Settings.set_medium()

class Resources:
	def __init__(self, screen_dim):
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
		
		self._background = pygame.image.load(os.path.join(self.images_path, "background.png")).convert()
		self.scale_background(screen_dim)
		
		self.smileys = {}
		self.smileys["happy1"] = pygame.image.load(os.path.join(self.images_path, "smiley000.png")).convert_alpha()
		self.smileys["dead1"] = pygame.image.load(os.path.join(self.images_path, "smiley001.png")).convert_alpha()
		self.smileys["sunglasses1"] = pygame.image.load(os.path.join(self.images_path, "smiley002.png")).convert_alpha()
		self.smileys["happy2"] = pygame.image.load(os.path.join(self.images_path, "smiley010.png")).convert_alpha()
		self.smileys["dead2"] = pygame.image.load(os.path.join(self.images_path, "smiley011.png")).convert_alpha()
		self.smileys["sunglasses2"] = pygame.image.load(os.path.join(self.images_path, "smiley012.png")).convert_alpha()
		
	def scale_background(self, dim):
		self.background = pygame.transform.scale(self._background, dim)
		


class Game_Controller:
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode(Settings.get_dim())
		self.clock = pygame.time.Clock()
		pygame.display.set_caption(Settings.title)
		self.resources = Resources(self.screen.get_size())
		
		self.smiley = Smiley(self.resources)
		self.game_loop = Game_Loop(self, self.screen, self.clock, self.resources, self.smiley)
		self.between_rounds_loop = Between_Rounds_Loop(self, self.screen, self.clock, self.resources, self.smiley)
		self.done = False
			
	def run(self):
		while not self.done:
			self.game_loop.run()
			self.between_rounds_loop.run()


class Game_Loop:
	def __init__(self, controller, screen, clock, resources, smiley):
		self.controller = controller
		self.screen = screen
		self.clock = clock
		self.resources = resources
		self.done = False
		self.resetting = False
		self.smiley = smiley
		
	def fullquit(self):
		self.controller.done = True
		self.done = True
		internal.done = True
		
	def handle_events(self):
		evs = pygame.event.get()
		for event in evs:
			#Quit on window closed
			if event.type == pygame.QUIT:
				self.fullquit()

			elif event.type == pygame.KEYUP:
				#Quit on Q
				if event.key == pygame.K_q:
					self.fullquit()
					
			elif event.type == pygame.MOUSEBUTTONDOWN:
				gx, gy = self.get_grid_pos(pygame.mouse.get_pos())
				mx, my = pygame.mouse.get_pos()
				if event.button == 1 and internal.can_uncover(gx,gy):
					internal.uncover(gx,gy)
				elif event.button == 3 and internal.can_flag(gx,gy):
					internal.toggle_flag(gx,gy)
				elif self.smiley.collidepoint(mx, my):
					self.reset()
		return len(evs)

	def draw(self):
		self.screen.blit(self.resources.background, (0,0))
		self.smiley.draw(self.screen)
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
		self.done = False
		self.smiley.set_new_round()
		while not self.done:
			internal.init(Settings.grid_width, Settings.grid_height, Settings.nof_mines)
			while not internal.done:
				nof_evs = self.handle_events()
				if nof_evs: self.draw() # only update the screen if an event occurred
				self.clock.tick(Settings.fps)
				
			if self.resetting:
				self.resetting = False
				continue
				
			if internal.won:
				self.smiley.set_won()
			else:
				self.smiley.set_lost()
			self.done = True

	def get_grid_pos(self, pos = [0,0]):
		"""
		get the relative position of a mouse coordinate on the grid
		"""
		return (pos[0] - Settings.x_tile_offset) // Settings.tile_width, (pos[1] - Settings.y_tile_offset) // Settings.tile_height

	def reset(self):
		internal.done = True
		self.resetting = True


class Between_Rounds_Loop:
	def __init__(self, controller, screen, clock, resources, smiley):
		self.controller = controller
		self.screen = screen
		self.clock = clock
		self.resources = resources
		self.done = False
		self.smiley = smiley
		
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
					
			if event.type == pygame.MOUSEBUTTONDOWN:
				mx, my = pygame.mouse.get_pos()
				if self.smiley.collidepoint(mx, my):
					self.done = True
		return len(evs)

	def draw(self):
		self.smiley.draw(self.screen)
		pygame.display.flip()

	def run(self):
		self.done = self.controller.done
		while not self.done:
			self.draw()
			self.handle_events()
			self.clock.tick(Settings.fps)


class Smiley(pygame.sprite.Sprite):
	def __init__(self, resources):
			self.image = resources.smileys["happy1"]
			self.images = [
				[resources.smileys["happy2"],resources.smileys["happy1"],],
				[resources.smileys["dead2"],resources.smileys["dead1"],],
				[resources.smileys["sunglasses2"],resources.smileys["sunglasses1"],],
			]
			self.rect = self.image.get_rect()
			width,height = Settings.get_dim()
			self.rect.move_ip((width - self.rect.width) // 2, (Settings.header_height - self.rect.height) // 2)
			self.status = 0 #0: new round, 1: lost, 2: won
			
	def collidepoint(self, x, y):
		return self.rect.collidepoint(x,y)

	def draw(self, screen):
		mouse_x, mouse_y = pygame.mouse.get_pos()
		hovering = 0
		if self.collidepoint(mouse_x, mouse_y): hovering = 1
		screen.blit(self.images[self.status][hovering], self.rect)
			
	def set_won(self):
		self.status = 2
	
	def set_lost(self):
		self.status = 1
		
	def set_new_round(self):
		self.status = 0


if __name__ == "__main__":
	game_controller = Game_Controller()
	game_controller.run()
	pygame.quit()