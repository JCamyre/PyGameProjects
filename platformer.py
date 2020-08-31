import pygame, sys, os, random
import data.engine as e
clock = pygame.time.Clock()

from pygame.locals import *
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init() # initiates pygame
pygame.mixer.set_num_channels(64)

MUSIC_ENDED = pygame.USEREVENT
pygame.mixer.music.set_endevent(MUSIC_ENDED)

pygame.display.set_caption('Pygame Platformer')

WINDOW_SIZE = (1200,800)

screen = pygame.display.set_mode(WINDOW_SIZE,0,32) # initiate the window

display = pygame.Surface((300,200)) # used as the surface for rendering, which is scaled

moving_right = False
moving_left = False
vertical_momentum = 0
air_timer = 0

true_scroll = [0,0]

CHUNK_SIZE = 8

def generate_chunk(x, y):
    chunk_data = []
    for y_pos in range(CHUNK_SIZE):
        for x_pos in range(CHUNK_SIZE):
            # we are multiplying by CHUNK_SIZE to get the top left corner of the square chunk we want from all the other chunks
            target_x = x * CHUNK_SIZE + x_pos # both of these are absolute positions with all the other chunks
            target_y = y * CHUNK_SIZE + y_pos
            tile_type = 0 # nothing
            if target_y > 10: # So basically the top couple rows of chunks will be only sky
                tile_type = 2 # dirt
            elif target_y == 10: 
                tile_type = 1 # grass
            elif target_y == 9:
                if random.randint(1, 5) == 1:
                    tile_type = 3 # plant
            if tile_type != 0:
                chunk_data.append([[target_x, target_y], tile_type])
    return chunk_data

class JumperObject:
    def __init__(self, loc):
        self.loc = loc 

    def render(self, surf, scroll):
        surf.blit(jumper_img, (self.loc[0] - scroll[0], self.loc[1] - scroll[1]))

    def get_rect(self):
        return pygame.Rect(self.loc[0], self.loc[1], 8, 9)

    def collision_test(self, rect): # test if the player's rect is touching it
        jumper_rect = self.get_rect()
        return jumper_rect.colliderect(rect)


e.load_animations('data/images/entities/')

game_map = {}

grass_img = pygame.image.load('data/images/grass.png')
dirt_img = pygame.image.load('data/images/dirt.png')
plant_img = pygame.image.load('data/images/plant.png').convert()
plant_img.set_colorkey((255, 255, 255))

jumper_img = pygame.image.load('data/images/jumper.png').convert()
jumper_img.set_colorkey((255, 255, 255))

tile_index = {
    1: grass_img,
    2: dirt_img,
    3: plant_img
}

jump_sound = pygame.mixer.Sound('data/audio/soundeffects/jump.wav')
grass_sounds = [pygame.mixer.Sound('data/audio/soundeffects/grass_0.wav'),pygame.mixer.Sound('data/audio/soundeffects/grass_1.wav')]
grass_sounds[0].set_volume(0.08)
grass_sounds[1].set_volume(0.08)
gun_sound = pygame.mixer.Sound('data/audio/soundeffects/gunshot.wav')
gun_sound.set_volume(0.1)

# Music related
all_songs = []
for root, dirs, files in os.walk("data/audio/music/", topdown=False):
   for name in files:
      all_songs.append(os.path.join(root, name))
random.shuffle(all_songs)
playlist = all_songs.copy()

# shuffle list, if at end of list, reshuffle list and start from top again
song_no = 0
pygame.mixer.music.load(playlist[song_no])
pygame.mixer.music.set_volume(0.25)
pygame.mixer.music.play() 

class Bullet:
    def __init__(self, scroll):
        if player.flip:
            self.vel = -3
            self.flip = True
        else:
            self.vel = 3
            self.flip = False
        self.timer = 0
            #  - scroll[0], - scroll[1]
        self.rect = pygame.Rect(player.x - 3, player.y + 3, 9, 4)

    def move(self, tiles):
        # Add an enemy rect list
        # Don't care about collision type for bullet, atleast for now
        # collision_types = {'right': False, 'left': False}

        self.rect.x += self.vel
        hit_list = e.collision_test(self.rect, tiles)
        for tile in hit_list:
            return False 
        return True

bullets = []

player_action = 'idle'
player_frame = 0
player_flip = False
player_sprint = False

grass_sound_timer = 0

player = e.entity(100, 100, 5, 13, 'player')

enemies = []

for i in range(5):
    enemies.append([0, e.entity(random.randint(0, 600)-300, 80, 13, 13, 'enemy')])

class Rect(pygame.Rect):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

    def __repr__(self):
        return f'x: {self.x}, y: {self.y}, width: {self.width}, height: {self.height}'

background_objects = [[0.25,[120,10,70,400]],[0.25,[280,30,40,400]],[0.5,[30,40,40,400]],[0.5,[130,90,100,400]],[0.5,[300,80,120,400]]]

jumper_objects = []

for i in range(10):
    jumper_objects.append(JumperObject((random.randint(0, 600) - 300, 80)))

while True: # game loop
    display.fill((146,244,255)) # clear screen by filling it with blue

    if grass_sound_timer > 0:
        grass_sound_timer -= 1

    true_scroll[0] += (player.x-true_scroll[0]-152)/20
    true_scroll[1] += (player.y-true_scroll[1]-106)/20
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])

    pygame.draw.rect(display,(7,80,75),pygame.Rect(0,120,300,80))
    for background_object in background_objects:
        obj_rect = pygame.Rect(background_object[1][0]-scroll[0]*background_object[0],background_object[1][1]-scroll[1]*background_object[0],background_object[1][2],background_object[1][3])
        if background_object[0] == 0.5:
            pygame.draw.rect(display,(20,170,150),obj_rect)
        else:
            pygame.draw.rect(display,(15,76,73),obj_rect)

    tile_rects = []
    """Calculations for amount of chunks to display on screen a time:
    x: 300 (display resolution, doesn't matter that it is scaled up) / (8 (which is CHUNK_SIZE) * 16 (which is the width of each tile)) = 
    2.344, and always round up and add one. So need 4 chunks at a time
    y: 200 / (8 * 16 (tile height)) = 1.6. Round up and add one. 3
    """    
    for y in range(3):
        for x in range(4):
            # find which specific chunks you need to display, but everytime you render you will need to show three chunks tall and 
            # four wide (total of 12 on screen at a time)
            target_x = x - 1 + int(round(scroll[0]/(CHUNK_SIZE * 16))) # target_x and target_y is which chunk to choose from the 2d map of chunks
            target_y = y - 1 + int(round(scroll[1]/(CHUNK_SIZE * 16)))
            '''x - 1 and y - 1 cause the top left corner of the most left chunk
            being loaded could be partly off-screen'''

            target_chunk = str(target_x) + ';' + str(target_y)
            if target_chunk not in game_map: # if the chunk we need to display hasn't been generated, generate it now
                game_map[target_chunk] = generate_chunk(target_x, target_y)
            for tile in game_map[target_chunk]: # display the chunk's tiles
                # I'm assuming that tile is a list with tile[0] = Rect(), tile[1] = What type it is
                display.blit(tile_index[tile[1]], (tile[0][0]*16-scroll[0], tile[0][1] * 16 - scroll[1]))
                if tile[1] in [1, 2]:
                    tile_rects.append(pygame.Rect(tile[0][0]*16, tile[0][1]*16, 16, 16))

    player_movement = [0,0]
    if moving_right == True:
        player_movement[0] += 1
    if moving_left == True:
        player_movement[0] -= 1

    if player_sprint:
        player_movement[0] *= 2

    player_movement[1] += vertical_momentum
    vertical_momentum += 0.08
    if vertical_momentum > 3:
        vertical_momentum = 3

    if player_movement[0] == 0:
        player.set_action('idle')
    if player_movement[0] > 0:
        player.set_flip(False)
        player.set_action('run')
    if player_movement[0] < 0:
        player.set_flip(True)
        player.set_action('run')


    collision_types = player.move(player_movement,tile_rects)

    if collision_types['bottom']:
        air_timer = 0
        vertical_momentum = 0
        if player_movement[0] != 0:
            if grass_sound_timer == 0:
                grass_sound_timer = 80
                random.choice(grass_sounds).play()
    else:
        air_timer += 1

    if collision_types['top']:
        vertical_momentum = 0.5

    player.change_frame(1)
    player.display(display, scroll)

    for jumper in jumper_objects:
        jumper.render(display, scroll)
        if jumper.collision_test(player.obj.rect):
            vertical_momentum = -6

    display_r = pygame.Rect(scroll[0], scroll[1], 300, 200) # Basically uses scroll at the top left corner of our display rectangle
    # if something collides with the rectangle, then we can display it as it is in our view

    for enemy in enemies:
        if display_r.colliderect(enemy[1].obj.rect):
            for bullet in bullets:      
                if bullet.rect.colliderect(enemy[1].obj.rect):
                    enemies.remove(enemy)
                    bullets.remove(bullet)
                    continue
            enemy[0] += 0.08
            if enemy[0] > 3:
                enemy[0] = 3
            enemy_movement = [0, enemy[0]]
            if player.x > enemy[1].x + 5: # enemy[1].x access the enemies rect's x coord
                enemy_movement[0] = 0.75
            if player.x < enemy[1].x - 5:
                enemy_movement[0] = -0.75
            collision_types = enemy[1].move(enemy_movement, tile_rects)
            if collision_types['bottom']:
                enemy[0] = 0

            enemy[1].display(display, scroll)

            if player.obj.rect.colliderect(enemy[1].obj.rect):
                vertical_momentum = -1.5



    for bullet in bullets:
        # If collides with wall, it breaks
        bullet.timer += 1
        if bullet.timer > 100:
            bullets.remove(bullet)
            continue
        if bullet.move(tile_rects):
            bullet_img = pygame.image.load('data/images/bullet.png').convert()
            bullet_img.set_colorkey((255, 255, 255))    
            bullet_img = pygame.transform.scale(bullet_img, (9, 4))
            display.blit(pygame.transform.flip(bullet_img, bullet.flip, False), (bullet.rect.x - scroll[0], bullet.rect.y - scroll[1]))
        else:
            bullets.remove(bullet)

    for event in pygame.event.get(): # event loop
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_w:
                pygame.mixer.music.fadeout(1000)
            if event.key == K_d:
                moving_right = True
            if event.key == K_a:
                moving_left = True
            if event.key == K_SPACE:
                if air_timer < 16:
                    jump_sound.play()
                    vertical_momentum = -4
            if event.key == K_j:
                bullets.append(Bullet(scroll))
                gun_sound.play()
            if event.key == K_LSHIFT:
                player_sprint = True
        if event.type == KEYUP:
            if event.key == K_d:
                moving_right = False
            if event.key == K_a:
                moving_left = False
            if event.key == K_LSHIFT:
                player_sprint = False
        if event.type == MUSIC_ENDED:
            if song_no == len(playlist) - 1:
                playlist = random.shuffle(all_songs)
            song_no = (song_no + 1) % len(playlist)
            pygame.mixer.music.load(playlist[song_no])
            pygame.mixer.music.play()


    screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))

    # fps counter
    font = pygame.font.SysFont('gillsans', 35)
    fps = font.render('FPS: ' + str(int(clock.get_fps())), True, pygame.Color('white'))
    screen.blit(fps, (25, 25))

    songname = font.render(playlist[song_no].split('/')[-1].split('.mp3')[0], True, pygame.Color('white'))
    screen.blit(songname, (400, 25))

    pygame.display.update()
    clock.tick(144)
