# -*- coding: utf-8 -*-
'''
Created on Nov 27, 2013

@author: rgrunitzki
'''

import xml.etree.ElementTree as ET

episodes = 200
file_name = 'summary_'
local = '../../network/grid/summary/10'
def get_average():
    
    #average
    time = 0
    loaded = 0
    emitted = 0
    waiting = 0
    ended = 0
    meanWaitingTime = 0
    meanTravelTime = 0
    duration = 0
    
    #total plots
    total_time = []
    total_loaded = []
    total_emitted = []
    total_waiting = []
    total_ended = []
    total_meanWaitingTime = []
    total_meanTravelTime = []
    total_duration = []
    for i in range(0, episodes):
        tree = ET.parse(local+'/summary_'+str(i)+'.xml')
        root = tree.getroot()
        step = root.findall('step')[len(root.findall('step'))-1]
        
        time += float(step.get('time'))
        loaded += float(step.get('loaded'))
        emitted += float(step.get('emitted'))
        waiting += float(step.get('waiting'))
        ended += float(step.get('ended'))
        meanWaitingTime += float(step.get('meanWaitingTime'))
        meanTravelTime += float(step.get('meanTravelTime'))
        duration += float(step.get('duration'))
        
        total_time.append(float(step.get('time')))
        total_loaded .append(float(step.get('loaded')))
        total_emitted.append(float(step.get('emitted')))
        total_waiting.append(float(step.get('waiting')))
        total_ended.append(float(step.get('ended')))
        total_meanWaitingTime.append(float(step.get('meanWaitingTime')))
        total_meanTravelTime.append(float(step.get('meanTravelTime')))
        total_duration.append(float(step.get('duration')))
    
    print 'inicio'
    #gera o csv com as médias
    average_file = open(local+'/average.csv', 'w')
    average_file.write('time\tloaded\temitted\twaiting\tended\tmeanWaitingTime\tmeanTravelTime\tduration\n')
    average_file.write(str(time/episodes) + '\t' + str(loaded/episodes) + '\t' + str(emitted/episodes) + '\t' + str(waiting/episodes) + 
                       '\t' + str(ended/episodes) + '\t' + str(meanWaitingTime/episodes) + '\t' + str(meanTravelTime/episodes) + '\t' + str(duration/episodes))
    average_file.close() 
    
    #gera o arquivo final
    final_file = open(local+'/final.csv', 'w')
    final_file.write('episode\ttime\tloaded\temitted\twaiting\tended\tmeanWaitingTime\tmeanTravelTime\tduration\n')
    
    for i in range(0, episodes):
        print i
        final_file.write(str(i) + '\t' + str(total_time[i]) + '\t' + str(total_loaded[i]) + '\t' + str(total_emitted[i]) + '\t' 
                         + str(total_waiting[i]) +  '\t' + str(total_ended[i]) + '\t' + str(total_meanWaitingTime[i]) 
                         + '\t' + str(total_meanTravelTime[i]) + '\t' + str(total_duration[i])+'\n')
    final_file.close()
    print 'fim'
'<step time="2164.00" loaded="2309" emitted="2080" running="2000" waiting="31" ended="80" meanWaitingTime="13.70" meanTravelTime="589.25" duration="16" />'

if __name__ == '__main__':
    get_average()