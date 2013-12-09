# -*- coding: utf-8 -*-
'''
Created on Nov 23, 2013

@author: rgrunitzki
'''
import traci, sumolib
from sumolib.net.edge import Edge
from sumolib.net.node import Node
import os, time, random
from xml.dom import minidom
from controller.QLearning import QLearning
from model.driver import Driver
from util import search

class Simulation(object):
    '''
    A simulation class
    '''
    net_directory = ''
    net_directory_shell = ''
    cfg_file = ''
    net_file = ''
    route_file = ''
    show_interface = True
    traci_port = 0
    sumo_options = ''
    qlearning = QLearning
    show_log = False
    drivers = []
    running_drivers = []
    max_steps = 0
    #not used on constructor
    network = ''
    mdp = []

    def __init__(self, net_directory, net_directory_shell, cfg_file, net_file, route_file, 
                 show_interface, traci_port, sumo_options, qlearning, show_log, max_steps):
        '''
        Constructor
        '''
        self.net_directory = net_directory
        self.net_directory_shell = net_directory_shell
        self.cfg_file = cfg_file
        self.net_file = net_file
        self.route_file = route_file
        self.show_interface = show_interface
        self.traci_port = traci_port
        self.sumo_options = sumo_options
        self.qlearning = qlearning
        self.show_log = show_log
        self.max_steps = max_steps
        self.drivers = range(0, self.get_vehicle_count()+1)
        self.network = sumolib.net.readNet(self.net_directory+self.net_file)      
    def get_sumo(self):
        if self.show_interface:
            return 'sumo-gui'
        else:
            return 'sumo'
    
    def run(self):
        for episode in range(0,self.qlearning.episodes):
            if (self.start_simulator(episode)):
                self.traci_connect()
                if (episode == 0):
                    self.mdp = self.init_mdp()  
                self.learning_method(episode)           
    
    def start_simulator(self, episode):
        sumo_call = self.get_sumo()  + ' -c ' + self.net_directory_shell + self.cfg_file + ' ' + self.sumo_options + str(episode) + '.xml &'
        if(os.system(sumo_call)==0):
            self.print_log('\tsimulator started')
            return True
        else:
            self.print_log('\tsimulator not started')
            return False
            
    def traci_connect(self):
        traci.init(self.traci_port)
        self.print_log('\tconnected on the traci')
    
    def traci_disconnect(self):
        traci.close()
        self.print_log('\tdisconnected of the traci')
    
    def print_log(self, msg):
        if(self.show_log):
            print msg
         
    '''Returns a Initialized mdp according to the network'''
    def init_mdp_old(self):    
        #get all network nodes
        node_count = len(traci.junction.getIDList())
        mdp = []        
        for node in range(0, node_count):
            no = (self.network.getNode(str(node+1)))
            list_edges = Node.getOutgoing(no)
            #for each node find all outgoing edges
            states = []
            for l in list_edges:
                #add the actions (edges) to the states (nodes): edge-id, q-value, reward (travel time on link)
                states.append([str(Edge.getID(l)), 50*random.random(), 50*random.random()])
            mdp.append(states)
        return mdp
    
    '''Returns a Initialized mdp according to the network'''
    def init_mdp(self):    
        #get all network nodes
        junction_list = traci.junction.getIDList()
        usefull = [i for i in junction_list if not ':' in i]
        mdp = dict([(x, []) for x in usefull])
        for node in usefull:
            no = (self.network.getNode(node))
            list_edges = Node.getOutgoing(no)
            states = dict([(x.getID(), []) for x in list_edges if not ':' in x.getID()])
            #for each node find all outgoing edgesTrue
            for e in list_edges:
                #add the actions (edges) to the states (nodes): edge-id, q-value, reward (travel time on link)
                states[e.getID()] = ([10*random.random(), 10*random.random()])
            mdp[node] = states
        return mdp

    def get_vehicle_count(self):
        xmldoc = minidom.parse(self.net_directory+self.route_file)
        itemlist = xmldoc.getElementsByTagName('vehicle') 
        return len(itemlist)
    
    def get_time(self):
        return traci.simulation.getCurrentTime()/1000
    
    def get_destination_node(self, edge_id):
        ed_atual = (self.network.getEdge(edge_id))
        return sumolib.net.edge.Edge.getToNode(ed_atual)
    
    def get_origin_node(self, edge_id):
        ed_atual = (self.network.getEdge(edge_id))
        return sumolib.net.edge.Edge.getFromNode(ed_atual)
    
    def return_route(self, origin, destination):
        rude_rotue = search.dijkstra(self.network,
                                     self.network.getEdge(origin), 
                                     self.network.getEdge(destination))
        route_ids = [e.getID() for e in rude_rotue]
        final_route = [e.encode('utf-8') for e in route_ids]
        return final_route
    
    def return_best_action(self, driver, id_next_node):
        keys = self.drivers[int(driver)].mdp[id_next_node].keys()
        action_key = ''
        minimo = 100000000000
        for k in keys:
            if(self.drivers[int(driver)].mdp[id_next_node][k][0]< minimo):
                minimo = self.drivers[int(driver)].mdp[id_next_node][k][0]
                action_key = k
        return action_key
    
    def isEdge(self, edge_id):
        try:
            self.network.getEdge(edge_id)
            return True
        except:
            return False
    
    def learning_method(self, episode):
        #all traci calls
        total_arrived_vehicle = 0
        total_departed_vehicle = 0
        total_time = 0
        

        
        while True:                        
            #update the total arrived and departed vehicles
            departed_list = traci.simulation.getDepartedIDList()
            arrived_list = traci.simulation.getArrivedIDList()
            total_departed_vehicle += len(departed_list)
            total_arrived_vehicle += len(arrived_list)
            
            #stop condition
            if(total_arrived_vehicle == total_departed_vehicle) and (total_departed_vehicle >0):
                break
            
            #create the drivers when they are departed
            if(episode == 0):
                for vehID in departed_list:
                    route = traci.vehicle.getRoute(vehID)
                    self.drivers[int(vehID)] = Driver(vehID, self.mdp, route[0], route[len(route)-1], 
                                                      traci.lane.getEdgeID(traci.vehicle.getLaneID(vehID)), 
                                                      self.get_time(), False, True)
                    self.drivers[int(vehID)].link_tt = self.get_time()
                    self.running_drivers.append(vehID)
            #set the drivers parameters
            else:
                for vehID in departed_list:
                    try:
                        self.drivers[int(vehID)].isArrived = False
                        self.drivers[int(vehID)].isStarted = True
                        self.drivers[int(vehID)].current_link = traci.lane.getEdgeID(traci.vehicle.getLaneID(vehID))
                        self.drivers[int(vehID)].link_tt = self.get_time() 
                        self.drivers[int(vehID)].initial_tt = self.get_time()
                        self.drivers[int(vehID)].steps = 0
                        self.drivers[int(vehID)].isChangeRoute = True
                        self.drivers[int(vehID)].isUpdate = True
                        self.drivers[int(vehID)].isTeleported = False
                        
                        self.running_drivers.append(vehID)
                    except:
                        print 'pau doido!'
            
            #update the arrived cars
            for vehID in arrived_list:
                self.drivers[int(vehID)].isArrived = True
                self.drivers[int(vehID)].isStarted = False
                #este parametro devo atualizar quando ele for sair da simulação
                self.drivers[int(vehID)].total_tt = self.get_time() - self.drivers[int(vehID)].initial_tt
            
            #solving teleporting
            total_teleporting_vehicle = traci.simulation.getStartingTeleportIDList()
            for vehID in total_teleporting_vehicle:
                self.drivers[int(vehID)].isTeleported = True
            total_end_teleporting_vehicle = traci.simulation.getEndingTeleportIDList()
            for vehID in total_end_teleporting_vehicle:
                self.drivers[int(vehID)].isTeleported = True
            
            
            #
            tempo = time.time()
            #            
            for driver in filter(lambda d:self.drivers[int(d)].isStarted and not self.drivers[int(d)].isArrived and not self.drivers[int(d)].isTeleported, self.running_drivers):
                self.process_vehicle(driver)
            total_time += time.time()-tempo
            #
            traci.simulationStep()     
        print '\tsimulation',episode, 'finished in', total_time, 'seconds',  'steps', self.drivers[0].steps, self.drivers[1].steps
        self.traci_disconnect()
    def print_vehicle(self, driver):
        print driver

    def process_vehicle(self, driver):                
                id_current_edge = traci.lane.getEdgeID(traci.vehicle.getLaneID(self.drivers[int(driver)].id))
                #Driver needs a new route
                if( self.isEdge(id_current_edge) and
                        (self.drivers[int(driver)].current_link == id_current_edge) and
                        (self.drivers[int(driver)].current_link!= self.drivers[int(driver)].destination) and
                        (self.drivers[int(driver)].isUpdate)):
                                            
                    next_node = self.get_destination_node(id_current_edge)
                    id_next_node = Node.getID(next_node)
                    action_key = ''
                    #next action,
                    if(random.random()<self.qlearning.epislon):
                        #returns one action randomly
                        action_key = self.drivers[int(driver)].mdp[id_next_node].keys()[random.randint(0, len(self.drivers[int(driver)].mdp[id_next_node].keys())-1)]
                        
                    #exploitation
                    else:
                        #returns the action that minimize the travel_time the reward        
                        action_key = self.return_best_action(driver, id_next_node)

                    #update q-table
                    #current q_value
                    current_q_value = self.drivers[int(driver)].mdp[id_next_node][action_key][0]
                    #action reward
                    reward = self.drivers[int(driver)].mdp[id_next_node][action_key][1]
                    
                    if(reward <0):
                        print 'reward negativo!'
                        
                    #node maximizes the reward on action
                    future_node = self.get_destination_node(action_key)
                    #id node maximizes the reward on action
                    id_new_future_edge = Node.getID(future_node)
                    
                    #q_value of the best action
                    best_action = self.drivers[int(driver)].mdp[id_new_future_edge][self.return_best_action(driver, id_new_future_edge)][0]
                    
                    #new q_value
                    q_value = ((1-self.qlearning.alpha)*current_q_value 
                                        + self.qlearning.alpha*(abs(reward)+self.qlearning.gamma*best_action))
                    
                    #updates q_value
                    self.drivers[int(driver)].mdp[id_next_node][action_key][0] = q_value
                    
                    #if it's ok, update the route just on dijkstra
                    new_route = self.return_route(self.drivers[int(driver)].current_link, action_key)
                      
                    #insert the new route in the vehicle
                    traci.vehicle.setRoute(self.drivers[int(driver)].id, new_route)                     
                    #update the driver steps
                    self.drivers[int(driver)].steps += 1
                    self.drivers[int(driver)].isUpdate = False                        
                
                #update the travel time on the last action
                elif(self.isEdge(id_current_edge) and (self.drivers[int(driver)].current_link!=id_current_edge)):
                    origin_node = self.get_origin_node(self.drivers[int(driver)].current_link).getID()
                    
                    for action in self.drivers[int(driver)].mdp[origin_node]:
                        #set the total travel time on link
                        if str(action) == str(self.drivers[int(driver)].current_link):
                            link_tt = self.drivers[int(driver)].get_travel_time_on_link(self.get_time())
                            if link_tt < 0:
                                print 'errado'
                            self.drivers[int(driver)].mdp[origin_node][action][1] = link_tt
                            break
                    #update the drivers properties
                    self.drivers[int(driver)].current_link = id_current_edge
                    self.drivers[int(driver)].link_tt = self.get_time()
                    self.drivers[int(driver)].isUpdate = True
                
                #The car is arriving on the destination
                elif(self.isEdge(id_current_edge) and
                    (self.drivers[int(driver)].current_link==id_current_edge) and 
                    (self.drivers[int(driver)].current_link == self.drivers[int(driver)].destination)):
                    
                    last_node = self.get_origin_node(self.drivers[int(driver)].current_link)
                    next_node = self.get_destination_node(self.drivers[int(driver)].current_link).getID()

                    for action in self.drivers[int(driver)].mdp[last_node.getID()].keys():
                            if(action==str(self.drivers[int(driver)].current_link)):
                                '''in the future we need change this for the total travel time*-1'''
                                #total_tt = - self.drivers[int(driver)].get_total_travel_time(self.get_time())
                                self.drivers[int(driver)].mdp[last_node.getID()][action][0] = -200
                                break
                                    
                    #driver rechead his goal
                    #print '\t\tpassos ', self.drivers[int(driver)].steps
                    self.drivers[int(driver)].isArrived = True
                    self.running_drivers.remove(self.drivers[int(driver)].id)