import os
import sys
import struct
import socket
import threading
import re
import time
import datetime
import logging
import jtt808_convert
import jtt808_header
import jtt808_print
import jtt808_reply
import jtt808_save_draw
import traceback


class Jtt808ClientThread(threading.Thread):
    def __init__(self,sk,fn_getclients,closecallback):
        super().__init__()
        self.getclients = fn_getclients
        self.sk = sk
        # default value
        self.retry = 3
        self.maxheart_time = 60
        self.timeout = 1
        self.sk.settimeout(self.timeout)
        
        self.closecallback = closecallback
        self.socket_is_closed = 0
        # 是否已经注册成功
        self.register_ok = 0                
        self.terminalId = None
        self.author_msg = None
        # heart        
        self.last_heart_time = 0
        # 存组合包的header和body
        self.multi_packet_list=[]
        # 保存及绘图
        self.savedraw = jtt808_save_draw.Jtt808SaveDraw()
        
    def set_net_params(self,retry,hearttime,timeout):
        self.retry = retry
        self.maxheart_time = hearttime
        self.timeout = timeout
        self.sk.settimeout(timeout)
        
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
                if str(e) == 'timed out':
                    pass
                else:
                    traceback.print_exc()
                    
                recv_timeo += 1
            finally:
                removeself = 0
                if not self.register_ok:
                    if (recv_timeo > 5 or loop_times > 3):                    
                        removeself = 1
                
                if self.register_ok:
                    if not self.last_heart_time:
                        self.last_heart_time = int(time.time())
                        
                    if int(time.time()) - self.last_heart_time > self.maxheart_time:
                        removeself = 1
                    
                if self.socket_is_closed: # 已经关闭                    
                    removeself = 1
                
                if removeself:
                    try:
                        del self.savedraw
                        self.sk.close()                        
                    except:
                        pass
                        
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
        reply = None
        if header.msgid == 0x100: # register
            header.msgid = 0x8100
            reply = self.process_action_register(header,payload)
        
        if self.register_ok:
            if header.msgid == 0x0002: # heart pkg
                header.msgid = 0x8001
                reply = self.process_action_heartpkg(header)            
            elif header.msgid == 0x0200: # gps
                header.msgid = 0x8001
                reply = self.process_action_position(header,payload)                
            elif header.msgid == 0xE001: # acceleration a1
                header.msgid = 0x8001
                reply = self.process_action_acceleration_a1(header,payload)
            elif header.msgid == 0xE002: # acceleration c1
                header.msgid = 0x8001
                reply = self.process_action_acceleration_c1(header,payload)
                
        if reply:
            retry = 0
            timeout = self.timeout
            while retry <= self.retry:
                retry += 1
                try:
                    self.send_one_packet(header,reply)
                    break
                except:
                    self.sk.settimeout(self.timeout*retry)
            
            self.sk.settimeout(timeout)
        
    def process_action_position(self,header,payload):
        reply = jtt808_reply.Jtt808Reply()
        reply.arg1 = header.flowid
        reply.arg2 = header.msgid
        reply.arg3 = 0
        
        if reply.arg3 == 0:
           self.savedraw.process_position_data(payload)
        return reply.to_bytes("HHB")
    
    def get_common_reply(self,header,value):
        reply = jtt808_reply.Jtt808Reply()
        reply.arg1 = header.flowid
        reply.arg2 = header.msgid
        reply.arg3 = value
        
        return reply.to_bytes("HHB")
        
    def process_action_heartpkg(self,header):
        return self.get_common_reply(header,0)
        
    def process_action_register(self,header,payload):
        reply = jtt808_reply.Jtt808Reply()
        
        terminalId = payload[45:75]
        alreadyregistered = False
        for client in self.getclients():
            if client.register_ok and client.terminalId == terminalId:
                alreadyregistered = True
                break
        
        reply.arg1 = header.msgid
        
        if alreadyregistered:
            reply.arg2= 1
        else:
            reply.arg2= 0
            
            self.register_ok = 1
            self.terminalId = terminalId            
            
            # author = terminalId 
            author = terminalId+datetime.datetime.now().strftime(' %Y-%m-%d %H:%M:%S').encode()
            
            totbts= int(len(author)).to_bytes(1,"little")+author
            
            self.author_msg = totbts
            
            self.savedraw.set_client_id(terminalId)
        
        return reply.to_bytes('HB') + (self.author_msg if self.register_ok else b'')        
    
    def process_action_position(self,header,payload):
        self.savedraw.process_position_data(payload)
        return self.get_common_reply(header,0)
    
    def process_action_acceleration_a1(self,header,payload):
        self.savedraw.process_accelration_a1_data(payload)
        return self.get_common_reply(header,0)
    def process_action_acceleration_c1(self,header,payload):
        self.savedraw.process_accelration_c1_data(payload)
        return self.get_common_reply(header,0)
        
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
        # jtt808_print.print_rawdata(data)
        return self.send_data(b'\x7e'+data+b'\x7e')
        