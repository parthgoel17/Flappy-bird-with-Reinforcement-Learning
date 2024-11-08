import torch
import random
import numpy as np 
from collections import deque,namedtuple
from yo import *
from model import Linear_QNet,QTrainer
from helper import plot

def get_horizontal_distance():
    if len(pipe_list) > 0:
        bird_center_x = flappy.rect.centerx
        upcoming_pipes = [pipe for pipe in pipe_list if pipe.rect.right > bird_center_x]
        if upcoming_pipes:
            nearest_pipe = min(upcoming_pipes, key=lambda pipe: abs(pipe.rect.centerx - bird_center_x))
            nearest_pipe_center_x = nearest_pipe.rect.centerx
            horizontal_dist = nearest_pipe_center_x - bird_center_x
            return horizontal_dist

    return 0

def get_vertical_distance():
    if len(pipe_list) > 0:
        bird_center_y = flappy.rect.centery
        upcoming_pipes = [pipe for pipe in pipe_list if pipe.rect.right > flappy.rect.centerx]
        if upcoming_pipes:
            nearest_pipe = min(upcoming_pipes, key=lambda pipe: pipe.rect.centerx)
            vertical_dist = bird_center_y - (nearest_pipe.rect.midtop[1] + pipe_gap / 2)
            return vertical_dist
    return 0


MAX_MEMORY = 100000
BATCH_SIZE = 1000
LR = 0.1

class Agent:
	def __init__(self):
		self.n_games =0
		self.epsilon = 0 #randomness
		self.gamma = 0.9 #discount
		self.memory = deque(maxlen=MAX_MEMORY)
		self.model = Linear_QNet(3,256,1)
		self.trainer = QTrainer(self.model,lr=LR,gamma=self.gamma)

	def get_state(self):
		state = [get_horizontal_distance(),get_vertical_distance(),flappy.vel]
		return np.array(state,dtype=int)

	def remember(self,state,action,reward,next_state,done):
		self.memory.append((state,action,reward,next_state,done))

	def train_long_memory(self):
		if len(self.memory) > BATCH_SIZE:
			mini_sample = random.sample(self.memory,BATCH_SIZE)
		else:
			mini_sample = self.memory

		states,actions,rewards,next_states,dones = zip(*mini_sample)
		self.trainer.train_step(states,actions,rewards,next_states,dones)

	def train_short_memory(self,state,action,reward,next_state,done):
		self.trainer.train_step(state,action,reward,next_state,done)
 
	def get_action(self,state):
		self.epsilon = 80 - self.n_games
		final_move = 0
		if random.randint(0,200) < self.epsilon:
			final_move = random.randint(0,1)
		else:
			state0 = torch.tensor(state,dtype = torch.float)
			prediction = self.model(state0)
			final_move = torch.argmax(prediction).item()
		return final_move

def train():
	global score
	plot_scores = []
	plot_mean_scores = []
	total_score =0
	record = 0 
	agent = Agent()
	while True:
		state_old = agent.get_state()

		final_move = agent.get_action(state_old)

		reward,done,score = play_state(final_move)
		state_new = agent.get_state()

		agent.train_short_memory(state_old,final_move,reward,state_new,done)

		agent.remember(state_old,final_move,reward,state_new,done)
		if done:
			reset_game()
			agent.n_games += 1
			agent.train_long_memory()
			if score>record:
				record= score
				agent.model.save()
			print('Game',agent.n_games,'score',score,'record',record)

			plot_scores.append(score)
			total_score += score
			mean_score = total_score/agent.n_games
			plot_mean_scores.append(mean_score)
			plot(plot_scores,plot_mean_scores)

if __name__ == "__main__":
	train()