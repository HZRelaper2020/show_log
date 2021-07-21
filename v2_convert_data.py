import os
import sys



def convert_a1():
    if len(sys.argv) < 2:
        logging.error("please input file")
        exit(0)
    
    fd = open(sys.argv[1])
    fdsave = open(sys.argv[1]+"convert.txt","w")    
    
    line = fd.readline()
    fdsave.write(line)
    
    
    while True:
        line = fd.readline()
        if not line:
            break
            
        line = line.split()
        newline = ""
        for i in range(0,len(line)):
            param = line[i]
            if i == 1:
                param = str(int(param) - 100)
            
            newline += "  "+param
        fdsave.write(newline+"\t\n")
    fdsave.close()
    fd.close()
    
convert_a1()