#!/usr/bin/env python
# coding: utf-8

# In[6]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import gym
import torch
import random

from collections import namedtuple
from itertools import count
from PIL import Image

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as T
from torch.utils.data import TensorDataset
import copy


# # The environment - soccer game






#creating a soccer environment that's similar to gym environments
#possible actions are N, S, E, W, and stick
#creating a soccer environment that's similar to gym environments
#possible actions are N, S, E, W, and stick
# action_map = {'N':-4,
# 'S' : 4,
# 'E' : 1,
# 'W' : -1,
# 'Stick' : 0
# }
action_map = {0:-4,
1 : 4,
2 : 1,
3 : -1,
4 : 0
}
#actions = np.array(['N','S','E','W','Stick'])
#map is 0123
#       4567    

#Each state of represented by three factors: position of player A, position of player B, and ball possession
class soccer:
    def _init_(self):
        self.goal_reward = 100
        self.action_space = 5
        self.has_ball = 'a'
        self.a_loc = 1
        self.b_loc = 1
        self.actions = np.array([0,1,2,3,4])
        self.action_map = {0:-4,
                            1 : 4,
                            2 : 1,
                            3 : -1,
                            4 : 0
                            }
    def reset(self):
        #######todo: initialize based on ball possesion and paper description
        self.a_loc, self.b_loc = np.array([1,2,5,6])[np.random.choice(4,2,replace = False)]
        # 0 means player a, 1 means player b
        players = np.array([0,1])
        self.has_ball = np.random.choice(players,1,replace = False).item()
        return self.a_loc,self.b_loc,self.has_ball
    def action_space(self):
        return (np.array([0,1,2,3,4]))
    def state_space(self):
        #8 states for player A, 7 other states for player B, two states for c
        return 8*7*2
    def take_action(self,a_action,a_current_location,b_action,b_current_location):
        a_move_to = a_current_location + action_map[a_action]
        b_move_to = b_current_location + action_map[b_action]
#         print('proposed a move to:', a_move_to)
#         print('proposed b move to:', b_move_to)
        if a_move_to < 0 or a_move_to > 7: a_move_to = a_current_location;
        if b_move_to < 0 or b_move_to > 7: b_move_to = b_current_location;
        if a_current_location == 3 and a_move_to == 4: a_move_to = a_current_location;
        if a_current_location == 4 and a_move_to == 3: a_move_to = a_current_location;
        if b_current_location == 3 and b_move_to == 4: b_move_to = b_current_location;
        if b_current_location == 4 and b_move_to == 3: b_move_to = b_current_location; 
        return (a_move_to,b_move_to)
    def sample_action(self):
        actions = np.array([0,1,2,3,4])
        return np.random.choice(actions,1,replace = False).item()
    def step(self,a_action,b_action):
        #The players’ actions are executed in random order.
        a_move_to,b_move_to = self.take_action(a_action, self.a_loc, b_action,self.b_loc)
        if np.random.random()<0.5:
            #print('A get to move first')
            # A get to move first 
            #when a player executes an action that would take it to the square occupied by the other player, 
            #possession of the ball goes to the stationary player and the move does not take place
            if a_move_to == self.b_loc:
                if self.has_ball == 0:
                    self.has_ball = 1
            else:
                self.a_loc = a_move_to
            # now b takes action
            if b_move_to == self.a_loc:
                if self.has_ball == 1:
                    self.has_ball = 0
            else:
                self.b_loc = b_move_to
        else:
            #print('B get to move first')
            # B get to move first 
            #when a player executes an action that would take it to the square occupied by the other player, 
            #possession of the ball goes to the stationary player and the move does not take place
            if b_move_to == self.a_loc:
                if self.has_ball == 1:
                    self.has_ball = 0
            else:
                self.b_loc = b_move_to
            # now a takes action
            if a_move_to == self.b_loc:
                if self.has_ball == 0:
                    self.has_ball = 1
            else:
                self.a_loc = a_move_to
        # get the rewards 
        a_reward, b_reward = 0,0
        done = False
        if self.a_loc in [0,4] and self.has_ball == 0:
            a_reward = 100
            b_reward = -100
            done = True
        elif self.a_loc in [3,7] and self.has_ball == 0:
            a_reward = -100
            b_reward = 100
            done = True
        elif self.b_loc in [3,7] and self.has_ball == 1:
            b_reward = 100
            a_reward = -100
            done = True
        elif self.b_loc in [0,4] and self.has_ball == 1:
            b_reward = -100
            a_reward = 100
            done = True
        return self.a_loc, self.b_loc,self.has_ball,a_reward,b_reward,done
    def render(self):
        #print('Current state:')
        for i in range(0,8):
            char = 'X'
            if(i == self.a_loc):
                if self.has_ball == 0:
                    char = 'A'
                else:
                    char = 'a'
            if(i == self.b_loc):
                if self.has_ball == 1:
                    char = 'B'
                else:
                    char = 'b'
            if (i==3): print(char)
            else: print(char, end ="") 
        print('\n')

