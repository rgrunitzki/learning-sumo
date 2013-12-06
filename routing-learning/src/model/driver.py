'''
Created on Nov 23, 2013

@author: rgrunitzki
'''

class Driver(object):
    
    '''
        Driver Class
    '''
    id = '0'
    mdp = []
    origin = ''
    destination = ''
    current_link = ''
    initial_tt = 0
    link_tt = 0
    steps = 0
    isArrived = False
    isStarted = False
    isChangeRoute = True
    isUpdate = False
    isTeleported = False

    def __init__(self, ident, mdp, origin, destination, current_link, initial_tt, arrived, started):
        '''
            Driver's constructor
        '''
        self.id = ident
        self.mdp = mdp
        self.origin = origin
        self.destination = destination
        self.current_link = current_link
        self.initial_tt = initial_tt
        self.isArrived = arrived
        self.isStarted = started
        
        self.isUpdate = True
        self.steps = 0
        self.isTeleported = False
        
    '''return the total travel time on simulation'''
    def get_total_travel_time(self, current_time):
        return current_time - self.initial_tt
    
    '''return the total travel time on link'''
    def get_travel_time_on_link(self, current_time):
        if(current_time - self.link_tt < 0):
            print 'treta'
        return current_time - self.link_tt
        
        
        