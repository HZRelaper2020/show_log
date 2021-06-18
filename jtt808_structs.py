import logging
import struct
import jtt808_print

def from_bcd(data):
    return (data>>4) *10 + (data&0xf)
    
class GpsStruct():

    def __init__(self,payload):
        array = struct.unpack("!4I3H6B",payload)
        self.alarmflag = array[0]
        self.status = array[1]
        self.latitude = array[2]/1000000
        self.longitude = array[3]/1000000 
        self.altitude = array[4]
        self.speed = array[5]
        self.direction = array[6]
        
        self.time = []
        for i in range(0,6):
            self.time.append(from_bcd(array[7+i]))
            
    def to_string(self,attr = 0):
        if attr:
            return "alarm_flag Satellite_status       latitude  longitude      hight speed     direction    年   月   日   时   分   秒"
        s = "%10d %12d %18.2f %10.2f %8d %8d %10d""%8d %4d %4d %4d %4d %4d"%(self.alarmflag,self.status,self.latitude,self.longitude,self.altitude,self.speed,self.directory,\
            self.time[0],self.time[1],self.time[2],self.time[3],self.time[4],self.time[5])
        return s
        
    def get_time(self):
        # hour *3600 + minutes * 60 + second
        return self.time[3]*3600+ self.time[4]*60+ self.time[5]
        
        
class AcclerationA1Struct():
    def __init__(self,payload):        
        array = struct.unpack("HH6BHB3b",payload)
        self.eventtype = array[0]
        self.timestamp = array[1]
        self.time=[]
        for i in range(0,6):
            self.time.append(from_bcd(array[i+2]))
        self.millisecond = array[8]
        self.resolution = array[9]
        self.x = array[10]
        self.y = array[11]
        self.z = array[12]        
        
    def to_string(self,attr=0):
        s = ""
        if attr:
            s =  "  年  月  日  时  分  秒   毫秒   resolution  x     y     z"
        else:
            s= " %3d %3d %3d %3d %3d %3d %5d %8d %8.2f %6.2f %6.2f"%(self.time[0],self.time[1],self.time[2],self.time[3],self.time[4],self.time[5],self.millisecond,self.resolution,\
                self.get_accelerate("x"),self.get_accelerate("y"),self.get_accelerate("z"))
        
        return s
        
    def get_accelerate(self,direction):
        uinit = self.resolution *0.78       
        if direction == 'x':
            return uinit * self.x
        elif direction == 'y':
            return uinit * self.y
        elif direction == 'z':
            return uinit * self.y
    
    def get_time(self):
        return (self.time[3]*3600+ self.time[4]*60+ self.time[5])*1000 + self.millisecond
        
class AcclerationC1Struct():
    def __init__(self,payload):
        # jtt808_print.print_rawdata(payload)
        array = struct.unpack("H6BHH3f6H",payload)
        self.eventtype = array[0]
        self.time = []
        for i in range(0,6):
            self.time.append(array[1+i])
        self.millisecond = array[7]
        self.temp = array[8]
        self.pitch = array[9]
        self.roll = array[10]
        self.yaw = array[11]
        self.aacx = array[12]/2048
        self.aacy = array[13]/2048
        self.aacz = array[14]/2048
        self.gyrox = array[15]/2000
        self.gyroy = array[16]/2000
        self.gyroz = array[17]/2000
        
    def to_string(self,attr=0):
        if attr:
            return "event type  年  月  日  时  分  秒  毫秒   temp   pitch  row    yaw  aacx   aacy  aacz     gyrox     gyroy     gyroz"
        s="%10d %3d %3d %3d %3d %3d %3d %5d"\
            "%7d %6.2f %6.2f %6.2f %5.2f %5.2f %6.2f %9.3f %9.3f %9.3f"%(self.eventtype,self.time[0],self.time[1],self.time[2],self.time[3],self.time[4],self.time[5],self.millisecond,\
            self.temp,self.pitch,self.roll,self.yaw,self.aacx,self.aacy,self.aacz,self.gyrox,self.gyroy,self.gyroz)
        return s
        
    def get_time(self):
        return (self.time[3]*3600+ self.time[4]*60+ self.time[5])*1000 + self.millisecond
    