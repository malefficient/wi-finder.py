#!/usr/local/bin/python3
import sys
from scapy.all import *


def do_test(pkt):
    print("Performing test on:")
    pkt.show2()
    input("enter'")

def usage():
  print("Usage: %s input" % (sys.argv[0]))

def main():
  if (len(sys.argv)) != 2:
    usage()

  pktlist=rdpcap(sys.argv[1])
  for p in pktlist:
     do_test(p)

if __name__ == '__main__':
  main()
