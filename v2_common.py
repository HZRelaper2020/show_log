import os
import struct
import logging
import sys
import matplotlib.pyplot as plt

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

def text_read_param():
    fd = open("1.txt")
    times = 0
    oldticks = 0
    
    start_count = 0
    while True:
        times += 1
        line = fd.readline()
        if not line:
            break   
        line=line.strip()
        if not line:
            continue
            
        line = line.split(";")
        line = line[0]
        
        stype = line.split()[0]
        sname = line.split()[1].split("[")[0]
        snumber = 1
        if line.find("[") > -1:
            txt = str(eval(re.search("\[(.*)\]",line)[0]))   
            snumber = int(re.search("\d+",txt)[0])
        # print("%-10s %-15s %-10d"%(stype,sname,snumber))
        
        
        stype = stype.lower()
        sname = sname.lower()
        
        perbyte = 0
        pstr = ""
        if stype == "uint8_t":
            perbyte = 1
            if snumber == 1:
                pstr = "self.%s = to_uint(data[%d:%d],%d)"%(sname,start_count,start_count+perbyte,perbyte)                
            else:
                pstr = "self.%s = data[%d:%d]"%(sname,start_count,start_count+snumber)
            
        elif stype == "uint16_t":
            perbyte = 2
            if snumber == 1:
                pstr = "self.%s = to_uint(data[%d:%d],%d)"%(sname,start_count,start_count+perbyte,perbyte)                
            else:
                print("not supoorted uint16 array")
                exit(0)
            
        elif stype == "uint32_t":
            perbyte = 4
            if snumber == 1:
                pstr = "self.%s = to_uint(data[%d:%d],%d)"%(sname,start_count,start_count+perbyte,perbyte)                
            else:
                print("not supoorted uint32 array")
                exit(0)            
        else:
            print("not supported type")
            break
        
        start_count += perbyte * snumber
        print(pstr)
        
    fd.close()
    
def print_data(data,perr=1):

    totline = ""
    oneline = ""
    for i in range(0,len(data)):
        if i%16 == 0:
            oneline +="%08x "%(i)
        
        oneline += "%02x "%data[i]
        if i%16 == 15:
            if perr:
                logging.error(oneline)
            else:
                totline += oneline + "\n"
            oneline = ""
    
    if perr:
        logging.error(" \n")
    
    if not perr:
        return totline

def exit_app(code=0):
    plt.clf()
    raise Exception("my exception")
    # exit(code)
    
class StructA1():
    def __init__(self,data):
        if len(data) != 8:
            logging.error("a1 data len failed %d",len(data))
            exit_app(0)
                    
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

class StructA3():
    def __init__(self,data,stype="A3"):
        if len(data) != 332:
            logging.error("c3 data len failed %d",len(data))
            exit_app(0)
        
        self.stype = stype
        # check sum        
        self.chksum = to_uint(data[0:2],2)
        self.acc_x = data[2:128]
        self.acc_y = data[128:254]
        self.delta_vx = data[254:280]
        self.delta_vy = data[280:306]
        self.max_delta_vx = to_uint(data[306:307],1)
        self.max_delta_vy = to_uint(data[307:308],1)
        self.max_delta_vxy2 = to_uint(data[308:310],2)
        self.event_set = to_uint(data[310:311],1)
        self.event_lock = to_uint(data[311:312],1)
        self.time_t0 = data[312:318]
        self.t_end = to_uint(data[318:319],1)
        self.t_max_delta_vx = to_uint(data[319:320],1)
        self.tick_t0 = to_uint(data[320:324],4)
        self.t_max_delta_vy = to_uint(data[324:325],1)
        self.t_max_delta_vxy2 = to_uint(data[325:326],1)
        self.t_flag_clip_x = to_uint(data[326:327],1)
        self.t_flag_clip_y = to_uint(data[327:328],1)
        
    def to_string(self,hasattribute=0):
        if hasattribute:
            return ""
        else:
            totc = ""
            totc += "acc_x \n"
            totc += print_data(self.acc_x,perr = 0)
            totc += " \n" + "acc_y" +"\n"
            totc += print_data(self.acc_y,0)
            totc += "\n" + "delta_vx"+"\n"
            totc += print_data(self.delta_vx,0)
            totc += "\n" + "delta_vy"+"\n"
            totc += print_data(self.delta_vy,0)
            totc +="\n" + "max_delta_vx 0x%x \n"%self.max_delta_vx
            totc +="\n" + "max_delta_vy 0x%x \n"%self.max_delta_vy
            totc +="\n" + "max_delta_vxy2 0x%x \n"%self.max_delta_vxy2
            totc +="\n" + "event_set 0x%x \n"%self.event_set
            totc +="\n" + "event_lock 0x%x \n"%self.event_lock
            totc += "\n" + "time_t0"+"\n"
            totc += print_data(self.time_t0,0)
            totc +="\n" + "t_end 0x%x \n"%self.t_end
            totc +="\n" + "t_max_delta_vx 0x%x \n"%self.t_max_delta_vx
            totc +="\n" + "tick_t0 0x%x \n"%self.tick_t0
            totc +="\n" + "t_max_delta_vy 0x%x \n"%self.t_max_delta_vy
            totc +="\n" + "t_max_delta_vxy2 0x%x \n"%self.t_max_delta_vxy2
            totc +="\n" + "t_flag_clip_x 0x%x \n"%self.t_flag_clip_x
            totc +="\n" + "t_flag_clip_y 0x%x \n"%self.t_flag_clip_y
            
            totc += "next struct......................................................\n"
            return totc
    
    def get_type(self):
        return self.stype
        
class StructC1():
    def __init__(self,data):
        if len(data) != 36:
            logging.error("c1 data len failed %d",len(data))
            exit_app(0)
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
            exit_app(0)
                        
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
    if stype == 0xA1 or stype == 0xC2 or stype == 0xA3 or stype == 0xA2 or stype == 0xA4:
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
    if stype == 0xA1 or stype == 0xC2 or stype == 0xA3 or stype == 0xA2 or stype == 0xA4:
        return data & 0x03ff 
    else:
        return data & 0x3fff
    
PKGSIZE = 1024

def read_structs(data,curpos,lista1,listc1,listc2,lista2=None,lista3=None,lista4=None):
    curlen = 0
    packlen = len(data)
    while curlen < packlen:
        structtype = to_uint(data[curlen:curlen+2],2)
        if structtype == 0:
            break
        structcount = get_struct_count(structtype,to_uint(data[curlen+2:curlen+4],2))
        totlen = get_struct_totlen(structtype,to_uint(data[curlen+2:curlen+4],2))              
        structlen = totlen//structcount
        #print("%02x structcount %d totlen:%d,structlen:%d"%(structtype,structcount,totlen,structlen))
        cur = curlen + 4        
        for i in range(0,structcount):
            dev = None
            sdata = data[cur + i*structlen:cur +(i+1)*structlen]
            if structtype == 0xA1:
                dev = StructA1(sdata)
                lista1.append(dev)
            elif structtype == 0xA2:
                dev = StructA3(sdata,"A2")
                if lista2 != None:
                    lista2.append(dev)
            elif structtype == 0xA3:
                dev = StructA3(sdata)
                if lista3 != None:
                    lista3.append(dev)
            elif structtype == 0xA4:
                dev = StructA3(sdata,"A4")
                if lista4 != None:
                    lista4.append(dev)
            elif structtype == 0xC1:
                dev = StructC1(sdata)
                listc1.append(dev)
            elif structtype == 0xC2:
                dev = StructC2(sdata)
                listc2.append(dev)
            else:
                logging.error("not supported type:0x%x curpos:0x%x",structtype,curpos+curlen)
                print_data(data)
                exit_app(0)
                
        curlen += totlen + 4 
       