import os
import sys
import struct
import socket
import threading

PORT =8837


g_livecient= []
def append_client(client,addr,thread):
    g_livecient.append((client,addr,thread))
    
class JTT808Header():
    def __init__(self,data):
        array=struct.unpack("!HHBH")
        self.msgid = array[0]
        self.msgproperty = array[1]
        self.version = array[2]
        self.flowid = array[3]        
        
    def get_msg_length(self):
        return (self.msgproperty&0x1f)
        
def PlatformCommonReply(flowid,msgid,reply):
    return struct.pack("")
        
class OneClientThread(threading.Thread):
    def __init__(self,sk,timeout):
        super().__init__()
        self.sk = sk
        self.sk.settimeout(timeout)
        
    def run(self):
        # 一直接收
        lastflow_id = -1
        while True:
            start = sk.recv(1)
            if len(start)==1 and start[0] == 0x7e:
                msgid = sk.recv(2)
                if (len(msgid) != 2):
                    print("msg id recv failed")
                    continue
                msgid = struct.unpack("!H")[0]
                if msgid == 0x0100: # 注册
                    pass
                # header= start[1]+sk.recv(16)
                # if len(header) != 17:
                    # print("drop error data 1")
                    # continue
                # if header[2]&0x20: # 是组合包
                    # header += sk.recv(4)
                    # if (len(header) != 21):
                        # print("drop error data 2")
                        # continue
                    # jttHeader = JTT808Header(header)
                # else:                # 单包
                    # jttHeader = JTT808Header(header)                    
                    # if lastflow_id +1 != jttHeader.flowid:
                        # print("flowid error")
                        # continue
                        
                    # msgbody = sk.recv(jttHeader.get_msg_length())
                    # checksum = sk.recv(1)
                    # tailidentify = sk.recv(1)
                    # if len(msgbody) != jttHeader.get_msg_length() or len(checksum) != 1 or tailidentify != 0x7e:
                        # print("drop error data 3")
                        # print("checksum", checksum, "tailidentify", tailidentify)
                        # continue
                    # 校验位
                    
                
        
class ServerThread(threading.Thread):
    def __init__(self,sk):
        super().__init__()
        self.sk = sk
    
    def run():
        while True:
            client,addr = self.sk.accept()            
            thread = OneClientThread(client)
            thread.start()
            
            append_client(client,addr,thread)
            print("recv from",addr)
        
        
def main():
    sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sk.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    ip = ("0.0.0.0",PORT)
    sk.bind(ip)
    print("listen on ",ip)
    sk.listen(100)
    
    
    while True:
        s= input()
        if not s or s=="e":
            os.kill(os.getpid(),-9)
            exit(0)
        elif s == "1":
            print(g_livecient)


main()