#!/usr/local/bin/python3
import sys
from time import sleep
from scapy.all import *

class dummy:
    signal=[-46, -47, -65, -44, -54]
    noise=[-66, -67, -52, -61, -70]
    lock=100
    

#from ext_beacon_util import return_IEList_by_tag
def do_test(pkt):
    print("####do_test:")
    H=HTinfo(channel_primary=43)
    H.show2()

def usage():
  print("Usage: %s input" % (sys.argv[0]))
  exit(0)

def do_print():
    while ( 1 ):
        print("aaa")
        sleep(1)
def main():
  do_print()
  if (len(sys.argv)) != 2:
    usage()

  pktlist=rdpcap(sys.argv[1])
  for p in pktlist:
     do_test(p)

if __name__ == '__main__':
  main()
