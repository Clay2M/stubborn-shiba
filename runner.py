import pygame
from sys import exit
from random import randint, choice
import pygame.mask, pygame.mixer

jump_debounce = True
flip_debounce = True
start_time = 0
current_score = 0

class Shiba(pygame.sprite.Sprite):
	def __init__(self) -> None:
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
	
	def player_input(self):
		global jump_debounce, flip_debounce, start_time
		current_time = pygame.time.get_ticks() - start_time
		keys = pygame.key.get_pressed()
		if keys[pygame.K_SPACE] and self.rect.bottom >= 300 and jump_debounce:
			self.gravity = -17
			jump_debounce = False
			start_time = pygame.time.get_ticks()
		elif self.rect.bottom >= 300 and not jump_debounce and current_time >= 250:
			jump_debounce = True
		elif keys[pygame.K_SPACE] and not jump_debounce and flip_debounce and current_time >= 250:
			self.gravity = -15
			self.shiba_jumping_index = 0
			flip_debounce = False
		elif jump_debounce:
			flip_debounce = True

		# Mask update
		self.mask = pygame.mask.from_surface(self.image)
	
	def apply_gravity(self):
		self.gravity += 1
		self.rect.y += self.gravity
		if self.rect.bottom >= 300:
			self.rect.bottom = 300
	
	def animation_player(self):
		if not jump_debounce:
			self.shiba_jumping_index += 0.15
			if self.shiba_jumping_index >= len(self.shiba_jumping): self.shiba_jumping_index = 0
			self.image = self.shiba_jumping[int(self.shiba_jumping_index)]
		else:
			self.shiba_jumping_index = 0
			self.shiba_running_index += 0.3
			if self.shiba_running_index >= len(self.shiba_running): self.shiba_running_index = 0
			self.image = self.shiba_running[int(self.shiba_running_index)]
		
	def update(self):
		self.player_input()
		self.apply_gravity()
		self.animation_player()

class Hands(pygame.sprite.Sprite):
	def __init__(self, type) -> None:
		super().__init__()
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
	
	def update(self):
		self.rect.x -= 6
		self.destroy()
		self.score_checker()
	
	def destroy(self):
		if self.rect.x <= -100:
			self.kill()
	
	def score_checker(self):
		if 75 <= self.rect.x <= 80:
			score_counter(1)

class Ground(pygame.sprite.Sprite):
	def __init__(self, start_position) -> None:
		super().__init__()
		sky = pygame.image.load('assets/graphics/environment/ground.png')
		self.image = sky
		self.rect = self.image.get_rect(topleft = (start_position, 300))
	
	def update(self):
		self.rect.x -= 6
		self.destroy()
	
	def destroy(self):
		if self.rect.x <= -380:
			self.kill()


def collision_sprite():
	global current_score
	for hand in hands:
		hand_mask_offset = (hand.rect.x - shiba.sprite.rect.x, hand.rect.y - shiba.sprite.rect.y)

		if shiba.sprite.mask.overlap(hand.mask, hand_mask_offset):
			# Collision occurred
			death_sound.set_volume(death_sound_volume)
			death_sound.play()
			hands.empty()
			current_score = 0
			shiba.sprite.rect.bottomleft = (80, 300)
			shiba.sprite.gravity = 0
			return False

	return True

def score_counter(score=0):
	global current_score
	current_score += score
	score_surf = game_font.render(f'{current_score}', False, (180, 180, 180))
	score_rect = score_surf.get_rect(midtop = (400, 25))
	screen.blit(score_surf, score_rect)

# Initialize
pygame.init()
pygame.mixer.init()

pygame.display.set_caption('Stubborn Shiba')
clock = pygame.time.Clock()
game_font = pygame.font.Font('assets/font/Pixeltype.ttf', 50)
game_active = True
# TODO: Add Music
death_sound = pygame.mixer.Sound('assets/audio/death.wav')
soundtrack = pygame.mixer.Sound('assets/audio/stubborn_shiba_soundtrack.wav')
death_sound_volume = 0.2
soundtrack_volume = 0.1

game_started = False

# Static Images
screen = pygame.display.set_mode((800, 400))
sky_surf = pygame.image.load('assets/graphics/environment/Sky.png').convert()
ground_surf = pygame.image.load('assets/graphics/environment/ground.png').convert()

# Groups
shiba = pygame.sprite.GroupSingle()
shiba.add(Shiba())
hands = pygame.sprite.Group()
ground = pygame.sprite.Group()
ground.add(Ground(0), Ground(800))

# Intro Screen
intro_font = pygame.font.Font('assets/font/Pixeltype.ttf', 150) # TODO: Figure out if game_font can be used with different size
game_over_surf = intro_font.render("Game Over!", False, (0,0,0))
restart_game_surf = game_font.render("Press Space to Restart", False, (0,0,0))
game_over_rect = game_over_surf.get_rect(midbottom = (400, 200))
restart_game_rect = restart_game_surf.get_rect(midtop = (400, 200))

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
	
	if game_active:
		screen.blit(sky_surf, (0,0))
		screen.blit(ground_surf, (0, 300))
		score_counter()

		# Shiba
		shiba.draw(screen)
		shiba.update()

		# Hands
		hands.draw(screen)
		hands.update()

		# Ground
		#ground.draw(screen)
		#ground.update()

		# Collisions
		game_active = collision_sprite()

		if not pygame.mixer.music.get_busy():  # Check if the soundtrack is not already playing
			pygame.mixer.music.load('assets/audio/stubborn_shiba_soundtrack.wav')
			pygame.mixer.music.set_volume(soundtrack_volume)
			pygame.mixer.music.play(-1)  # -1 plays the soundtrack on a loop

	else:
		screen.blit(game_over_surf, game_over_rect)
		screen.blit(restart_game_surf, restart_game_rect)
	
	pygame.display.update()
	clock.tick(60)