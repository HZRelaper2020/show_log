import os
import sys
import struct
import socket
import threading
import re
import time
import logging
import jtt808_print

# payload 转化为 有头标志的 byte数据
# def rawdata_to_packet_data(msgid,mobile,flowid,payload):
def jtt808_decode_0x7d01_0x7d02(data):
    newdata=[]
    nextignore = 0
    for i in range(0,len(data)-1):
        if nextignore:
            nextignore = 0
            continue
            
        if data[i] == 0x7d and data[i+1] == 0x01:
            newdata.append(0x7d)
            nextignore = 1
        elif data[i] == 0x7d and data[i+1] == 0x02:
            newdata.append(0x7e)
            nextignore = 1
        else:
            newdata.append(data[i])
            
    newdata.append(data[len(data)-1])
    
    return bytes(newdata)
    
def jt808_get_checksum(data):
    checksum =0
    for i in data:
        checksum ^= i
        
    return checksum

def jt808_encode_0x7d_0x7e(data):
    newdata = []
    for i in range(0,len(data)):
        if data[i] == 0x7d:
            newdata.append(0x7d)
            newdata.append(0x01)
        elif data[i] == 0x7e:
            newdata.append(0x7d)
            newdata.append(0x02)
        else:
            newdata.append(data[i])
            
    return bytes(newdata)