import threading
# import pygame
from matplotlib import pyplot as plt
import numpy as np

# class Jtt808DrawModel(threading.Thread):
    # def __init__(self,size,title):
        # super().__init__()
        # self.done = False
        # self.winsize = size
        # self.title = title

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
            
            
            
class Jtt808DrawModel(threading.Thread):
    def __init__(self):
        super().__init__()
        