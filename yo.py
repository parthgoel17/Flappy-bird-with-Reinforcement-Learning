import pygame
from pygame.locals import *
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 864
screen_height = 936

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')
font = pygame.font.SysFont('Bauhaus 93', 60)

white = (255, 255, 255)

ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 175
pipe_frequency = 1500 #milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False
pipe_list = []


bg = pygame.image.load('bg.png')
ground_img = pygame.image.load('ground.png')
button_img = pygame.image.load('restart.png')

class Bird(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('bird1.png')
		self.index = 0
		self.counter = 0
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.vel = 0
		self.clicked = False

	def update(self):
		self.vel += 0.5
		if self.vel > 8:
			self.vel = 8
		if self.rect.bottom < 768:
			self.rect.y += int(self.vel)

	def move(self,action):
		if game_over == False:
			if action==1:
				self.vel = -10


class Pipe(pygame.sprite.Sprite):
	def __init__(self, x, y, position):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('pipe.png')
		self.rect = self.image.get_rect()
		#position 1 is from the top, -1 is from the bottom
		if position == 1:
			self.image = pygame.transform.flip(self.image, False, True)
			self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
		if position == -1:
			self.rect.topleft = [x, y + int(pipe_gap / 2)]

	def update(self):
		self.rect.x -= scroll_speed
		if self.rect.center < flappy.rect.center:
			pipe_list.pop(0)
			pipe_list.pop(0)
			self.kill()


bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))

bird_group.add(flappy)

def update_ui():
	global ground_scroll
	screen.blit(bg, (0,0))
	screen.blit(ground_img, (ground_scroll, 768))
			#draw and scroll the ground
	ground_scroll -= scroll_speed
	if abs(ground_scroll) > 35:
			ground_scroll = 0
	clock.tick(fps)
	bird_group.draw(screen)
	bird_group.update()
	pipe_group.draw(screen)
	#draw_text(str(score), font, white, int(screen_width / 2), 20)
	pygame.display.update()


def reset_game():
	global game_over,last_pipe,pass_pipe,score
	game_over=False
	last_pipe = 0
	pass_pipe = False
	pipe_group.empty()
	pipe_list.clear()
	flappy.rect.x = 100
	flappy.rect.y = int(screen_height / 2)
	score = 0


def play_state(action):
	global game_over,last_pipe,pass_pipe
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
			pygame.quit()

	flappy.move(action)
	global score
	reward = 0
	#194
	if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0 or flappy.rect.bottom >= 768:
		game_over = True
		reward -= 100
		return reward, game_over,score

	if len(pipe_group) > 0:
		if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
			and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
			and pass_pipe == False:
			pass_pipe = True
		if pass_pipe == True:
			if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
				score += 1
				reward += 1
				print(score)
				pass_pipe = False

	if game_over == False:

		#generate new pipes
		time_now = pygame.time.get_ticks()
		if time_now - last_pipe > pipe_frequency:
			pipe_height = random.randint(-100, 100)
			btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
			top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
			pipe_list.append(btm_pipe)
			pipe_list.append(top_pipe)
			pipe_group.add(btm_pipe)
			pipe_group.add(top_pipe)
			last_pipe = time_now

		if pipe_list:
			pipe_group.update()



	update_ui()
	return reward,game_over,score


