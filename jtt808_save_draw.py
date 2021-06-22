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
        self.fd_acceleration_a1 = None
        self.fd_acceleration_c1 = None
        self.fd_other = None
        
        self.save_file_dir = "data"
        
        self.drawer = jtt808_draw.drawer
        
    def __del__(self):
        if self.fd_position:
            self.fd_position.close()
            self.fd_position = None
        if self.fd_acceleration_a1:
            self.fd_acceleration_a1.close()
            self.fd_acceleration_a1 = None
        if self.fd_acceleration_c1:
            self.fd_acceleration_c1.close()
            self.fd_acceleration_c1 = None
        if self.fd_other:
            self.fd_other.close()
            self.fd_other = None
            
    def set_client_id(self,clientid):
        tempstr = ""
        for i in clientid:
            tempstr += "%02x"%i;            
        self.clientid = tempstr
        
    def get_create_filename(self,param):
        return (self.save_file_dir+"/" + datetime.datetime.now().strftime('%Y_%m_%d__%H_%M_%S')+"_%s__"+self.clientid+".txt")%param

    def process_other_data(self,payload):
        if not self.fd_other:
            self.fd_other = open(self.get_create_filename("other"),"wb")
        islast = payload[0]
        payload = payload[30:]
        
        self.fd_other.write(payload)
        print(len(payload),islast)
        if islast:
            self.fd_other.close()
            self.fd_other = None
            
    def process_position_data(self,payload): 
        gps = jtt808_structs.GpsStruct(payload)        
        
        if not self.fd_position:
            filename = self.get_create_filename("gps")           
            self.fd_position = open(filename,"w")                
            self.save_file(self.fd_position,gps.to_string(1))
            
        self.save_file(self.fd_position,gps.to_string())
        self.drawer.add_param(gps,1)
    
    def process_accelration_a1_data(self,payload):
        acce = jtt808_structs.AcclerationA1Struct(payload)
        if not self.fd_acceleration_a1:
            filename = self.get_create_filename("acceleration_a1")
            self.fd_acceleration_a1 = open(filename,"w")
            self.save_file(self.fd_acceleration_a1,acce.to_string(1))
        self.save_file(self.fd_acceleration_a1,acce.to_string())
        self.drawer.add_param(acce,2)
        
    def process_accelration_c1_data(self,payload):
        acce = jtt808_structs.AcclerationC1Struct(payload)
        if not self.fd_acceleration_c1:
            filename = self.get_create_filename("acceleration_c1")
            self.fd_acceleration_c1 = open(filename,"w")
            self.save_file(self.fd_acceleration_c1,acce.to_string(1))
        self.save_file(self.fd_acceleration_c1,acce.to_string())
        self.drawer.add_param(acce,3)
        
    def save_file(self,fd,data):
        if data:
            fd.write(data+"\t\n")