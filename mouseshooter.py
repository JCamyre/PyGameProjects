import pygame, sys
from math import asin, sin, cos, pi, degrees
mainClock = pygame.time.Clock()
from pygame.locals import *

pygame.mixer.pre_init(44100, -16, 2, 512) # NO LAG WHEN .play()
pygame.init() # initiates pygame
pygame.mixer.set_num_channels(64)

screen = pygame.display.set_mode((1200, 800), 0, 32)

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

def player_mouse_direction():
	mx, my = pygame.mouse.get_pos()
	x, y = player_rect.x - scroll[0], player_rect.y+25 - scroll[1]
	hypotenuse = ((mx - x)**2 + (my - y)**2)**0.5
	height = my - y
	direction = asin(height/hypotenuse)
	return direction 

class Bullet:

	def __init__(self):
		self.rect = pygame.Rect(player_rect.x, player_rect.y, player_rect.width, player_rect.height)
		self.direction = player_mouse_direction()
		self.vel_x = 0
		self.vel_y = 0
		self.flip = player_flip
		self.get_velocity(10)
		self.count = 0

	def get_velocity(self, hypotenuse):
		if self.flip:
			self.vel_x = -1 * hypotenuse * cos(self.direction)
		else:
			self.vel_x = hypotenuse * cos(self.direction)
		self.vel_y = hypotenuse * sin(self.direction)

	def move(self):
		self.rect.x += self.vel_x
		self.rect.y += self.vel_y


bullet_img = pygame.image.load('bullet.png').convert()
bullet_img = pygame.transform.scale(bullet_img, (36, 16))
bullet_img.set_colorkey((255, 255, 255))

bullets = []

class Enemy:

	def __init__(self):
		self.rect = pygame.Rect(800, 400, 50, 50)
		self.image = pygame.image.load('data/images/entities/enemy/idle/idle_0.png').convert()
		self.image.set_colorkey((255, 255, 255))

enemies = []
enemy1 = Enemy()
enemies.append(enemy1)

clicking = False

player_flip = False

moving_right = False
moving_left = False
moving_forward = False
moving_backward = False

true_scroll = [0, 0]

while True:
	screen.fill((0, 120, 0))

	true_scroll[0] += (player_rect.x-true_scroll[0]-600)/20
	true_scroll[1] += (player_rect.y-true_scroll[1]-400)/20
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
		screen.blit(pygame.transform.flip(pygame.transform.scale(char_front, (20, 52)), player_flip, False), (player_rect.x - scroll[0], player_rect.y - scroll[1]))
	else:
		screen.blit(pygame.transform.flip(pygame.transform.scale(char_behind, (20, 52)), player_flip, False), (player_rect.x - scroll[0], player_rect.y - scroll[1]))


	for enemy in enemies:
		screen.blit(enemy.image, (enemy.rect.x - scroll[0], enemy.rect.y - scroll[1]))
		for bullet in bullets:
			if enemy.rect.colliderect(bullet.rect):
				hitmarker_sound.play()
				enemies.remove(enemy)
				bullets.remove(bullet)

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
		screen.blit(modified_bullet_img, (bullet.rect.x - scroll[0], bullet.rect.y - scroll[1]))

	mouseloc = [mx, my]
	img_dimensions = crosshair.get_size()
	mid_x, mid_y = mouseloc[0] - img_dimensions[0]//2, mouseloc[1] - img_dimensions[1]//2
	screen.blit(crosshair, (mid_x + offset[0], mid_y + offset[1]))

	if moving_right:
		player_rect.x += 4
	if moving_left:
		player_rect.x -= 4
	if moving_forward:
		player_rect.y -= 4
	if moving_backward:
		player_rect.y += 4

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
		if event.type == KEYUP:
			if event.key == K_a:
				moving_left = False
			if event.key == K_d:
				moving_right = False
			if event.key == K_w:
				moving_forward = False
			if event.key == K_s:
				moving_backward = False
		if event.type == MOUSEBUTTONDOWN:
			if event.button == 1:
				gun_sound.play()
				clicking = True
				bullets.append(Bullet())
		if event.type == MOUSEBUTTONUP:
			if event.button == 1:
				clicking = False

	font = pygame.font.SysFont('gillsans', 35)
	display_direction = font.render(str(player_mouse_direction()), True, pygame.Color('white'))
	screen.blit(display_direction, (25, 25))

	position = font.render(str(player_rect.x) + ', ' + str(player_rect.y), True, pygame.Color('white'))
	screen.blit(position, (25, 50))

	pygame.display.update()
	mainClock.tick(144)
