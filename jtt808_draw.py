import threading
# import pygame
# import matplotlib
# matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np

drawer = None
# class Jtt808DrawModel(threading.Thread):
    # def __init__(self):
        # super().__init__()
        # self.done = False
        # self.winsize = (480,320)
        # self.title = "do position"
        
        # self.started = False
        
    # def run(self):
        # FPSClock=pygame.time.Clock()
        # FPSClock.tick(30)
        
        # pygame.init()  
        # scr = pygame.display.set_mode(self.winsize)  
        # scr.fill([255,255,255])
        # pygame.display.set_caption(self.title)
        
        # while not self.done:
            # for event in pygame.event.get():
                # if event.type == pygame.QUIT:  
                    # self.done = True 
            # pygame.display.update()
            
    # def draw_position(self,gps):
        # if not self.started:
            # self.start()
            # self.started = True
            
class Jtt808DrawModel():
    def __init__(self):
        self.arg1 = []
        self.arg2 = []
        self.arg3 = []
        self.arg4 = []
        self.arg5 = []
        self.arg6 = []
        self.arg7 = []
        self.arg8 = []
        self.arg9 = []
        self.starttime = 0
        plt.ion()
        
        self.gpslist = []
        self.a1list = []
        self.c1list = []
    # def __del__(self):
        # plt.close()
    def clear_args(self):
        self.arg1.clear()
        self.arg2.clear()
        self.arg3.clear()
        self.arg4.clear()
        self.arg5.clear()
        self.arg6.clear()
        self.arg7.clear()
        self.arg8.clear()
        self.arg9.clear()
    
    def clear_all(self):
        self.clear_args()
        self.gpslist.clear()
        self.c1list.clear()
        self.a1list.clear()
        
        plt.close()
        
    # paramtype 1:position  2:3轴   3：六轴
    def add_param(self,param,paramtype):        
        lst = None        
        if paramtype == 1:
            lst = self.gpslist
        elif paramtype == 2:
            lst = self.a1list
        elif paramtype == 3:
            lst = self.c1list
            
        if lst != None:            
            lst.append(param)            
            if len(lst) > 300: # max length 300
                lst.pop(0)
        
    def draw_position(self):
        self.clear_args()
        for gps in self.gpslist:
            # if not self.starttime:
                # self.starttime = gps.get_time()
                        
            # time = gps.get_time() - self.starttime
            self.arg1.append(gps.get_time())
            self.arg2.append(gps.longitude)
            self.arg3.append(gps.latitude)
         
        plt.clf()
        # plt.figure(1)        
        plt.plot(self.arg1,self.arg2,label="logitude")
        plt.plot(self.arg1,self.arg3,label="latitude")
        # print(self.arg1,self.arg2,self.arg3)
        plt.legend()    
        plt.ioff()
    
    def draw_accelration_a1(self):
        self.clear_args()
        for a1 in self.a1list:
            self.arg1.append(a1.get_time())
            self.arg2.append(a1.x)
            self.arg3.append(a1.y)
            self.arg4.append(a1.z)
            
        plt.clf()
        
        plt.plot(self.arg1,self.arg2,label="x")
        plt.plot(self.arg1,self.arg3,label="y")
        plt.plot(self.arg1,self.arg4,label="z")        
        plt.legend()
        plt.ioff()
        
    def draw_accelration_c1(self):
        self.clear_args()
        for c1 in self.c1list:
            self.arg1.append(c1.get_time())
            self.arg2.append(c1.aacx)
            self.arg3.append(c1.aacy)
            self.arg4.append(c1.aacz)
        
        plt.clf()
        plt.plot(self.arg1,self.arg2,label="aacx")
        plt.plot(self.arg1,self.arg3,label="aacy")
        plt.plot(self.arg1,self.arg4,label="aacz")        
        plt.legend()
        plt.ioff()
# def main():
    # draw = Jtt808DrawModel()    
    # for i in range(0,100):
        # draw.arg1.append(i)
        # draw.arg2.append(i*i)
        # plt.clf()
        # plt.plot(draw.arg1,draw.arg2)
        # plt.pause(0.001)
        # # plt.ioff()
        
# main()