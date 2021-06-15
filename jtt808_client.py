import os
import sys
import struct
import socket
import threading
import re
import time
import logging
import jtt808_convert
import jtt808_header
import jtt808_print


class Jtt808ClientThread(threading.Thread):
    def __init__(self,sk,closecallback,timeout,retry,maxheart_time):
        super().__init__()
        self.sk = sk
        self.retry = retry
        self.maxheart_time = maxheart_time
        self.sk.settimeout(timeout)
        self.closecallback = closecallback
        self.socket_is_closed = 0
        # 是否已经注册成功
        self.register_ok = 0                
        self.last_heart_time = 0
        # 存组合包的header和body
        self.multi_packet_list=[]        
        
    def recv_data(self,size):
        data= self.sk.recv(size)
        if not data:
            self.socket_is_closed  = 1           
        return data
        
    def send_data(self,data):
        ret= self.sk.send(data)
        if data and not ret:
            self.socket_is_closed  = 1
        return ret
        
    def recv_until_0x7e(self):
        data = b''
       
        times = 0
        while True:
            times += 1
            if times > 1514:
                break
                
            c = self.recv_data(1)
            if c and c[0] == 0x7e:
                break
            
            if c:
                data += c
        return data
        
    def recv_data_between0x7e_and_0x7e(self):
        self.recv_until_0x7e()
        data = self.recv_until_0x7e()
        if len(data) < 17:
            data = self.recv_until_0x7e()
        
        if len(data) < 17:
            data=b''
            
        return data
        
    def run(self):
        # 一直接收
        loop_times = 0
        recv_timeo = 0
        while True:
            try: 
                loop_times += 1
                                
                data = self.recv_data_between0x7e_and_0x7e()
                if data:
                    recv_timeo = 0
                    self.process_recv_step1(data)
                    
            except Exception as e:
                print(e)
                # traceback.print_exc()
                recv_timeo += 1
            finally:
                removeself = 0
                if not self.register_ok and (recv_timeo > 5 or loop_times > 3):                    
                    removeself = 1
                    
                if self.socket_is_closed: # 已经关闭                    
                    removeself = 1
                
                if removeself:
                    self.closecallback(self)
                    break
    
    # decode 0x7d01 0x7d02 and check checksum,remove checksum
    def process_recv_step1(self,data):
        if len(data) < 14:
            logging.error("len(data) is too small",len(data))
            return -1
        
        prestepok = 0
        # decode 0x7d01 and 0x7d02        
        data = jtt808_convert.jtt808_decode_0x7d01_0x7d02(data)        
        # checksum
        check_checksum = 1
        if check_checksum:
            end = len(data)-1
            checksum = data[end]
            prestepok = 0
            if checksum == jtt808_convert.jt808_get_checksum(data[:-1]):
                prestepok = 1
            else:                
                logging.error("check sum not equal 0x%02x 0x%02x"%(checksum,jtt808_convert.jt808_get_checksum(data[:-1])))                
        else:
            prestepok = 1        
            
        if prestepok:
            prestepok = 0
            data = data[:-1] # remove checkcode
            self.process_recv_step2(data)
            
    def process_recv_step2(self,data):        
        header = jtt808_header.Jtt808Header()        
        if header.convert_from_rawdata(data):
           # check msg length is ok?
           if header.msgproperty.msg_length != len(data) - 17 - (4 if header.msgproperty.has_sub_packet else 0):
                logging.error("header.msgproperty.msg_length error 0x%x 0x%x",header.msgproperty.msg_length,len(data) - 17 - (4 if header.msgproperty.has_sub_packet else 0))                
           else:
                if header.is_multi_packet():
                    if header.pkgnumber == 1:
                        self.multi_packet_list.clear()
                    
                    self.multi_packet_list.append((header,data[21:]))
                    
                    if header.pkgcount > 1000:
                        logging.error("header.pkgcount  is too big",header.pkgcount)                    
                    elif header.pkgnumber == header.pkgcount:                        
                        self.process_recv_packet_multi(self.multi_packet_list)                    
                else:
                    self.recv_one_packet(header,data[17:])
    
    # process multi packet
    def process_recv_packet_multi(self,listdata):        
        if listdata:            
            one= listdata[0][0]
            
            msgid = one.msgid
            pkgnum = 0
            pkgcount = one.pkgcount
            flowid = one.flowid
            
            tpyalod= b''
            for header,payload in listdata:
                pkgnum += 1
                if header.pkgcount != pkgcount:
                    logging.error("header.pkgcount != pkgcount")
                    break
                elif pkgnum != header.pkgnumber:
                    logging.error("pkgnum != header.pkgnum")
                    break
                elif msgid != header.msgid:
                    logging.error("msgid != header.msgid")
                    break
                elif flowid != header.flowid:
                    logging.error("flowid != header.flowid")
                    break
                tpyalod += payload
                
            if pkgnum == pkgcount:
                self.process_one_packet(one,tpyalod)
                
    def recv_one_packet(self,header,payload):
        print("receive one packet success")  
         
    
    def send_one_packet(self,header,payload):
        max_packet_size = 0x3ff
        multipkg = 1 if len(payload) > max_packet_size else 0
        
        remain = len(payload)
        pkgcount = (len(payload) + max_packet_size -1)//max_packet_size
        pkgnum = 0
                
        while (remain > 0):
            pkgnum += 1
            sendsize = max_packet_size if remain> max_packet_size else remain
            senddata = payload[len(payload)-remain:len(payload)-remain + sendsize]
            
            header.msgproperty.msg_length = sendsize
            if multipkg:
                header.msgproperty.has_sub_packet = 1                
                header.pkgcount = pkgcount
                header.pkgnumber = pkgnum
            else:
                header.msgproperty.has_sub_packet = 0
                
            data = header.convert_to_rawdata() + senddata
            self.send_one_packet_rawdata(data)
            remain -= sendsize
            
        
    def send_one_packet_rawdata(self,rawdata):
        # checksum
        checksum = jtt808_convert.jt808_get_checksum(rawdata)
        data = rawdata+int(checksum).to_bytes(1,'little')
        # encode 0x7d and 0x7e
        data = jtt808_convert.jt808_encode_0x7d_0x7e(data)
        # send data
        return self.send_data(b'\x7e'+data+b'\x7e')
        
    def process_one_packet222(self,header,payload):
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
            send_msgid = 0
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
                
                send_msgid = 0x8100
                data = struct.pack("!HB",reply_flowid,reply_result)
                if reply_token:
                    data += reply_token.encode()
            elif msgid == 0x002:
                pass
                
            retry = 0
            if send_msgid and data:
                if self.send_reply_packet(send_msgid,header,data):
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
            if self.print_send_data:
                print("send data len",len(totaldata))
                print(totaldata)
                # for (i in range(0,len(totaldata)):
                
            if sk.send(totaldata) == len(totaldata):
                ret  = 0
                break
            else:
                print("send failed");
                
        return ret
        