import numpy as np
import matplotlib.pyplot as plt
import random
import struct
import sys
# https://blog.csdn.net/xyisv/article/details/80651334 画动态图
# 安装 https://www.python.org/ 下载 3.0
#  再运行  py -m pip install numpy 
#  再运行 py -m pip install matplotlib

_read_data=None

def read_data(filename,itype):
    # here read data from file
    global _read_data
    if not _read_data:
        _read_data = read_log(filename)
    data=_read_data
    
    rowtime = []
    colx = []
    coly = []
    colz = []
    
    l_pitch=[]
    l_roll=[]
    l_yaw=[]
    l_aacx=[]
    l_aacy=[]
    l_aacz=[]
    l_gyrox=[]
    l_gyroy=[]
    l_gyroz=[]
    
    l_c2=[]
    
    moduledev=None
    firsttime=-1
    
    for dev in data:
        subdev = dev.subdev        
        if itype == dev.itype:
            moduledev = dev    
            
            if dev.is_devA1():                                        
                # firsttime +=1
                # rowtime.append(firsttime)
                if firsttime < 0:
                    firsttime = subdev.get_mtime()
                
                rowtime.append(subdev.get_mtime() -firsttime)
                colx.append(subdev.get_accelerate("x"))
                coly.append(subdev.get_accelerate("y"))
                colz.append(subdev.get_accelerate("z"))
            elif dev.is_devC1():
                if firsttime < 0:
                    firsttime = subdev.get_mtime()
                
                rowtime.append(subdev.get_mtime() -firsttime)
                l_pitch.append(subdev.get_attribute("pitch"))
                l_roll.append(subdev.get_attribute("roll"))
                l_yaw.append(subdev.get_attribute("yaw"))
                l_aacx.append(subdev.get_attribute("aacx"))
                l_aacy.append(subdev.get_attribute("aacy"))
                l_aacz.append(subdev.get_attribute("aacz"))
                l_gyrox.append(subdev.get_attribute("gyrox"))
                l_gyroy.append(subdev.get_attribute("gyroy"))
                l_gyroz.append(subdev.get_attribute("gyroz"))
            elif dev.is_devC2():
                l_c2.append(dev)
               
                
    if moduledev.is_devA1():
        return {"time":rowtime,"x":colx,"y":coly,"z":colz}
    elif moduledev.is_devC1():
        return {"time":rowtime,"pitch":l_pitch,"roll":l_roll,"yaw":l_yaw,"aacx":l_aacx,"aacy":l_aacy,"aacz":l_aacz,"gyrox":l_gyrox,"gyroy":l_gyroy,"gyroz":l_gyroz}
    elif moduledev.is_devC2():
        return {"device",l_c2}



def plot_a1(filename):
    plt.rcParams['font.sans-serif']=['SimHei']
    plt.title("3轴")
    plt.xlabel("时间")
    plt.ylabel("单位")
    plt.xticks(np.arange(1, 2000, 1000))
    
    
    data = read_data(filename,0xa1)
    
    plt.plot(data['time'],data['x'],label='x')
    plt.plot(data['time'],data['y'],label='y')
    plt.plot(data['time'],data['z'],label='z')
    
    plt.legend()
    plt.grid()
    plt.show()

def plot_c1(filename):
    plt.rcParams['font.sans-serif']=['SimHei']
    plt.title("6轴")
    plt.xlabel("时间")
    plt.ylabel("单位")
    plt.xticks(np.arange(1, 2000, 1000))
    
    
    data = read_data(filename,0xc1)    
    plt.plot(data['time'],data['pitch'],label='pitch')
    plt.plot(data['time'],data['roll'],label='roll')
    plt.plot(data['time'],data['yaw'],label='yaw')
    plt.plot(data['time'],data['aacx'],label='aacx')
    plt.plot(data['time'],data['aacy'],label='aacy')
    plt.plot(data['time'],data['aacz'],label='aacz')
    plt.plot(data['time'],data['gyrox'],label='gyrox')
    plt.plot(data['time'],data['gyroy'],label='gyroy')
    plt.plot(data['time'],data['gyroz'],label='gyroz')    
    
    plt.legend()
    plt.grid()
    plt.show()
    
def main():
    if len(sys.argv) < 3:
        print("inputfile num")
        exit(0)
    filename = sys.argv[1]
    num = int(sys.argv[2])
    
    if num == 0:    
        plot_a1(filename)
    elif num ==1:
        plot_c1(filename)

def to_uint(data,bytecount):
    ret=0
    for i in range(0,bytecount):
        ret += data[i] << i*8        
    return ret

def to_int(data,bytecount):    
    ret = 0
    if bytecount ==1:
        ret = data[0]
        if (ret > 127):
            ret= -(~ret + 1 &0xff)
    elif bytecount == 2:
        ret = data[1]<<8 + data[0]
        if ret >= 0x1000:
            ret= -(~ret + 1 &0xff)
    else:
        print("not supported",bytecount)
        exit(0)
    return ret

def to_float(data,bytecount):
    if bytecount != 4 or len(data) !=4:
        print("to float error",bytecount)
        exit(0)
    return struct.unpack('f',data)[0]
    
def to_bcd(data,bytecount):
    if bytecount != 1:
        print("bytecount error",bytecount)
    ret = (data[0]>>4)*10 +  (data[0]&0x0f)    
    return ret
    
class BaseZhou():
    def __init__(self):
        self.itype = 0
   
_temp=-100
class StructA1(BaseZhou):
    def __init__(self,data,curlen):                
        self.event_type = to_uint(data[0:2],2)
        self.timestamp = to_uint(data[2:4],2)
        self.time=[]
        for i in range(0,6):            
            self.time.append(to_bcd(data[4+i:5+i],1))
        self.m_second = to_uint(data[10:12],2)
        self.out_resolution = to_uint(data[12:13],1)
        self.out_x = to_int(data[13:14],1)
        self.out_y = to_int(data[14:15],1)
        self.out_z = to_int(data[15:16],1)
                
        global _temp
                
        if  self.get_mtime() < _temp:            
            pass
            # print("time error curlen:0x%x time:0x%x"%(curlen,self.get_mtime()))
        _temp = self.get_mtime()    
            
    def get_accelerate(self,direction):
        uinit = self.out_resolution *0.78       
        if (direction == 'x'):
            return uinit * self.out_x
        elif direction == 'y':
            return uinit * self.out_x
        elif direction == 'z':
            return uinit * self.out_x
         
    def get_mtime(self):
        return self.time[3]*3600*1000 + self.time[4]*60*1000 + self.time[5]*1000+ self.m_second
    
    def to_string(self,attr=0):
        if attr:
            return "  年  月  日  时  分  秒   毫秒   resolution  x   y   z"
        data = " %3d %3d %3d %3d %3d %3d %5d %8d %8d %3d %3d"%(self.time[0],self.time[1],self.time[2],self.time[3],self.time[4],self.time[5],self.m_second,self.out_resolution,self.out_x,self.out_y,self.out_z)
        return data
        
class StructC1(BaseZhou):
    def __init__(self,data,curlen):
        self.event_type = to_uint(data[0:2],2)        
        self.time=[]
        for i in range(0,6):
            self.time.append( to_bcd(data[2+i:3+i],1))
            
        self.m_second = to_uint(data[8:10],2)        
        self.temp = to_int(data[10:12],2)
        self.pitch = to_float(data[12:16],4)
        self.roll = to_float(data[16:20],4)
        self.yaw = to_float(data[20:24],4)
        self.aacx = to_int(data[24:26],2)
        self.aacy = to_int(data[26:28],2)
        self.aacz = to_int(data[28:30],2)
        self.gyrox = to_int(data[30:32],2)
        self.gyroy = to_int(data[32:34],2)
        self.gyroz = to_int(data[34:36],2)
    
    def get_mtime(self):
        return self.time[3]*3600*1000 + self.time[4]*60*1000 + self.time[5]*1000+ self.m_second
        
    def get_attribute(self,name):
       return getattr(self,name)
       
    def to_string(self,attr=0):
        if attr:
            return "event type  年  月  日  时  分  秒  毫秒   temp   pitch  row    yaw   aacx aacy  aacz  gyrox  gyroy  gyroz"
        data="%10d %3d %3d %3d %3d %3d %3d %5d"\
            "%7d %6.2f %6.2f %6.2f %4d %4d %4d %6d %6d %6d"%(self.event_type,self.time[0],self.time[1],self.time[2],self.time[3],self.time[4],self.time[5],self.m_second,\
            self.temp,self.pitch,self.roll,self.yaw,self.aacx,self.aacy,self.aacz,self.gyrox,self.gyroy,self.gyroz)
        return data
        
class StructC2():
    def __init__(self,data,curlen):
        self.alarm_flag = to_uint(data[0:4],4)
        self.satellite_status = to_uint(data[4:8],4)
        self.latitude = to_uint(data[8:12],4)
        self.longitude = to_uint(data[12:16],4)
        self.hight = to_uint(data[16:18],2)
        self.speed = to_uint(data[18:20],2)
        self.directory = to_uint(data[20:22],2)
        
        self.utc_time=[]
        for i in range(0,6):
            self.utc_time.append(to_bcd(data[22+i:22+i+1],1))
    
    def to_string(self,attr=0):
        if attr:
            return "alarm_flag Satellite_status       latitude  longitude      hight speed     direction    年   月   日   时   分   秒"
        data = "%10d %12d %18d %10d %8d %8d %10d""%8d %4d %4d %4d %4d %4d"%(self.alarm_flag,self.satellite_status,self.latitude,self.longitude,self.hight,self.speed,self.directory,\
                    self.utc_time[0],self.utc_time[1],self.utc_time[2],self.utc_time[3],self.utc_time[4],self.utc_time[5])
        return data
     
    def get_mtime(self):
        return self.utc_time[3]*3600*1000 + self.utc_time[4]*60*1000 + self.utc_time[5]*1000+ self.m_second
        
class LogDevice():
    def __init__(self,itype,ilen,data,curlen):
        self.totaldata = data
        self.itype = itype
        self.ilen = ilen        
        self.curlen = curlen
        self.subdev = None
        
        if self.is_devA1():            
            self.subdev = StructA1(data,self.curlen)
        elif self.is_devC1():
            self.subdev = StructC1(data,self.curlen)
        elif self.is_devC2():
            self.subdev = StructC2(data,self.curlen)
        
    def is_ok(self):
        return self.is_devA1() or self.is_devC1() or self.is_devC2()                
    def is_devA1(self):
        return self.itype == 0xA1
    def is_devC1(self):
        return self.itype == 0xC1
    def is_devC2(self):
        return self.itype == 0xC2
            
def get_struct_numbers(data):
    tt = data>>6 & 0x3
    if tt == 0:
        return 1
    elif tt == 1:
        return 10
    elif tt == 2:
        return 25
    elif tt == 3:
        return 50

def save_single_log_file(devices):
    total=[]
    
    for dev in devices:
        itype = dev.itype
        
        find = False
        descript=None
        for unit in total:
            if unit['itype'] == itype:
                find = True
                descript = unit
                break
        if not find:
            fname = "dev_%x.txt"%itype
            fd = open(fname,"w")
            descript ={'itype':itype,"fd":fd,"fname":fname}             
            total.append(descript)
            fd.write(dev.subdev.to_string(1)+"\r\n")
            
        descript["fd"].write(dev.subdev.to_string()+"\r\n")    
    for unit in total:
        print("save file %s ok"%unit['fname'])
        unit["fd"].close()
        
def read_log(filepath):
    devices=[]
    fd = open(filepath,"rb")
    totaldata=b""
    while True:
        onepack = fd.read(1024)
        if (len(onepack) != 1024):               
            break               
        totaldata += onepack[20:]
        
    fd.close()
    
    # fd = open(r"C:\Users\nwz\Desktop\temp\one\test.hex","wb")
    # fd.write(totaldata)
    # fd.close()
        
    totallen = len(totaldata)
    curlen = 0;
    devicecount=0
    while True:        
        if curlen >= totallen:
            break
        
        structtype = to_uint(totaldata[curlen:curlen+2],2) 
        structnumbers = get_struct_numbers(totaldata[curlen +3])
        structlen = (to_uint(totaldata[curlen+2:curlen+4],2) &0x3fff)//structnumbers
        devicecount+=1      
        # print("%d type:0x%x cur:0x%x"%(devicecount,structtype,curlen),"structnumber:",structnumbers,"structlen:",structlen)
                
        for i in range(0,structnumbers):
            if curlen +4 +i*(structlen+1) >= totallen:
                break
                
            dev = LogDevice(structtype,structlen,totaldata[curlen+4+i*structlen:curlen+4+i*structlen+structlen],curlen+4+i*structlen)
            if dev.is_ok():                
                devices.append(dev)
            else:
                print("get device failed")
                print("type:0x%x cur:0x%x"%(structtype,curlen),"structnumber:",structnumbers,"structlen:",structlen)                
                exit(1)
        
        curlen += 4 + structnumbers * structlen 
    
    save_single_log_file(devices)
    
    return devices

main()
#read_log("apdat-3.hex")