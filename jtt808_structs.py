import logging
import struct


def from_bcd(data):
    return (data>>4) *10 + (data&0xf)
    
class GpsStruct():

    def __init__(self,payload):
        array = struct.unpack("!4I3H6B",payload)
        self.alarmflag = array[0]
        self.status = array[1]
        self.longitude = array[2]
        self.latitude = array[3]
        self.altitude = array[4]
        self.speed = array[5]
        self.direction = array[6]
        
        self.time = []
        for i in range(0,6):
            self.time.append(from_bcd(array[7+i]))
            
    def to_string(self,attr = 0):
        s = ""
        if attr:
            pass
        else:
            pass
            
        return s