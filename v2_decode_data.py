import os
import struct
import logging
import sys

def to_uint(data,size,isnegative = 0):
    if isnegative:
        if size == 1:
            return struct.unpack("<b",data)[0]
            
    if size == 1:
        return struct.unpack("<B",data)[0]
    elif size == 2:
        return struct.unpack("<H",data)[0]
    elif size  == 4:
        return struct.unpack("<I",data)[0]

def print_data(data):
    for i in range(0,len(data)):
        print("%02x "%data[i],end="")
        if i%16 == 15:
            print("\n")
    print("\n\n")
    
class StructA1():
    def __init__(self,data):
        if len(data) != 8:
            logging.error("a1 data len failed %d",len(data))
            exit(0)
                    
        self.time = to_uint(data[0:4],4)
        self.x = to_uint(data[4:5],1,1)
        self.y = to_uint(data[5:6],1,1)
        self.z = to_uint(data[6:7],1,1)
        self.status = to_uint(data[7:8],1)
        # print_data(data)
        # print(self.x,self.y,self.z)
        # exit(0)
        
    def to_string(self,hasattribute=0):
        if hasattribute:
            return "time            x       y     z     status"
        else:
            return "%08d  %d  %d  %d  %d"%(self.time,self.x,self.y,self.z,self.status)
    
    def get_type(self):
        return "A1"
        
class StructC1():
    def __init__(self,data):
        if len(data) != 36:
            logging.error("c1 data len failed %d",len(data))
            exit(0)
    
    def to_string(self,hasattribute=0):
        return " "
    
    def get_type(self):
        return "C1"
        
def save_file(liststructs):
    if liststructs:
        fd = None
        for uint in liststructs:
            if fd == None:
                fname = "new_"+uint.get_type()+".txt"
                print("save to ",fname)
                fd = open(fname,"w")
                fd.write(uint.to_string(1)+"\t\n")
            fd.write(uint.to_string()+"\t\n")
            
        fd.close()
   
def get_struct_count(stype,data):
    if stype == 0xA1:
        return data >> (2+8)
        
    tt = data>>(6+8) & 0x3
    if tt == 0:
        return 1
    elif tt == 1:
        return 10
    elif tt == 2:
        return 25
    elif tt == 3:
        return 50
        
def get_struct_totlen(stype,data):
    if stype == 0xA1:
        return data & 0x03ff 
    else:
        return data & 0x3fff
    
PKGSIZE = 1024

def main():
    if len(sys.argv) < 2:
        logging.error("please input file")
        exit(0)
             
    data = b'';
    fd =open(sys.argv[1],"rb")
    pkgnumber = -1
    curpos = 0
    lista1 = []
    listc1 = []
    while True:
        onepack = fd.read(PKGSIZE)        
        
        if not onepack:
            break
        if len(onepack) != PKGSIZE:
            break
        
         # check pkg number
        newnumber = to_uint(onepack[0:4],4)
        if pkgnumber < 0:
            pkgnumber = newnumber
        else:
            if (pkgnumber != newnumber -1):
                logging.error("pkgnum failed %d %d 0x%x",pkgnum,newnumber,curpos)
                exit(1)
            pkgnumber = newnumber
        # check RepoEDR
        syncheader = onepack[12:18]
        if syncheader[0] != 0x72 or syncheader[1] != 0x65 or syncheader[2] != 0x70 or syncheader[3] != 0x45 \
            or syncheader[4] != 0x44 or syncheader[5] != 0x52:
                logging.error("sync header is no repEDR")
                exit(1)
                
        curpos += 20
        # data process
        data = onepack[20:PKGSIZE]
        curlen = 0
        packlen = len(data)
        while curlen < packlen:
            structtype = to_uint(data[curlen:curlen+2],2)
            if structtype == 0:
                break
            structcount = get_struct_count(structtype,to_uint(data[curlen+2:curlen+4],2))
            totlen = get_struct_totlen(structtype,to_uint(data[curlen+2:curlen+4],2))              
            structlen = totlen//structcount
            
            cur = curlen + 4
            # print("curpos:0x%08x type:0x%04x count:0x%02x structlen:%d  0x%x"%(curpos+curlen, structtype,structcount,structlen,to_uint(data[curlen+2:curlen+4],2)))
            for i in range(0,structcount):
                dev = None
                sdata = data[cur + i*structlen:cur +(i+1)*structlen]
                if structtype == 0xA1:
                    dev = StructA1(sdata)
                    lista1.append(dev)
                elif structtype == 0xC1:
                    dev = StructC1(sdata)
                    listc1.append(dev)
                else:
                    logging.error("not supported type:0x%x",structtype)
                    exit(0)
                    
            curlen += totlen + 4      
            
        curpos += PKGSIZE-20
    fd.close()
    
    save_file(lista1)
    save_file(listc1)
    
main()