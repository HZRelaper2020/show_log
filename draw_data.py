import os
import sys
import struct
import logging
import matplotlib.pyplot as plt

def main():
    if len(sys.argv) < 2:
        logging.error("please input file")
        exit(0)
    
    fd = open(sys.argv[1])
    
    params = fd.readline()
    params = params.split()
    
    lvalue = {}
    for param in params:
        lvalue[param] = []
        
    while True:
        line = fd.readline()
        if not line:
            break
        line = line.split()
        
        for i in range(0,len(params)):
            lvalue[params[i]].append(float(line[i]))
            
    fd.close()
    
    curi = 0
    time = None
    for key in lvalue:
        if curi == 0:            
            time = lvalue[key]
            curi =1
        else:         
            plt.plot(time,lvalue[key],label = key)            
    plt.legend()
    plt.show()
    
main()