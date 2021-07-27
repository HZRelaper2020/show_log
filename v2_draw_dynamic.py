import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import re
import logging
import v2_common as util
import _thread

plot_x_start = 0
def plot_data(data):
    global plot_x_start
    data = bytes(data)
    curlen = 0
    
    lista1=[]
    listc1= []    
    listc2 = []
    util.read_structs(data,0,lista1,listc1,listc2)
    # plot or print
    x=[]
    y=[]
    z=[]
    st = []
    t = []
    for unit in lista1:
        t.append(unit.time)
        x.append(unit.x)
        y.append(unit.y)
        z.append(unit.z)
        st.append(unit.status)
        
        max_time = 1000*10
        if plot_x_start == 0:
            plot_x_start = unit.time
            plt.legend()
        elif unit.time > plot_x_start + max_time:
            plot_x_start = unit.time
            # plt.xlim((plot_x_start,plot_x_start + max_time))
            plt.clf()
        
    plt.plot(t,x,label="x")
    plt.plot(t,y,label= "y")
    plt.plot(t,z,label = "z")
    plt.plot(t,st,label = "status")
    
    util.save_file(lista1,"a+")
    util.save_file(listc2,"a+")
    
def get_input_char():
    while True:
        c = input()
        if not c:
            print("kill by user")
            os.kill(os.getpid(),-9)

def main():
    _thread.start_new_thread(get_input_char,())
    
    filename = sys.argv[1]
    fd = open(filename)
    fd.seek(0,2)
    curpos = fd.tell()
    fd.close()    
    
    mtime = os.stat(filename).st_mtime
    
    ldata = []
    tot_pkg_count =0
    pkg_number = 0
    while (True):

        bodylen = 0
        serialno = 0
        
        setting_ignore_serail_no = 0
        if os.stat(filename).st_mtime != mtime:
            mtime = os.stat(filename).st_mtime
            fd = open(filename,encoding='gbk')
            fd.seek(curpos,0)
            
            while True:
                serail_number_equal = 0 # judge serial number is equal
                line = fd.readline()       
                if not line:
                    break
                if line.find("[0x0900]") > -1:                   
                    bdtxt = re.search("bodyLen\[(\d+)\]",line)[0]                    
                    bodylen = int(re.search("\d+",bdtxt)[0])
                                             
                    serialtxt = re.search("serialNO\[(\d+)\]",line)[0]
                    new_serialno = int(re.search("\d+",serialtxt)[0])                                        
                    if serialno == 0:
                        serialno = new_serialno
                    else:                        
                        if serialno + 1 != new_serialno:
                            logging.error("serail no not ok before %d after %d",serialno,new_serialno)
                            ldata.clear()
                            if setting_ignore_serail_no and serailno == new_serialno:
                                serail_number_equal = 1
                                break
                            else:
                                exit(0)
                        else:
                            serialno = new_serialno
                    print("main serialno",serialno,"bodylen",bodylen)
                    
                    fd.readline() # ignore \n
                    
                    tempdata = ""
                    while True:
                        onedata = fd.readline()
                        if  not onedata:
                            break
                        if not onedata.startswith("【"):
                            break
                        tempdata += onedata
                        
                    # tempdata = fd.read(1024*100)
                                        
                    tempdata = re.compile("【\d+】").sub(" ",tempdata)
                    tempdata = tempdata.replace("—"," ")
                    tempdata = tempdata.split()
                    
                    tempdata = tempdata[12:] # remove jtt808 header
                    
                    for unit in tempdata:
                        if not serail_number_equal:
                            ldata.append(int(unit,16))
                        
            curpos = fd.tell()            
            fd.close()
            
        if len(ldata) >= 1024:        
            # find “repEDR”  0X72 0X65 0X70 0X45 0X44 0X52
            finddata = [0X72,0X65,0X70,0X45,0X44,0X52]
            isfind = 1
            for i in range(12,17):
                if ldata[i] != finddata[i-12]:
                    isfind = 0
                    break
                    
            if isfind:
                pkg_number = ldata[0] + (ldata[1]<<8) + (ldata[2]<<16) + (ldata[3]<<24)
                print("find serialno",serialno,"bodylen",bodylen,"pkg_number",pkg_number)
                data = ldata[20:1024]
                # util.print_data(data)
                ldata = ldata[1024:]
                plot_data(data)
                tot_pkg_count += 1
                
            else:                
                logging.error("some thing wrong with %d %d",serialno,bodylen)
                find_identify = False
                for i in range(0,len(ldata)-len(finddata)):
                    if ldata[i:i+6] == finddata:                        
                        ldata = [0x0,0x0,0x0,0x0,0xaa,0xaa,0xaa,0xaa,0xaa,0xaa,0xaa,0xaa] + ldata[i:]                        
                        find_identify = True
                        pkg_number = 0
                        break
                if not find_identify:
                    ldata.clear()
                    
                # break
            
        plt.pause(0.01)
        
main()
