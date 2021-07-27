import os
import struct
import logging
import sys

PKGSIZE = 1024

def to_uint(data,size,isnegative = 0):
    if isnegative:
        if size == 1:
            return struct.unpack("<b",data)[0]
            
    if size == 1:
        return struct.unpack("<B",data)[0]
    elif size == 2:
        return struct.unpack("<H",data)[0]
    elif size  == 4:
        return struct.unpack("<I",data)[0]

def print_data(data):

    
    for i in range(0,len(data)):
        if i%16 == 0:
            print("%08x "%(i),end="")
        print("%02x "%data[i],end="")
        if i%16 == 15:
            print("")
    print("\n\n")
    
class StructA1():
    def __init__(self,data):
        if len(data) != 8:
            logging.error("a1 data len failed %d",len(data))
            exit(0)
                    
        self.time = to_uint(data[0:4],4) - 127
        self.x = to_uint(data[4:5],1) - 127
        self.y = to_uint(data[5:6],1) - 127
        self.z = to_uint(data[6:7],1) - 127
        self.status = to_uint(data[7:8],1)
        
    def to_string(self,hasattribute=0):
        if hasattribute:
            return "time            x       y     z     status"
        else:
            return "%08d  %d  %d  %d  %d"%(self.time,self.x,self.y,self.z,self.status)
    
    def get_type(self):
        return "A1"
        
class StructC1():
    def __init__(self,data):
        if len(data) != 36:
            logging.error("c1 data len failed %d",len(data))
            exit(0)
        # self.eventtype = to_uint(data[0:2],2)
        # self.time = []
        # for i in range(0,6):
            # self.time.append(to_uint(data[i+2:i+3],1))
        
        # self.aacx = to_u
        
    def to_string(self,hasattribute=0):
        return " "
    
    def get_type(self):
        return "C1"
        
class StructC2():
    def __init__(self,data):
        if len(data) != 28:
            logging.error("c2 data len failed %d",len(data))
            exit(0)
                        
        self.time = to_uint(data[0:4],4)
        self.lat = to_uint(data[4:8],4)
        self.lon = to_uint(data[8:12],4)
        self.latDesc = to_uint(data[12:13],1)
        self.lonDesc = to_uint(data[13:14],1)
        self.elevation = to_uint(data[14:16],2)
        self.speed = to_uint(data[16:18],2)
        self.azimuth = to_uint(data[18:20],2)
        self.status = to_uint(data[20:21],1)
        self.gsanum = to_uint(data[21:22],1)
        self.gsapdop = to_uint(data[22:23],1)
        self.gsvnum = to_uint(data[23:27],4)
        
    def to_string(self,has_attr = 0):
        if has_attr:
            return "time         lat        lon    latDesc  lonDesc  elevation    speed azimuth status gsanum gsapdop gsvnum"
        return "%08d  %08d %08d %08d %08d"%(self.time,self.lat,self.lon,self.latDesc,self.lonDesc) + \
            "  %04d       %04d   %04d     %02d      %02d     %02d       0x%08x"%(self.elevation,self.speed,self.azimuth,self.status,self.gsanum,self.gsapdop,self.gsvnum)
    def get_type(self):
        return "C2"
        
def save_file(liststructs,mode="w"):
    if liststructs:
        fd = None
        for uint in liststructs:
            if fd == None:
                fname = "struct_"+uint.get_type()+".txt"
                print("save to ",fname)
                fd = open(fname,mode)
                fd.write(uint.to_string(1)+"\t\n")
            fd.write(uint.to_string()+"\t\n")
            
        fd.close()
   
def get_struct_count(stype,data):
    if stype == 0xA1 or stype == 0xC2:
        return data >> (2+8)
        
    tt = data>>(6+8) & 0x3
    if tt == 0:
        return 1
    elif tt == 1:
        return 10
    elif tt == 2:
        return 25
    elif tt == 3:
        return 50
        
def get_struct_totlen(stype,data):
    if stype == 0xA1 or stype == 0xC2:
        return data & 0x03ff 
    else:
        return data & 0x3fff
    
PKGSIZE = 1024

def read_structs(data,curpos,lista1,listc1,listc2):
    curlen = 0
    packlen = len(data)
    while curlen < packlen:
        structtype = to_uint(data[curlen:curlen+2],2)
        if structtype == 0:
            break
        structcount = get_struct_count(structtype,to_uint(data[curlen+2:curlen+4],2))
        totlen = get_struct_totlen(structtype,to_uint(data[curlen+2:curlen+4],2))              
        structlen = totlen//structcount
        
        cur = curlen + 4
        # print("curpos:0x%08x type:0x%04x totlen:0x%x count:0x%02x structlen:%d  0x%x"%(curpos+curlen, structtype,totlen,structcount,structlen,to_uint(data[curlen+2:curlen+4],2)))
        for i in range(0,structcount):
            dev = None
            sdata = data[cur + i*structlen:cur +(i+1)*structlen]
            if structtype == 0xA1:
                dev = StructA1(sdata)
                lista1.append(dev)
            elif structtype == 0xC1:
                dev = StructC1(sdata)
                listc1.append(dev)
            elif structtype == 0xC2:
                dev = StructC2(sdata)
                listc2.append(dev)
            else:
                logging.error("not supported type:0x%x curpos:0x%x",structtype,curpos+curlen)
                print_data(data)
                exit(0)
                
        curlen += totlen + 4 
        
