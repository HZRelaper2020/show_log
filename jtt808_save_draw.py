import logging
import os
import threading
import jtt808_structs
import jtt808_draw
import datetime

    

class Jtt808SaveDraw():
    def __init__(self):
        self.clientid = "" # for save file
        self.fd_position = None
        self.save_file_dir = "data"
        
        self.drawposition_thr = jtt808_draw.Jtt808DrawModel()
        
    def __del__(self):
        if self.fd_position:
            self.fd_position.close()
            self.fd_position = None
            
        self.drawposition_thr.done = True
    
    def set_client_id(self,clientid):
        tempstr = ""
        for i in clientid:
            tempstr += "%02x"%i;            
        self.clientid = tempstr
        
    def process_position_data(self,payload):                
        if not self.fd_position:
            filename = self.save_file_dir+"/" + datetime.datetime.now().strftime('%Y_%m_%d__%H_%M_%S')+"_%s__"+self.clientid+".txt"            
            self.fd_position = open(filename%"gps","w")
                
            self.drawposition_thr.start()
            
        gps = jtt808_structs.GpsStruct(payload)
        self.save_file(self.fd_position,gps.to_string())
        
    def draw_position(self,GpsCls):
        pass
    
    def save_file(self,fd,data):
        pass
        
    