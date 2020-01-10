#!/usr/local/bin/python3
import sys
from scapy.all import *

from ext_beacon_util import return_IE_by_tag
def do_test(pkt):
    print("####do_test:")
    H=HTinfo(channel_primary=43)
    H.show2()

def usage():
  print("Usage: %s input" % (sys.argv[0]))
  exit(0)
def main():
  if (len(sys.argv)) != 2:
    usage()

  pktlist=rdpcap(sys.argv[1])
  for p in pktlist:
     do_test(p)

if __name__ == '__main__':
  main()
