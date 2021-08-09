import os
import v2_draw_dynamic as main_app
import logging
import sys

def cmd(cmdstr):
    print(cmdstr)
    os.system(cmdstr)
    
def main():    
    if len(sys.argv) < 2:
        logging.error("please input msg log file")
        return
        
    while True:
        try:
            main_app.draw_dynamic(sys.argv[1])
        except Exception as e:
            print("catch exception",e)
            logging.error(str(e))
    
main()