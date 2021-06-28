import os
import socket
import threading
import logging
import struct
import time
import numpy as np
import matplotlib.pyplot as plt
inputchar = None

class InputWait(threading.Thread):
    def __init__(self):
        super().__init__()
        
    def run(self):
        global inputchar
        while True:
            c = input()
            inputchar = c  
            if c == " ":
                os.kill(os.getpid(), -9)

class DataType01():
    def __init__(self,data):        
        a = struct.unpack("<hhhI",data)
        self.x = a[0]/2048  
        self.y = a[1]/2048 -5
        self.z = a[2]/2048
        self.ticks = a[3]
        print(a)
        
    def get_time(self):
        return self.ticks
     
def draw_type_01(lt):
    tm = []
    x= []
    y = []
    z = []
    
    for cls in lt:
        tm.append(cls.get_time())
        x.append(cls.x)
        y.append(cls.y)
        z.append(cls.z)
    
    plt.ylim((-10,10))
    if len(lt) > 20:
        plt.xlim((lt[0].get_time(),lt[len(lt)-1].get_time()))
    
    if inputchar == "2":
        plt.plot(tm,y,label="y")
    elif inputchar == "3":
        plt.plot(tm,z,label="z")
    elif inputchar == "4":
        plt.plot(tm,x,label="x")    
        plt.plot(tm,y,label="y")
        plt.plot(tm,z,label="z")
    else:    
        plt.plot(tm,x,label="x")    
    
def print_data(data):
    sstr =""
    for i in data:
        sstr += " %02x"%i
    print(sstr)
    
def main():
    plt.ion()

    InputWait().start()
    
    sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sk.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    
    sk.bind(("0.0.0.0",8837))
    sk.listen(1)
    client,addr = sk.accept()
    print("connect from",addr)
   
    lastdraw_time = 0
    listtype1 = []
    while True:
        data = client.recv(1)
        nowtime = time.time()
        if not data:
            continue
            
        if data[0] != 0x7e:
            logging.error("data header failed");
            continue
        data = client.recv(2)
        datalen = struct.unpack("!H",data)[0]
        if (datalen > 100):
            logging.error("data length failed");
            continue
        data = client.recv(datalen+1)
        if data[len(data)-1] != 0x7d:
            logging.error("data tail failed")
            continue
        data = data[:-1]
                
        array = struct.unpack("H",data[0:2])
        data = data[2:]
        itype = array[0]
        if itype == 0x1:     
            listtype1.append(DataType01(data))
        else:
            logging.error("not supported type %x",itype)
        
        # draw it
        if inputchar != 's':
            while( len(listtype1) > 5000):
                listtype1.pop(0)
          
            if (nowtime - lastdraw_time > 1):
                lastdraw_time = nowtime
                draw_type_01(listtype1)        
                plt.pause(0.005)
            
main()