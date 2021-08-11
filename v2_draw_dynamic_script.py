import os
import v2_draw_dynamic as main_app
import logging
import sys

def cmd(cmdstr):
    print(cmdstr)
    os.system(cmdstr)
    
def main():    
    '''
    if len(sys.argv) < 2:
        logging.error("please input msg log file")
        return
    '''        
    while True:
        try:
            main_app.draw_dynamic(r"D:\Programs\bin3(EC2)_R\log\010011112222\msg.log")
        except Exception as e:
            print("catch exception",e)
            logging.error(str(e))
    
main()