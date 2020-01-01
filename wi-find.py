#!/usr/bin/python
########################################
#
#  wi-find.py: Finds things with Wi-Fi!
#
# Copyright (C) 2019 Johnny Cache <johnycsh@gmail.com>
#

import sys
import getopt
import re

from colorama import Fore, Back, Style
from scapy.all import *
from rtap_ext_util import Listify_Radiotap_Headers


from Rtap_Char import RadioTap_Profile_C, StateC

def Usage():
  print("Usage: %s -b <BSSID> -i <input>" % (sys.argv[0]))
  sys.exit(0)

class Mathy_Stuff_Holder:

  def Compare_dBm(self, a, b):
  # For a good explanation of all these negative numbers:
  # https://community.cisco.com/t5/small-business-support-documents/why-is-almost-everything-negative-in-wireless/ta-p/3159743
  # 1dBm = 1.258925 mW

    deltaDbm = 1.0 * abs(a - b)
    #print("    deltaDbm(%d,%d) = %d" % (a,b, deltaDbm))
    return deltaDbm

  ### Comparing dBm: How do i always forget this formula?
  ### Quick note: The 'old' version (ap-finder.c) simply told you if curr_avg was (Better, equal, Worse) than prev_avg
  ###             This actually does not require us to work/convert into/from a logarithmic scale.
  ###             -50 is better than -51. The Distance is irrelvant (sortof.)
  def RateSelf(self):
    #print("    RateSelf(%3d,%3d)" % (self.prev_avg, self.curr_avg))
    print("    Delta_dBm (%3d, %3d) = %2d" % ( self.State.curr_avg,  self.State.prev_avg, self.Compare_dBm(self.State.curr_avg, self.State.prev_avg)))
    print("    Delta_dBm (%3d, %3d) = %2d " % ( self.State.curr_avg, self.Config.Ref_dBm, self.Compare_dBm(self.State.curr_avg, self.Config.Ref_dBm)))
  ### TODO: Really should make some sort of BeaconMeasurement() class that handles dBm/ SNR / .. conversion and comparison


class ConfigC:  #Set-once configuration paramters (values do not change during main loop)
  BSSID=None
  input_src=None    # 'en0', file.pcap, ...
  sniff_mode=None #  Valid options: 'offline' (pcap file) or 'iface' (self-descr) 
  Ref_dBm=-40   #Pick an arbitrary (but consistent) 'standard candle'


class MainAppC:

  State = StateC()
  Config = ConfigC()

  def Careful_Process_Radiotap_(self, pkt):
    reqd_rtap_pres = ['Rate', 'Channel', 'dBm_AntSignal'] #List of minimum set of viable radiotap fields to be useful
    self.State.cnt+=1
    print("--%2d): #### AntTuner::ProcessRadiotap" % (self.State.cnt))
    if ( not pkt.haslayer(RadioTap)):
      print("    No RadioTap header(s) detected")
      return

    #rtap=pkt[RadioTap]

    print("    Present: 0x%08x: " % (rtap.present))
    for k in self.reqd_rtap_pres:
      print("Good: %s Marked present" %(k))

    print("    Rate: %d Channel:%d dBm_AntSignal: %d  Lock_Quality: %d" % (rtap.Rate, rtap.Channel,  rtap.dBm_AntSignal, rtap.Lock_Quality))

  def Simpl_Process_Radiotap(self, pkt):
    self.State.cnt+=1

    if (not pkt.haslayer(RadioTap)):
      print("Error. Wrong DLT (not radiotap). Exiting")
      sys.exit(0)

    #print("--%2d): #### AntTuner::SimpleProcessRadiotap" % (self.State.cnt))
    rtap=pkt[RadioTap]
    #print("    Rate: %d Channel:%d dBm_AntSignal: %d  Lock_Quality: %d" % (rtap.Rate, rtap.Channel,  rtap.dBm_AntSignal, rtap.Lock_Quality))


    if (  not ('dBm_AntSignal'in rtap.present)):
      print("Skiiped. No signal present")
      return

    #print("        Minimal threshold hit")

    pkts_per_avg=200
    if (  len(self.State.curr_sigdBms) <pkts_per_avg):
          self.State.curr_sigdBms.append(rtap.dBm_AntSignal)
          return

    #Else: Time to compute average
    self.State.prev_avg=self.State.curr_avg
    self.State.curr_avg = sum(self.State.curr_sigdBms) / pkts_per_avg

    if (self.State.curr_avg == self.State.prev_avg):
      curr_color = Fore.WHITE
    elif (self.State.curr_avg > self.State.prev_avg):
      curr_color = Fore.GREEN
    elif (self.State.curr_avg < self.State.prev_avg):
      curr_color = Fore.RED

    delta = abs( self.State.prev_avg) - abs(self.State.curr_avg)
    if (delta == 0):
      print(".")
    else:
      print("%s(%s %+02d %s)  Signal(dBm):(%s %2d %s) " % (Fore.WHITE, curr_color, self.State.curr_avg, Fore.WHITE, Fore.WHITE, self.State.prev_avg, Fore.WHITE))


    ## TODO: Make this output 'Tabular' (columnar)
    #print("    %s Signal: %s %02d %s " % (Fore.WHITE,  curr_color, self.State.curr_avg, Fore.WHITE))

    self.State.curr_sigdBms = [] # Clear list
    #self.RateSelf()

  def Parse_Args(self):
    print("#### Parse_Args: Start")
    opts = getopt.getopt(sys.argv[1:],"b:i:h")
    
    for opt,optarg in opts[0]:
      if opt == "-b":
        self.Config.BSSID = optarg
      elif opt == "-i":
        self.Config.input_src = optarg
      elif opt == "-h":
        Usage()

    if not self.Config.BSSID:
      print("\nError: BSSID not defined\n")
    if re.match('^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$', self.Config.BSSID):
      self.Config.BSSID = self.Config.BSSID.lower()
    else:
      print("\nError: Wrong format for BSSID\n")
      Usage()

    if not (self.Config.input_src):
      print("\nError: Input not specified")
      Usage()

    # Attempt to open input as both file and iface
    try:
      rdpcap(filename=self.Config.input_src, count=1) 
    except:
      pass
    else:
      print("Parse_args: %s opened as file success" % (self.Config.input_src))
      self.Config.sniff_mode="offline"
    

    if (self.Config.sniff_mode != "offline"):
      try:
        sniff(iface=self.Config.input_src, monitor=1, store=0, count=1)

      except:
        print("Error. %s not valid as input file or interface. Exiting." % (self.Config.input_src))
        sys.exit(0)
      else:
        print("Opened input src as iface successfully.")
        self.Config.sniff_mode="iface"

    if self.Config.sniff_mode == "offline":
      print("    ---- Offline mode enabled")
    elif self.Config.sniff_mode == "iface":
      print("     ------Online mode enabled")
    else:
      Usage()



def GetFirstBeacon(pkt):
  print("####GetFirstBeacon::Start")
  ret = Listify_Radiotap_Headers(pkt)
  print("#####GetFirstBeacon::ListifyResults")
  #print(ret)
  #wrpcap("out2.pcap", ret)
  #sys.exit(0)

def main():
  A = MainAppC()
  A.Parse_Args()
  sys.exit(1)
  C = RadioTap_Profile_C()

  ## Misc platform setup: On Macos we need to explicitly enable libpcap for BPF to work correctly
  conf.use_pcap = True
  sniff(input=self.Config.infile, count=1)

  ## TODO:
  bpfilter="type mgt and subtype beacon wlan host %s " % "88:ad:43:6c:b6:68"
  print(bpfilter)

  ### Before we can get to the main loop, we need to catch atleast 1 beacon (so we know how many measurements are present etc)
  sniff(prn=GetFirstBeacon, offline="png.pcap", filter=bpfilter, monitor=1, store=0, count=1)

  sniff(prn=A.Simpl_Process_Radiotap, offline="png.pcap", filter=bpfilter, monitor=1, store=0, count=0)



if __name__=='__main__':
  main()
#tcpdump  -I -i png.pcap  type mgt subtype beacon
## Here we put a BPF filter so only 802.11 Data/to-DS frames are captured
#s = conf.L2listen(offline = IN_INPUT,filter = "link[0]&0xc == 8 and link[1]&0xf == 1")
## TODO Here we _should_ put a BPF filter so only 802.11 Management frames are captured
## XXX JC: RESUME HERE ^^^. Fix BSSID, investigate pkts /w no signal,
# tcpdump  -I -i png.pcap  -e  type mgt subtype beacon  -c 10 -w ~/t.cap3


# Target: The AWUS1900 / 88XXau.ko driver
#         This device supports a/b/g/n/ac with 4 Antennas.
#		  On top of this, the driver provides a radiotap antenna tag _per_ antenna
#
