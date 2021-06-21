import os
import sys
import struct
import socket
import threading
import re
from matplotlib import pyplot as plt
import time
import logging
import jtt808_client
import jtt808_server
import jtt808_draw

inputchar = None

class InputThread(threading.Thread):
    def __init__(self,server):
        super().__init__()
        self.server = server        
    
    def run(self):
        server = self.server
        global inputchar
        while True:        
            s= input()
            if s and s==" ":                
                os.kill(os.getpid(),-9)            
                exit(0)
            inputchar = s    

def main():
    logging.basicConfig(level = logging.INFO)
    jtt808_draw.drawer = jtt808_draw.Jtt808DrawModel() # must in main thread
    drawer = jtt808_draw.drawer
    
    server = jtt808_server.Jtt808ServerThread(8837)
    server.start()
     
    InputThread(server).start()
       
    global inputchar
    old_inputchar=None
    while True:
        if inputchar == "1": # accelrator a1
            drawer.draw_accelration_a1()
        elif inputchar == "2": # accelration c1
            drawer.draw_accelration_c1()
        elif inputchar == "3":      # gps
            drawer.draw_position() # must in main thread
        elif inputchar == "l":
            print(server.get_clients())
            inputchar = None
        elif inputchar == 'c':
            drawer.clear_all()
            inputchar = None 
        elif inputchar == 'd':
            for client in server.get_clients():
                client.do_force_quit()
                
            inputchar = None
            
        plt.pause(0.005)
        
        old_inputchar = inputchar
main()