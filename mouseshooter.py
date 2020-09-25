import pygame, sys
from math import asin, sin, cos, pi, degrees
import random
mainClock = pygame.time.Clock()
from pygame.locals import *

pygame.mixer.pre_init(44100, -16, 2, 512) # NO LAG WHEN .play()
pygame.init() # initiates pygame
pygame.mixer.set_num_channels(64)

screen = pygame.display.set_mode((1400, 1000), 0, 32)

pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))

crosshair = pygame.transform.scale(pygame.image.load('crosshair.png').convert(), (50, 50))
crosshair.set_colorkey((0, 0, 255))
print(crosshair.get_size())
offset = [0, 0]

gun_sound = pygame.mixer.Sound('data/audio/soundeffects/gunshot.wav')
gun_sound.set_volume(0.1)

hitmarker_sound = pygame.mixer.Sound('hitmarker_2.wav')
hitmarker_sound.set_volume(0.03)

char_front = pygame.image.load('idle_2.png').convert()
char_front.set_colorkey((255, 255, 255))

char_behind = pygame.image.load('char_behind.png').convert()
char_behind.set_colorkey((255, 255, 255))

player_rect = pygame.Rect(600, 400, 40, 104)
# Have to account for camera movement when deciding bullet direction blit.

def player_mouse_direction():
	mx, my = pygame.mouse.get_pos()
	x, y = player_rect.x - scroll[0], player_rect.y+10 - scroll[1]
	hypotenuse = ((mx - x)**2 + (my - y)**2)**0.5
	height = my - y
	direction = asin(height/hypotenuse)
	return direction 

class Bullet:

	def __init__(self):
		self.vel_x = 0
		self.vel_y = 0
		self.count = 0

	def pos(self):
		if player_flip:
			self.rect = pygame.Rect(player_rect.x-5, player_rect.y+20, 36, 16)
		else:
			self.rect = pygame.Rect(player_rect.x+5, player_rect.y+20, 36, 16)
		self.direction = player_mouse_direction()
		self.flip = player_flip
		self.get_velocity(10)

	def get_velocity(self, hypotenuse):
		if self.flip:
			self.vel_x = -1 * hypotenuse * cos(self.direction)
		else:
			self.vel_x = hypotenuse * cos(self.direction)
		self.vel_y = hypotenuse * sin(self.direction)

	def move(self):
		self.rect.x += self.vel_x
		self.rect.y += self.vel_y

# do I have bullets in the gun class? To track when to reload. 
# Could have a base gun class and have classes for them.
class Gun:

	def __init__(self, mag_size):
		self.mag_size = mag_size
		self.reload()

	def reload(self):
		print('Reloading...')
		self.bullets = [Bullet() for bullet in range(self.mag_size)] 

	def shoot(self):
		# pop() returns on its own right?
		bullet = self.bullets.pop(0)
		bullet.pos()
		return bullet

gun_img = pygame.image.load('M1911.png').convert()
gun_img = pygame.transform.scale(gun_img, (44, 32))
gun_img.set_colorkey((255, 255, 255))
# 436, 332

bullet_img = pygame.image.load('bullet.png').convert()
bullet_img = pygame.transform.scale(bullet_img, (36, 16))
bullet_img.set_colorkey((255, 255, 255))

bullets = []

enemy_img = pygame.image.load('data/images/entities/enemy/idle/idle_0.png').convert()
enemy_img = pygame.transform.scale(enemy_img, (35, 35))
enemy_img.set_colorkey((255, 255, 255))

class Enemy:

	def __init__(self):
		self.x = random.randint(50, 1400)
		self.y = random.randint(50, 1400)
		self.rect = pygame.Rect(self.x, self.y, 35, 35)

	# Need to make a universal method for x and y velocity. If you know where you want to go, automatically does x and y velocity
	# given a certain max velocity. 
	def move(self, x, y):
		if player_rect.x > self.x + 10:
			self.x += 15
		else:
			self.x -= 15

		if player_rect.y > self.y + 10:
			self.y += 15
		else:
			self.y -= 15

		self.rect = pygame.Rect(self.x, self.y, 35, 35)

enemies = []

for _ in range(random.randint(5, 10)):
	enemies.append(Enemy())

player_flip = False
player_sprint = False
player_roll = False
player_roll_frame = 0

moving_right = False
moving_left = False
moving_forward = False
moving_backward = False

true_scroll = [0, 0]

true_scroll[0] += (player_rect.x-true_scroll[0]-700)/15
true_scroll[1] += (player_rect.y-true_scroll[1]-500)/15
scroll = true_scroll.copy()
scroll[0] = int(scroll[0])
scroll[1] = int(scroll[1])

player_gun = Gun(9)

while True:
	screen.fill((117, 18, 255))

	true_scroll[0] += (player_rect.x-true_scroll[0]-700)/15
	true_scroll[1] += (player_rect.y-true_scroll[1]-500)/15
	scroll = true_scroll.copy()
	scroll[0] = int(scroll[0])
	scroll[1] = int(scroll[1])

	# Mouse aiming
	mx, my = pygame.mouse.get_pos()
	if mx > player_rect.x - scroll[0]:
		player_flip = False
	else:	
		player_flip = True

	if player_rect.y - scroll[1] < my:
		if player_roll:
			screen.blit(pygame.transform.rotate(pygame.transform.flip(pygame.transform.scale(char_front, (40, 104)), player_flip, False), (player_rect.x - scroll[0], player_rect.y - scroll[1]), player_roll_frame%15 * 90))
			player_roll_frame += 1
			if player_roll_frame > 60:
				player_roll = False
		else:
			screen.blit(pygame.transform.flip(pygame.transform.scale(char_front, (40, 104)), player_flip, False), (player_rect.x - scroll[0], player_rect.y - scroll[1]))
	else:
		screen.blit(pygame.transform.flip(pygame.transform.scale(char_behind, (40, 104)), player_flip, False), (player_rect.x - scroll[0], player_rect.y - scroll[1]))
	# Add direction, pygame.transform.rotate()
	if player_flip:
		screen.blit(pygame.transform.rotate(pygame.transform.flip(gun_img, player_flip, False), degrees(player_mouse_direction())), (player_rect.x - 30 - scroll[0], player_rect.y + 20 - scroll[1]))
	else:
		screen.blit(pygame.transform.rotate(pygame.transform.flip(gun_img, player_flip, False), -1 * degrees(player_mouse_direction())), (player_rect.x + 25 - scroll[0], player_rect.y + 20 - scroll[1]))


	for enemy in enemies:
		# Enemy movement determined by player position + it just moves a little bit randomly
		if random.randint(0, 20) == 0:
			enemy.move(random.randint(-10, 10), random.randint(-10, 10))
		screen.blit(enemy_img, (enemy.rect.x - scroll[0], enemy.rect.y - scroll[1]))
		for bullet in bullets:
			if enemy.rect.colliderect(bullet.rect):
				hitmarker_sound.play()
				enemies.remove(enemy)
				bullets.remove(bullet)

	player_movement = [0, 0]

	if moving_right:
		player_movement[0] = 2
	if moving_left:
		player_movement[0] = -2
	if moving_forward:
		player_movement[1] = -2
	if moving_backward:
		player_movement[1] = 2

	if player_sprint:
		player_movement[0] *= 2
		player_movement[1] *= 2

	player_rect.x += player_movement[0]
	player_rect.y += player_movement[1]

	for bullet in bullets:
		bullet.count += 1
		if bullet.count > 144: 
			bullets.remove(bullet)
			continue
		bullet.move()

		if bullet.flip:		
			modified_bullet_img = pygame.transform.rotate(pygame.transform.flip(bullet_img, bullet.flip, False), degrees(bullet.direction))
		else:
			modified_bullet_img = pygame.transform.rotate(pygame.transform.flip(bullet_img, bullet.flip, False), degrees(-1*bullet.direction))		
		# Bullet speed is relative if I am moving/sprinting. Cringe.
		screen.blit(modified_bullet_img, (bullet.rect.x - scroll[0], bullet.rect.y - scroll[1]))

	mouseloc = [mx, my]
	img_dimensions = crosshair.get_size()
	mid_x, mid_y = mouseloc[0] - img_dimensions[0]//2, mouseloc[1] - img_dimensions[1]//2
	screen.blit(crosshair, (mid_x + offset[0], mid_y + offset[1]))

	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		if event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				pygame.quit()
				sys.exit()
			if event.key == K_a:
				moving_left = True
			if event.key == K_d:
				moving_right = True
			if event.key == K_w:
				moving_forward = True
			if event.key == K_s:
				moving_backward = True
			if event.key == K_r:
				player_gun.reload()
			if event.key == K_LSHIFT:
				player_sprint = True
			if event.key == K_SPACE:
				player_roll = True
		if event.type == KEYUP:
			if event.key == K_a:
				moving_left = False
			if event.key == K_d:
				moving_right = False
			if event.key == K_w:
				moving_forward = False
			if event.key == K_s:
				moving_backward = False
			if event.key == K_LSHIFT:
				player_sprint = False
			if event.key == K_SPACE:
				player_roll = False
		if event.type == MOUSEBUTTONDOWN:
			if event.button == 1:
				if len(player_gun.bullets) > 0:			
					gun_sound.play()
					bullets.append(player_gun.shoot())
				else:
					print('Your clip is empty')
			if event.button == 2:
				player_roll = True
		if event.type == MOUSEBUTTONUP:
			if event.button == 2:
				player_roll = False

	font = pygame.font.SysFont('gillsans', 35)
	display_direction = font.render(str(player_mouse_direction()), True, pygame.Color('white'))
	screen.blit(display_direction, (25, 25))

	position = font.render(str(player_rect.x) + ', ' + str(player_rect.y), True, pygame.Color('white'))
	screen.blit(position, (25, 75))

	ammo = font.render(str(len(player_gun.bullets)) + '/' + str(player_gun.mag_size), True, pygame.Color('white'))
	screen.blit(ammo, (25, 125))

	pygame.display.update()
	mainClock.tick(144)
