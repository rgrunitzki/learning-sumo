'''
Created on Nov 23, 2013

@author: rgrunitzki
'''
import random
from random import Random

class QLearning(object):
    '''
    QLearning Class
    '''
    episodes = 0
    alpha = 0
    gamma = 0
    epislon = 0
    epislon_rate = 0
        
    def __init__(self, episodes, alpha, gamma, epislon, epislon_rate):
        '''
        QLearnign Constructor
        '''
        self.episodes = episodes
        self.alpha = alpha
        self.gamma = gamma
        self.epislon = epislon
        self.epislon_rate = epislon_rate
    
    def decreases_epislon(self):
        self.epislon = self.epislon*self.epislon_rate
        
    def next_action(self, mdp, id_next_node):
        #exploration
        if(Random.random()<self.epislon):
            #returns one action randomly
            return mdp[int(id_next_node)-1][random.randrange(0, len(mdp[int(id_next_node)-1]))]
        #exploitation
        else:
            #returns the action that minimize the travel_time the reward
            return (min(mdp[int(id_next_node)-1], key=lambda x:x[1]))
    