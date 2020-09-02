import pygame, sys
from math import asin, sin, cos, pi
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

target = pygame.Rect(400, 400, 100, 100)

player_rect = pygame.Rect(600, 400, 40, 104)

def player_mouse_direction(flip=False):
	mx, my = pygame.mouse.get_pos()
	x, y = player_rect.x, player_rect.y 
	hypotenuse = ((mx - x)**2 + (my - y)**2)**0.5
	height = my - y
	# How to get full 360 instead of the 0-90 range for a triangle (like a triangle in quadrant 3)
	direction1 = asin(height/hypotenuse)
	direction2 = acos((mx-x)/hypotenuse)
	if flip:
		print(direction*-1)
		return direction * -1
	return direction 

class Bullet:

	def __init__(self):
		self.x = player_rect.x
		self.y = player_rect.y
		self.direction = player_mouse_direction(flip=player_flip)
		self.vel_x = 0
		self.vel_y = 0
		self.get_velocity(10)

	# For full 360 movement, get the direction you want to go, then self.y_vel and self.x_vel
	def get_velocity(self, hypotenuse):
		self.vel_x = hypotenuse * cos(self.direction)
		self.vel_y = hypotenuse * sin(self.direction)


bullet_img = pygame.image.load('bullet.png').convert()
bullet_img.set_colorkey((255, 255, 255))

bullets = []

clicking = False

player_flip = False

while True:
	screen.fill((0, 120, 0))

	mx, my = pygame.mouse.get_pos()

	if mx > 600:
		player_flip = False
	else:
		player_flip = True

	if 400 < my:
		screen.blit(pygame.transform.flip(pygame.transform.scale(char_front, (40, 104)), player_flip, False), (600, 400))
	else:
		screen.blit(pygame.transform.flip(pygame.transform.scale(char_behind, (40, 104)), player_flip, False), (600, 400))


	if target.collidepoint(mx, my):
		if clicking:
			hitmarker_sound.play()
			pygame.draw.rect(screen, (255, 255, 0), target)
		else:
			pygame.draw.rect(screen, (0, 255, 255), target)
	else:
		pygame.draw.rect(screen, (0, 255, 255), target)

	for bullet in bullets:
		# note you have to rotate considering that the base bullet img is pointing straight right (0 radians)
		# screen.blit(pygame.transform.rotate(img, degrees), (x, y))
		bullet.x += bullet.vel_x 
		bullet.y += bullet.vel_y
		screen.blit(bullet_img, (bullet.x, bullet.y))

	loc = [mx, my]
	img_dimensions = crosshair.get_size()
	mid_x, mid_y = loc[0] - img_dimensions[0]//2, loc[1] - img_dimensions[1]//2
	screen.blit(crosshair, (mid_x + offset[0], mid_y + offset[1]))


	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		if event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				pygame.quit()
				sys.exit()
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

	pygame.display.update()
	mainClock.tick(144)
