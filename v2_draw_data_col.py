import os
import sys
import struct
import logging
import matplotlib.pyplot as plt

def read_attribute(pkg):
    spkg = pkg.split("\n")    
    for line in spkg:
        if line and line.strip():            
            attr = line.split()[0]
            if attr:
                attr = attr.strip()
                if attr[0:1].isalpha(): # first is alpha
                    return attr

def remove_attribute(pkg,attr):
    spkg = pkg.split("\n")
    newpkg = ""
    jump = False
    for line in spkg:
        if line and line.strip():
            sattr = line.split()[0].strip()
            if sattr:
                if sattr.strip() == attr:
                    jump = True
                elif sattr[0:1].isalpha():
                    jump = False
            
        if not jump:
            newpkg += line+"\n"
            
    return newpkg
    
def read_value(pkg,attr):
    spkg = pkg.split("\n")
    val = ""
    start = False
    firstline = True
    cutline = False
    for line in spkg:
        if line and line.strip():
            sattr = line.split()[0].strip()
            if sattr:
                if sattr.strip() == attr:
                    start = True
                elif sattr[0:1].isalpha():
                    break
                    
            if start:
                if firstline:
                    if len(line.split()) > 1:
                        val += " " + line.split()[1]+" "
                    firstline = False
                else:
                    if line.startswith("00000000"):
                        cutline = True
                    if cutline:
                        line = line[8:]
                    val += line + " "
    return val

# self define data process
def self_process_data(attr,value):
    newvalue = []    
    if len(attr) == 5 and attr.startswith("acc_"):        
        for subval in value:            
            newvalue.append(subval - 127)            
    else:
        newvalue = value
        
    return newvalue
    
def main():
    if len(sys.argv) < 2:
        logging.error("please input file")
        exit(0)
    
    fd = open(sys.argv[1])
    save_filename = os.path.dirname(sys.argv[1]) + os.path.splitext(os.path.basename(sys.argv[1]))[0] + "_p1.txt"
    fd_save = open(save_filename,"w")
    print("save to ",save_filename)
    lvalue = []
    
    pkg = ""
    attr = ""
    while True:
        line = fd.readline()
        if not line:
            break        
        if line.find(".....") > -1:
            # set pkgs
            while True:
                attr = read_attribute(pkg)
                if not attr:
                    break
                    
                value = read_value(pkg,attr)
                pkg = remove_attribute(pkg,attr)
                newvalue = []
                if value:
                    for subval in value.split():
                        newvalue.append(int(subval,16))
                        
                newvalue = self_process_data(attr,newvalue)
                
                fd_save.write(attr+"\n")
                for subval in newvalue:
                    fd_save.write(str(subval)+"\n")
                fd_save.write("\n")
            pkg = ""
        else:
            pkg += line
            
    fd.close()
    fd_save.close()
main()