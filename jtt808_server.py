import os
import sys
import struct
import socket
import threading
import re
import time
import logging

#
# 单包测试
# 组合包测试
# 包含 0x7e及0x7d测试
#


PORT =8837

JTT808_NEED_CHECK_FLOWID            =   1
JTT808_NEED_CHECK_CHECKSUM          =   1

g_livecient= []

def jtt808_append_client(client,addr,thread):
    g_livecient.append((client,addr,thread))

def jtt808_get_client_threads():
    threads = []
    for unit in g_livecient:
        threads.append(unit[2])
    return threads
    
def jtt808_remove_client(thread):
    for client  in g_livecient:
        if client[2] == thread:
            g_livecient.remove(client)
            break
    
class JTT808Header():
    def __init__(self,data):
        array=struct.unpack("!HHBBBBBBBBBBBH",data[0:17])
        self.msgid = array[0]
        
        self.msgProperty = array[1]
        self.versionIdentify = array[1]>>14 & 0x1
        self.hasSubItem = array[1]>>13 & 0x1
        self.encrypt = array[1]>>10 & 0x3
        self.msgBodyLen = array[1] &0x1f
     
        self.mobile = ""
        for i in range(0,6):
            self.mobile += "%02x"%array[3+i]
        self.mobile= self.mobile[0:-1]
        
        self.version = array[2]
        self.flowid = array[13]
        
        self.msgPkgCount = 1
        self.msgPkgNumber = 1
        if self.hasSubItem:
            array = struct.unpack("!HH",data[17:21])
            self.msgPkgCount = array[0]
            self.msgPkgNumber = array[1]
            
        
        
    def get_msg_length(self):
        return self.msgBodyLen

class JTT808Msg():
    def __init__(self):
        pass
        
        
def PlatformCommonReply(flowid,msgid,reply):
    return struct.pack("")
        
class OneClientThread(threading.Thread):
    def __init__(self,sk,timeout,retry,maxheart_time):
        super().__init__()
        self.sk = sk
        self.retry = retry
        self.maxheart_time = maxheart_time
        self.sk.settimeout(timeout)
        # 是否已经注册成功
        self.register_ok = False        
        self.last_recv_ok_frame = None
        self.last_heart_time = 0
        # 存组合包的header和body
        self.subframe_headers = []
        self.subframe_bodys = []
        self.mobile=""
        
    def process_data(self,data):
        if len(data) < 5:
            return -1
        
        prestepok = 0
        # checksum
        if JTT808_NEED_CHECK_CHECKSUM:
            end = len(data)-1
            checksum = data[end]
            if (data[end-1] == 0x7d and data[end] == 0x1):
                end -= 1
                checksum = 0x7d
            elif (data[end-1] == 0x7d and data[end] == 0x1):
                end -= 1
                checksum = 0x7e
            
            sumval = 0
            for i in range(0,end):
                sumval ^= data[i]
            
            if (sumval&0xff) == checksum:                
                prestepok = 1
        else:
            prestepok = 1
                
        if prestepok:
            prestepok = 0
            data = data[:-1] # remove checkcode
            
            # message header process            
            data = self.translate_7e7d_char(data)
            header = JTT808Header(data[0:23])            
            
            if header.msgPkgCount == 1:
                self.process_one_packet(header,data[24:])
                
            elif header.msgPkgCount >1:
                if header.msgPkgNumber ==1:
                    self.subframe_bodys.clear()
                    self.subframe_headers.clear()
                
                self.subframe_headers.append(header)
                self.subframe_bodys.append(datadata[21:])
            
                header = self.subframe_headers[0]   

                # check flowid,total pkg count
                flowid = header.flowid
                msgid = header.msgid
                pkgcount = header.msgPkgCount
                success = 1
                for uint in self.subframe_headers:
                    if uint.flowid != flowid:   
                        success = 0
                        print("flowid not equal")                        
                        break
                    if uint.msgid != msgid:
                        print("msg id failed")
                        success = 0
                        break
                    if uint.msgPkgCount != pkgcount:
                        print("msg pkg count not equal")
                        success = 0
                        break
                
                if success:
                    if header.msgPkgNumber == header.msgPkgCount:                    
                        # check pkgnumber
                        pkgnumber = 0
                        for uint in self.subframe_headers:
                            pkgnumber += 1
                            if uint.msgPkgNumber != pkgnumber:
                                break
                                
                        if pkgnumber == header.msgPkgCount:
                            payload = b''
                            for uint in self.subframe_bodys:
                                payload += uint
                            if self.process_one_packet(header,payload):
                                pass
                            else:
                                prestepok = 1
                    
        return not prestepok;
        
    def process_one_packet(self,header,payload):
        preflowid = -1 # need set
        ret = 0
        if JTT808_NEED_CHECK_FLOWID:
            if preflowid +1 != header.flowid:
                print("preflowid +1 != header.flowid")
                ret = 1
                
        if not ret:
            ret = 2
            data = None
            msgid = header.msgid
            if msgid == 0x0100: # register，返回鉴权码
                mobile = header.mobile;
                
                reply_flowid = header.flowid
                reply_result = 0
                reply_token = None
                for unit in jtt808_get_client_threads():
                    # 是否已经注册
                    if unit != self and unit.mobile == mobile:                        
                        reply_result = 1
                        break
                        
                if not reply_result:
                    self.register_ok = 1
                    self.last_heart_time = time.time()
                    reply_token = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime()) + mobile +" 1.0"
                        
                data = struct.pack("!HB",reply_flowid,reply_result)
                if reply_token:
                    data += reply_token.encode()
            elif msgid == 0x002:
                pass
                
            retry = 0
            if data:
                if self.send_reply_packet(0x8100,header,data):
                    pass
                else: # send ok
                    ret = 0
                                   
        return ret
        
    def send_reply_packet(self,msgid,header,payload): # only for single packet
        ret = 1
        
        payload = self.encode_7e7d_char(payload) # payload ok
        
        msgid = msgid
        msgproperty = 0x4000 + len(payload)
        version = 1
        mobile = self.mobile+"000000000000"
        flowid = header.flowid        
        
        headerdata = struct.pack("!HHBBBBBBBBBBBH",msgid,msgproperty,version,\
            int(mobile[0],16),int(mobile[1],16),int(mobile[2],16),int(mobile[3],16),int(mobile[4],16),int(mobile[5],16),int(mobile[6],16),int(mobile[7],16),int(mobile[8],16),int(mobile[9],16),\
            flowid)
            
        headerdata = self.encode_7e7d_char(headerdata)
        
        checkcode = 0
        for i in headerdata + payload:
            checkcode ^= i
            
        checkcode = checkcode.to_bytes(1,"little")    
        checkcode = self.encode_7e7d_char(checkcode)
         
        retry = 0
        while (retry < self.retry):
            sk = self.sk
            retry += 1
            totaldata = b'\x7e' + headerdata + payload + checkcode+ b'\x7e'
            if sk.send(totaldata) == len(totaldata):
                ret  = 0
                break
            else:
                print("send failed");
                
        return ret
        
    def encode_7e7d_char(self,data):
        newdata = b''
        for i in range(0,len(data)):
            if data[i] == 0x7d:
                newdata += b'\x7d\x01'
            elif data[i] == 0x7e:
                newdata += b'\x7d\x02'
            else:
                newdata += data[i:i+1]
        return newdata
        
    def translate_7e7d_char(self,data):
        newdata = b""        
        for i in range(0,len(data)): # 最后一个不可能为0x7d，否则就是包错误了
            if data[i] == 0x7d and data[i+1] == 0x1:
                i += 1
                newdata += b'\x7d'
            elif data[i] == 0x7d and data[i+1] == 0x2:
                i += 1
                newdata += b'\x7e'
            else:
                newdata += data[i:i+1]
        
        return newdata
            
    def run(self):
        # 一直接收        
        retry = 0
        sockisclosed = 0
        while True:
            try:
                sk = self.sk                
                start = sk.recv(2)
                if not start:
                    sockisclosed = 1
                recvsuccess = 0
                data=b""
                if len(start) ==2:
                    nextstep = 0                    
                    if start[1] == 0x7e:
                        nextstep = 1
                    elif start[0] == 0x7e:
                        data += start[1:2]
                        nextstep =1
                        
                    if nextstep:    
                        while True:                            
                            end = sk.recv(1024) # 不做字节判断，效率太低                                    
                            if not end:
                                sockisclosed =1
                                break
                                
                            data += end
                            if end[len(end)-1]== 0x7e and len(data) > 5:                            
                                recvsuccess = 1                           
                                self.process_data(data[0:-1])
                                break                    
                            if len(data) > 2000: # 这么大的长度还没接收完成，肯定错误了
                                break
                                
                if recvsuccess:
                    retry = 0
                else:
                    raise Exception("recv data error")
                    
            except Exception as e:              
                print(e)
                if sockisclosed or getattr(self.sk, '_closed'): # 已经关闭
                    print("socket already closed")
                    jtt808_remove_client(self)
                    break
                                    
                if self.register_ok:                    
                    if time.time() - self.last_heart_time > self.maxheart_time:
                        print("no heart packet break")
                        jtt808_remove_client(self)
                        break
                else:
                    retry += 1
                    if retry > self.retry:
                        jtt808_remove_client(self)
                        break
                
                    
                
        
class ServerThread(threading.Thread):
    def __init__(self,sk):
        super().__init__()
        self.sk = sk
    
    def run(self):
        while True:
            client,addr = self.sk.accept()            
            thread = OneClientThread(client,5000,3,60)
            thread.start()
            
            jtt808_append_client(client,addr,thread)
            print("recv from",addr)
        
        
def main():    
    sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sk.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    ip = ("0.0.0.0",PORT)
    sk.bind(ip)
    print("listen on ",ip)
    sk.listen(100)
    server = ServerThread(sk)
    server.start()
    
    while True:
        s= input()
        if not s or s=="e":
            os.kill(os.getpid(),-9)
            exit(0)
        elif s == "1":
            print(g_livecient)


main()