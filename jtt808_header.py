import os
import logging
import struct


class Jtt808MsgProperty():
    def __init__(self):
        self.version_identity = 1
        self.has_sub_packet = 0
        self.msg_length = 0
        
        self.value = 0
        
    def convert_from_value(self,value):
        self.version_identity = value &0x4000
        self.has_sub_packet = value & 0x2000
        self.msg_length = value &0x3ff
        
        self.value = value
    
    def get_value(self):
        return (1<<14) + ((1 if self.has_sub_packet else 0)<<13) +self.msg_length
        
class Jtt808Header():
    def __init__(self):
        self.pkgcount = 0
        self.pkgnumber = 0
        
    def convert_from_rawdata(self,data):
        ret = False
        if (len(data) < 17):
            logging.error("data len is too small")            
        else:    
            array = struct.unpack("!HH11BH",data[0:17])
            self.msgid = array[0]
            self.msgproperty = Jtt808MsgProperty()
            self.msgproperty.convert_from_value(array[1])
            self.version = array[2]
            self.mobile=b''
            for i in range (0,10):
                self.mobile += int(array[3+i]).to_bytes(1,'little')
            
            self.flowid = array[13]
            
            if not self.msgproperty.has_sub_packet:
                ret = True
            elif self.msgproperty.has_sub_packet and len(data) >=21:
                array = struct.unpack("!HH",data[17:21])
                self.pkgcount = array[0]
                self.pkgnumber = array[1]
                if self.pkgcount > 1 and self.pkgnumber <= self.pkgcount:
                    ret = True
               
        return ret
        
    def set_params(self,msgid,flowid,mobile=b"\x17\x31\x84\x53\x26\x80\x00\x00\x00\x00",version=1):
        self.msgid = msgid
        self.flowid = flowid
        self.pkgcount = 0
        self.pkgnumber = 0
        self.mobile = mobile
        self.version = version
        
        self.msgproperty = Jtt808MsgProperty()
        
    def is_multi_packet(self):
        return self.msgproperty.has_sub_packet
        
    def convert_to_rawdata(self):
        m= self.mobile        
        ret = struct.pack("!HH11BH",self.msgid,self.msgproperty.get_value(),self.version,\
                m[0],m[1],m[2],m[3],m[4],m[5],m[6],m[7],m[8],m[9],\
                self.flowid)
                
        if self.is_multi_packet():            
            ret += struct.pack("!HH",self.pkgcount,self.pkgnumber)
        
        return ret