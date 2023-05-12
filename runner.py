import pygame
from sys import exit
from random import randint, choice
import pygame.mask, pygame.mixer

jump_debounce = True
double_jump_debounce = True
secret_active = False
game_active = False
start_time = 0
current_score = -1
secret_start_time = 0

class Shiba(pygame.sprite.Sprite):
	''' Shiba sprite with frames for running and jumping '''
	def __init__(self) -> None:
		''' Initializes sprite class, imports frames, sets animation index, and creates gravity for sprite '''
		super().__init__()

		# Importing frames for running animation
		shiba_running1 = pygame.image.load('assets/graphics/shiba/running/running_1.png').convert_alpha()
		shiba_running1 = pygame.transform.scale2x(shiba_running1)
		shiba_running2 = pygame.image.load('assets/graphics/shiba/running/running_2.png').convert_alpha()
		shiba_running2 = pygame.transform.scale2x(shiba_running2)
		shiba_running3 = pygame.image.load('assets/graphics/shiba/running/running_3.png').convert_alpha()
		shiba_running3 = pygame.transform.scale2x(shiba_running3)
		shiba_running4 = pygame.image.load('assets/graphics/shiba/running/running_4.png').convert_alpha()
		shiba_running4 = pygame.transform.scale2x(shiba_running4)
		shiba_running5 = pygame.image.load('assets/graphics/shiba/running/running_5.png').convert_alpha()
		shiba_running5 = pygame.transform.scale2x(shiba_running5)
		self.shiba_running = [shiba_running1, shiba_running2, shiba_running3, shiba_running4, shiba_running5]
		self.shiba_running_index = 0

		# Importing frames for jumping animation
		shiba_jumping1 = pygame.image.load('assets/graphics/shiba/jumping/jumping_1.png').convert_alpha()
		shiba_jumping1 = pygame.transform.scale2x(shiba_jumping1)
		shiba_jumping2 = pygame.image.load('assets/graphics/shiba/jumping/jumping_2.png').convert_alpha()
		shiba_jumping2 = pygame.transform.scale2x(shiba_jumping2)
		shiba_jumping3 = pygame.image.load('assets/graphics/shiba/jumping/jumping_3.png').convert_alpha()
		shiba_jumping3 = pygame.transform.scale2x(shiba_jumping3)
		shiba_jumping4 = pygame.image.load('assets/graphics/shiba/jumping/jumping_4.png').convert_alpha()
		shiba_jumping4 = pygame.transform.scale2x(shiba_jumping4)
		shiba_jumping5 = pygame.image.load('assets/graphics/shiba/jumping/jumping_5.png').convert_alpha()
		shiba_jumping5 = pygame.transform.scale2x(shiba_jumping5)
		self.shiba_jumping = [shiba_jumping1, shiba_jumping2, shiba_jumping3, shiba_jumping4, shiba_jumping5]
		self.shiba_jumping_index = 0

		self.image = self.shiba_running[self.shiba_running_index]
		self.rect = self.image.get_rect(bottomleft = (80, 300))
		self.gravity = 0

		self.mask = pygame.mask.from_surface(self.image)
	
	def player_input(self) -> None:
		''' Checks if player presses the spacebar and changes shiba sprite gravity if they did '''
		global jump_debounce, double_jump_debounce, start_time
		current_time = pygame.time.get_ticks() - start_time
		keys = pygame.key.get_pressed()
		if keys[pygame.K_SPACE] and self.rect.bottom >= 300 and jump_debounce:
			self.gravity = -17
			jump_debounce = False
			start_time = pygame.time.get_ticks()
		elif self.rect.bottom >= 300 and not jump_debounce and current_time >= 250:
			jump_debounce = True
		elif keys[pygame.K_SPACE] and not jump_debounce and double_jump_debounce and current_time >= 250:
			self.gravity = -15
			self.shiba_jumping_index = 0
			double_jump_debounce = False
		elif jump_debounce:
			double_jump_debounce = True

		# Mask update
		self.mask = pygame.mask.from_surface(self.image)
	
	def apply_gravity(self) -> None:
		''' Applies a constant force of gravity to shiba sprite by adding gravity to y-values '''
		self.gravity += 1
		self.rect.y += self.gravity
		if self.rect.bottom >= 300:
			self.rect.bottom = 300
	
	def animation_player(self) -> None:
		''' Picks animation to play by checking if shiba sprite is in jumping state '''
		if not jump_debounce:
			self.shiba_jumping_index += 0.15
			if self.shiba_jumping_index >= len(self.shiba_jumping): self.shiba_jumping_index = 0
			self.image = self.shiba_jumping[int(self.shiba_jumping_index)]
		else:
			self.shiba_jumping_index = 0
			self.shiba_running_index += 0.3
			if self.shiba_running_index >= len(self.shiba_running): self.shiba_running_index = 0
			self.image = self.shiba_running[int(self.shiba_running_index)]
		
	def update(self) -> None:
		''' Calls necessary function for simulating movement and player_input on shiba sprite '''
		self.player_input()
		self.apply_gravity()
		self.animation_player()

class Hands(pygame.sprite.Sprite):
	''' Obstacle sprites represented by hands to pet shiba '''
	def __init__(self, type) -> None:
		''' Initializes sprite class, picks hand type to generate, and randomly sets x-position '''
		super().__init__()
		self.passed = False
		if type == "hand_1":
			hand = pygame.image.load('assets/graphics/hands/hand_1.png').convert_alpha()
			hand = pygame.transform.scale2x(hand)
			y_pos = randint(140, 240)
			self.image = hand
			self.rect = self.image.get_rect(midtop = (randint(950,1050), y_pos))
		elif type == "hand_2":
			hand = pygame.image.load('assets/graphics/hands/hand_2.png').convert_alpha()
			hand = pygame.transform.scale2x(hand)
			y_pos = randint(180,250)
			self.image = hand
			self.rect = self.image.get_rect(midbottom = (randint(900,950), y_pos))
		
		self.mask = pygame.mask.from_surface(self.image)
	
	def destroy(self) -> None:
		''' Destroys hand sprite when off-screen '''
		if self.rect.x <= -100:
			self.kill()
	
	def score_checker(self) -> None:
		''' Checks shiba sprite location relative to hand. Calls score_counter if hand passes shiba sprite. '''
		if self.rect.x <= 80 and not self.passed:
			self.passed = True
			score_counter(1)

	def update(self, speed) -> None:
		''' Calls necessary function for tracking hands position and updating dependent values '''
		self.rect.x -= speed
		self.destroy()
		self.score_checker()

class Ground(pygame.sprite.Sprite):
	''' Ground sprite to generate seamless moving ground images '''
	def __init__(self, start_position, image_name) -> None:
		''' Initializes sprite class, picks image_name to generate '''
		super().__init__()
		self.image = pygame.image.load('assets/graphics/environment/'+image_name+'.png').convert()
		self.rect = self.image.get_rect(topleft = (start_position, 300))
	
	def update(self, speed) -> None:
		''' Updates sprite x value by the speed parameters '''
		self.rect.x -= speed
		self.destroy()
	
	def destroy(self) -> None:
		''' Destroys ground sprite when it leaves screen on the left side '''
		if self.rect.topright[0] <= 0:
			self.kill()
			if not secret_active:
				ground.add(Ground(812, 'ground'))
			else:
				ground.add(Ground(812, 'secret_ground'))

class Sky(pygame.sprite.Sprite):
	''' Sky sprite to generate seamless moving sky images '''
	def __init__(self, start_position, image_name) -> None:
		''' Initializes sprite class, picks image_name to generate '''
		super().__init__()
		self.image = pygame.image.load('assets/graphics/environment/'+image_name+'.png').convert()
		self.rect = self.image.get_rect(topleft = (start_position, 0))
	
	def update(self, speed) -> None:
		''' Updates sprite x value by the speed parameters '''
		self.rect.x -= speed
		self.destroy()
	
	def destroy(self) -> None:
		''' Destroys sky sprite when it leaves screen on the left side '''
		if self.rect.topright[0] <= 0:
			self.kill()
			if not secret_active:
				sky.add(Sky(850, 'sky'))
			else:
				sky.add(Sky(850, 'secret_sky'))

def collision_sprite() -> bool:
	''' Checks if hand and shiba sprites collide. Returns False if they collide. '''
	global current_score, secret_active, secret_start_time
	for hand in hands:
		hand_mask_offset = (hand.rect.x - shiba.sprite.rect.x, hand.rect.y - shiba.sprite.rect.y)
		if shiba.sprite.mask.overlap(hand.mask, hand_mask_offset):
			# Collision occurred
			death_sound.set_volume(death_sound_volume)
			death_sound.play()
			current_score = 0
			hands.empty()
			if secret_active == True:
				pygame.mixer.music.stop()
				pygame.mixer.music.load('assets/audio/stubborn_shiba_soundtrack.wav')
				pygame.mixer.music.set_volume(soundtrack_volume)
				pygame.mixer.music.play(-1)  # -1 plays the soundtrack on a loop
				pygame.time.set_timer(hand_timer, 1100)
				secret_start_time = 0
				secret_active=False
			shiba.sprite.rect.bottomleft = (80, 300)
			shiba.sprite.gravity = 0
			return False
	return True

def score_counter(score=0) -> None:
	''' Adds score to current_score and updates score_surf with current_score value '''
	global current_score
	current_score += score
	score_surf = game_font.render(f'{current_score}', False, (180, 180, 180))
	score_rect = score_surf.get_rect(midtop = (400, 25))
	screen.blit(score_surf, score_rect)

# Initialize pygame and assets
pygame.init()
pygame.mixer.init()
pygame.display.set_caption('Stubborn Shiba')
clock = pygame.time.Clock()
game_font = pygame.font.Font('assets/font/Pixeltype.ttf', 50)
death_sound = pygame.mixer.Sound('assets/audio/death.wav')
soundtrack = pygame.mixer.Sound('assets/audio/stubborn_shiba_soundtrack.wav')
death_sound_volume = 0.2
soundtrack_volume = 0.1

# Static Images
screen = pygame.display.set_mode((800, 400))
sky_surf = pygame.image.load('assets/graphics/environment/sky.png').convert()
ground_surf = pygame.image.load('assets/graphics/environment/ground.png').convert()
screen.blit(sky_surf, (0,0))
screen.blit(ground_surf, (0,300))

# Groups
shiba = pygame.sprite.GroupSingle()
shiba.add(Shiba())
hands = pygame.sprite.Group()
ground = pygame.sprite.Group()
sky = pygame.sprite.Group()
sky.add(Sky(0, 'sky'), Sky(850, 'sky'))
ground.add(Ground(0, 'ground'), Ground(812, 'ground'))

# Intro Screen
intro_font = pygame.font.Font('assets/font/Pixeltype.ttf', 100)
game_name_surf = intro_font.render("Stubborn Shiba", False, (0,0,0))
game_over_surf = intro_font.render("Game Over!", False, (0,0,0))
start_game_surf = game_font.render("Press Space to Start", False, (0,0,0))
restart_game_surf = game_font.render("Press Space to Restart", False, (0,0,0))
secret_title_surf = game_font.render("I don't know why you're still here", False, (255, 255, 255))
secret_subtitle_surf = intro_font.render("but good luck :)))", False, (255,255,255))
game_name_rect = game_name_surf.get_rect(midbottom=(400,200))
game_over_rect = game_over_surf.get_rect(midbottom=(400,200))
start_game_rect = start_game_surf.get_rect(midtop=(400, 200))
restart_game_rect = restart_game_surf.get_rect(midtop=(400, 200))
secret_title_rect = secret_title_surf.get_rect(midbottom=(400,200))
secret_subtitle_rect = secret_subtitle_surf.get_rect(midtop=(400,200))

# Timer
hand_timer = pygame.USEREVENT + 1
pygame.time.set_timer(hand_timer, 1100)
while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			exit()
		if not game_active:
			if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
				game_active = True
		else:
			if event.type == hand_timer:
				hands.add(Hands(choice(['hand_1', 'hand_2', 'hand_1', 'hand_1'])))
	
	if game_active and current_score < 100:
		# Sky
		sky.draw(screen)
		sky.update(1)
		
		# Score
		if current_score == -1:
			current_score = 0
		score_counter()

		# Shiba
		shiba.draw(screen)
		shiba.update()

		# Hands
		hands.draw(screen)
		hands.update(7)

		# Ground
		ground.draw(screen)
		ground.update(7)

		# Collisions
		game_active = collision_sprite()

		if not pygame.mixer.music.get_busy():  # Check if the soundtrack is not already playing
			pygame.mixer.music.load('assets/audio/stubborn_shiba_soundtrack.wav')
			pygame.mixer.music.set_volume(soundtrack_volume)
			pygame.mixer.music.play(-1)  # -1 plays the soundtrack on a loop

	elif not game_active and current_score < 100:
		if current_score == -1:
			screen.blit(game_name_surf, game_name_rect)
			screen.blit(start_game_surf, start_game_rect)
		else:
			screen.blit(game_over_surf, game_over_rect)
			screen.blit(restart_game_surf, restart_game_rect)
	else:
		# A "fun" little easter egg for users who get 100 points
		screen.fill('Black')
		if secret_active == False:
			pygame.mixer.music.rewind()
			hands.empty()
			sky.empty()
			ground.empty()
			if secret_start_time == 0:
				secret_start_time = pygame.time.get_ticks()
			if pygame.time.get_ticks() - secret_start_time >= 1000:
				screen.blit(secret_title_surf, secret_title_rect)
			if pygame.time.get_ticks() - secret_start_time >= 5000:
				screen.blit(secret_subtitle_surf, secret_subtitle_rect)
			if pygame.time.get_ticks() - secret_start_time >= 6000:
				secret_active = True
				sky.add(Sky(0, 'secret_sky'), Sky(850, 'secret_sky'))
				ground.add(Ground(0, 'secret_ground'), Ground(812, 'secret_ground'))
				pygame.mixer.music.stop()
				pygame.mixer.music.load('assets/audio/secret_song.mp3')
				pygame.mixer.music.set_volume(0.2)
				pygame.mixer.music.play(-1)
				pygame.time.set_timer(hand_timer, 800)
		else:
			# Sky
			sky.draw(screen)
			sky.update(10)
			
			# Score
			if current_score == -1:
				current_score = 0
			score_counter()

			# Shiba
			shiba.draw(screen)
			shiba.update()

			# Hands
			hands.draw(screen)
			hands.update(14)

			# Ground
			ground.draw(screen)
			ground.update(14)

			# Collisions
			game_active = collision_sprite()
	
	pygame.display.update() # Required by pygame to update changes to display
	clock.tick(60) # Sets max framerate at 60 FPS

