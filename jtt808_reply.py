import logging
import time
import struct

class Jtt808Reply():
    def __init__(self):
        self.arg1 = None
        self.arg2 = None
        self.arg3 = None
        self.arg4 = None
        self.arg5 = None
        self.arg6 = None
        self.arg7 = None
        self.arg8 = None
        self.arg9 = None
        
    def to_bytes(self,f,start=0):
        f ="!" + f
        args = ""
        
        for i in range(start+1,start+len(f)):
            args += "self.arg%d,"%i
        args = args[:-1]
        
        return eval("struct.pack('%s',%s)"%(f,args))        