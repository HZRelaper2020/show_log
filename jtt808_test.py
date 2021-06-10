import os
import sys
import struct
import socket
import threading
import re
import time
import logging

PORT = 5555

def test_send_subpacket(sk):
    # time.sleep(0.1)
    data = [0x7e,0x7e,0x0,0x1,0x0,0x12,0x5,0x76,0x7,0x8,0x8,0xa,0xb,0xc,0xd,0xe,0x7d,0x1,0x7d,0x02,0x01,0x02,0x69,0x7e,0x7e]
    sk.send(bytes(data))

def test_send_multipacket(sk):
    data = []
    sk.send(bytes(data))
    
def main():
    sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sk.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    ip = ("0.0.0.0",PORT)
    sk.bind(ip)
    print("listen on ",ip)
    sk.listen(100)
    
    client,addr = sk.accept()
    # print(client,addr)
    test_send_subpacket(client)
    
    client.close()
    sk.close()
    
main()