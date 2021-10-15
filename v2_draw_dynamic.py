import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import re
import logging
import v2_common as util
import _thread

plot_x_start = 0
plot_tmp_count =  0
plot_speed_t = 0;
plot_c2_t = []
plot_c2_x = []

def collision_plot(ldata):
    if ldata:
        t = []
        x = []
        start = 0
        for unit in ldata:
            for i,dx in enumerate(unit.delta_vx):            
                if dx == 0xfe:
                    continue
                t.append(start)
                start += 1
                x.append(dx-127)
                    
        plt.plot(t,x,label="x")
        
def plot_data(data):
    global plot_x_start
    global plot_tmp_count
    
    global plot_speed_t
    global plot_c2_t
    global plot_c2_x
    
    data = bytes(data)
    curlen = 0
    
    lista1=[]
    listc1= []    
    listc2 = []
    lista2 = []
    lista3 = []
    lista4 = []
    util.read_structs(data,0,lista1,listc1,listc2,lista2 = lista2,lista3=lista3,lista4=lista4)
    # plot or print
    x=[]
    y=[]
    z=[]
    st = []
    t = []

    for unit in lista1:
        t.append(unit.time)
        x.append(unit.x+10)
        y.append(unit.y)
        z.append(unit.z-10)        
    # vx,vy -127    
    max_number = 1000*5
    plot_tmp_count += len(lista1)
    
    plt.figure(1)
    # plt.subplot(1,2,1)
    plt.title("3 zhou x,y")
    if plot_tmp_count > max_number:
        plot_tmp_count = 0
        plt.clf()
        
    plt.ylim(-30,30)
    plt.plot(t,x,label="x")
    plt.plot(t,y,label= "y")    
    
    # draw pic
    if lista2 or lista3 or lista4:
        plt.figure(2)
        plt.xlim(0,30)
        plt.ylim(-128,128)
        
    if lista2:
        # plt.subplot(1,3,1).set_title("a2")
        plt.title("a2")
        collision_plot(lista2)
    elif lista3:
        plt.title("a3")
        # plt.subplot(1,3,2).set_title("a3")
        collision_plot(lista3)
    elif lista4:
        plt.title("a4")
        # plt.subplot(1,3,3).set_title("a4")
        collision_plot(lista4)
    
    t.clear()
    x.clear()
    if listc2:
        if len(plot_c2_t) > 500:
            plot_c2_t.clear()
            plot_c2_x.clear()
            
        plt.figure(3)
        for i,unit in enumerate(listc2):
            plot_speed_t += 1
            # t.append(unit.time)
            plot_c2_t.append(plot_speed_t)
            plot_c2_x.append(unit.speed)        
        plt.title("gps speed km/h")
        plt.cla()
        plt.plot(plot_c2_t,plot_c2_x,label="speed")
        
    util.save_file(lista1,"a+")
    util.save_file(listc2,"a+")
    util.save_file(lista2,"a+")
    util.save_file(lista3,"a+")
    util.save_file(lista4,"a+")
    
def get_input_char():
    while True:
        c = input()
        if c==" ":
            print("kill by user")
            # exit(0)
            os.kill(os.getpid(),-9)

def draw_dynamic(filename):
    logging.basicConfig(filename="err.log",filemode="a+")
    _thread.start_new_thread(get_input_char,())
    
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
        
        jump_serilano = 0
        if os.stat(filename).st_mtime != mtime:
            mtime = os.stat(filename).st_mtime
            fd = open(filename,encoding='gbk')
            fd.seek(curpos,0)
            
            while True:
                serail_number_equal = 0 # judge serial number is equal
                line = fd.readline()       
                if not line:
                    break
                if line.find("serialNO") > -1:
                    serialtxt = re.search("serialNO\[(\d+)\]",line)[0]
                    new_serialno = int(re.search("\d+",serialtxt)[0])                                        
                    if serialno == 0:
                        serialno = new_serialno
                    else:
                        if jump_serilano == new_serialno:                            
                            serialno = new_serialno        
                            jump_serilano = 0
                        else:
                            if serialno + 1 != new_serialno:
                                if jump_serilano:
                                    logging.error("serail number wrong before %d after %d",jump_serilano -1,jump_serilano +1)
                                    ldata.clear()
                                    util.exit_app(0)
                                else:
                                    jump_serilano = serialno + 1                            
                                    serialno = new_serialno
                            else:
                                serialno = new_serialno                                   
                    
                    
                    if line.find("[0x0900]") > -1:                   
                        bdtxt = re.search("bodyLen\[(\d+)\]",line)[0]                    
                        bodylen = int(re.search("\d+",bdtxt)[0])                                                
                        
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

def main():    
    draw_dynamic(sys.argv[1])

#main()
