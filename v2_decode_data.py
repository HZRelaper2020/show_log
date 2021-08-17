import os
import struct
import logging
import sys
import v2_common as util

PKGSIZE = util.PKGSIZE
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
    listc2 = []
    lista2 = []
    lista3 = []
    lista4 = []
    while True:
        onepack = fd.read(PKGSIZE)        
        
        if not onepack:
            break
        if len(onepack) != PKGSIZE:
            break
        
         # check pkg number
        newnumber = util.to_uint(onepack[0:4],4)
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
             
        util.read_structs(data,curpos,lista1,listc1,listc2,lista2=lista2,lista3=lista3,lista4=lista4)
        
        curpos += PKGSIZE-20
    fd.close()
    
    util.save_file(lista1)
    util.save_file(listc1)
    util.save_file(listc2)    
    util.save_file(lista2)
    util.save_file(lista3)
    util.save_file(lista4)
    
main()