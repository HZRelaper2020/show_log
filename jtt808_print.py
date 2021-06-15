import os
import logging


def print_rawdata(data):
    s = ""
    for i in range(0,len(data)):
        s += "%02x "%data[i]
        if i%16 == 15:
            s += "\n"
    print(s)
    print("")