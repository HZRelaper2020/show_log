import os
import sys
import struct
import socket
import threading
import re
import time
import logging
import jtt808_client

#
# 单包测试
# 组合包测试
# 包含 0x7e及0x7d测试
#


JTT808_NEED_CHECK_FLOWID            =   1
JTT808_NEED_CHECK_CHECKSUM          =   1

        
class Jtt808ServerThread(threading.Thread):
    def __init__(self,port):
        super().__init__()    
        sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sk.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        ip = ("0.0.0.0",port)
        sk.bind(ip)        
        
        logging.info("listen on %s",ip)
        sk.listen(100)
        self.sk = sk
    
        self.clients = []
        
    def run(self):
        while True:
            client,addr = self.sk.accept()            
            logging.info("recv from %s",addr)            
            thread = jtt808_client.Jtt808ClientThread(client,self.get_clients,self.client_close_callback)
            thread.start()
            
            self.clients.append(thread)                        
    
    def get_clients(self):
        return self.clients
        
    def client_close_callback(self,client):
        self.clients.remove(client)
    
def main():
    logging.basicConfig(level = logging.INFO)    
    
    server = Jtt808ServerThread(8837)
    server.start()
        
    while True:
        s= input()
        if not s or s=="e":
            os.kill(os.getpid(),-9)
            exit(0)
        elif s == "1":
            print(server.get_clients())

main()