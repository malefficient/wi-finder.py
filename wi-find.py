#!/usr/bin/python
########################################
#
#  wi-find.py: Finds things with Wi-Fi!
#
# Copyright (C) 2019 Johnny Cache <johnycsh@gmail.com>
#

import sys, getopt, re, copy
from scapy.all import *

from rtap_ext_util import Listify_Radiotap_Headers
from ext_beacon_util import return_IE_by_tag, TargetCharacteristics
from Rtap_Char import  MeasureyM, MeasureyM_PrintShop

from colorama import Fore, Back, Style

def Usage():
  print("Usage: %s -b <BSSID> -i <input>" % (sys.argv[0]))
  sys.exit(0)


class ConfigC:  #Set-once configuration paramters (values do not change during main loop)
  BSSID=None
  SSID=None
  input_src=None    # 'en0', file.pcap, ...
  sniff_mode=None #  Valid options: 'offline' (pcap file) or 'iface' (self-descr)
  pkts_per_avg=5
  
  def Parse_Args(self):
      print("#### Parse_Args: Start")
      opts = getopt.getopt(sys.argv[1:],"b:i:h")

      for opt,optarg in opts[0]:
        if opt == "-b":
          self.BSSID = optarg
        elif opt == "-i":
          self.input_src = optarg
        elif opt == "-h":
          Usage()

      if not self.BSSID:
        print("\nError: BSSID not defined\n")
        Usage()
      if re.match('^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$', self.BSSID):
        self.BSSID = self.BSSID.lower()
      else:
        print("\nError: Wrong format for BSSID\n")
        Usage()

      if not (self.input_src):
        print("\nError: Input not specified")
        Usage()

      # Attempt to open input as both file and iface
      try:
        rdpcap(filename=self.input_src, count=1)
      except:
        pass
      else:
        print("Parse_args: %s opened as file success" % (self.input_src))
        self.sniff_mode="offline"


      if (self.sniff_mode != "offline"):
        try:
          print("asdf")
          sniff(iface=self.input_src, monitor=1, store=0, count=1)

        except:
          print("Error. %s not valid as input file or interface. Exiting." % (self.input_src))
          sys.exit(0)
        else:
          print("Opened input src as iface successfully.")
          self.sniff_mode="iface"

      if self.sniff_mode == "offline":
        print("    ---- Offline mode enabled")
      elif self.sniff_mode == "iface":
        print("     ------Online mode enabled")
      else:
        Usage()

class StateC:  #All dynamic state associated with instance
  cnt=0
  prev_measurement_sample_avgs = []
  curr_measurement_samples = MeasureyM()
  Pretty_Printer = MeasureyM_PrintShop()
  ### YYY: *Hmm*. What would be ideal is a simple Map of AntennaId->List(MeasureyM's)
  ### I think we should go this way, with the following caveat:
  ### The 'Top' Level radiotap measurement will be in AntennaMeasuryMap[0].
  ###Extended Radiotap records will be stored at AnteannaId+1. 
  ### //This accounts for the fact that 'Extended' Antenna rtap headers typically start
  ### with AntennaID 0.
  

  def init(self):
    print("#### StateC::ctor::Start")
    input("Continue:")

class MainAppC:

  State = StateC()
  Config = ConfigC()
  Target = TargetCharacteristics()
  

  def callback_main(self, pkt):
    self.State.cnt+=1
    #header_list=[]
    argslist=[]
    colorlist=[]
    #print("--%2d): #### sniff::callback_main" % (self.State.cnt))
    
    if (not pkt.haslayer(RadioTap)):
      print("Error. Wrong DLT (not radiotap). Exiting")
      sys.exit(0)

    R=pkt[RadioTap]
    R=RadioTap(raw(R)[:R.len]) ## Trim  Radiotap down to only itself
  
    #reqd_rtap_pres = ['Rate', 'Channel', 'dBm_AntSignal'] #List of minimum set of viable radiotap fields to be useful
    #print("    Present: 0x%08x: " % int(R.present))
    #for k in reqd_rtap_pres:
    #  print("Good: %s Marked present" %(k))

    ### Convert scapy-native radiotap layer into a more compact 'measurement' record  ###
    m = MeasureyM()
    m.ProcessExtendedRtap(pkt)
    #print("    (singleton)%s" % (m.Measurey_Map))
    self.State.curr_measurement_samples += (m)
    #print("    (Aggregate)%s" % (self.State.curr_measurement_samples.Measurey_Map))
    ll = len(self.State.curr_measurement_samples)
    #print("PRocessed counter count: %d" % (ll))
    #input("")

    if  ( ll < self.Config.pkts_per_avg):
      return
    else:
      self.State.prev_measurement_sample_avgs.append (self.State.curr_measurement_samples.Average())
      self.State.curr_measurement_samples = MeasureyM() # Clear current list
      if ( len(self.State.prev_measurement_sample_avgs) >= 2):
        print("#### Most recent averages ####")
        #print("    (P) %s" % (self.State.prev_measurement_sample_avgs[-2].Measurey_Map))
        #print("    (C) %s" % (self.State.prev_measurement_sample_avgs[-1].Measurey_Map))
        self.State.Pretty_Printer.print(self.State.prev_measurement_sample_avgs[-1])
    return
    #sys.exit(0)
    ########
    #print("Returning early!")
    return 

    if (len(self.State.curr_sigdBms) < self.Config.pkts_per_avg):
      self.State.curr_sigdBms.append(R.dBm_AntSignal)
      #self.State.curr_noisedBms.append(R.dBm_AntNoise)
      return
    else:
      self.State.prev_avg_sig = self.State.curr_avg_sig
      self.State.curr_avg_sig = sum(self.State.curr_sigdBms) / self.Config.pkts_per_avg
      self.State.curr_sigdBms = [] # Clear lists


    ###First thing first: Create the ascii output for the top-level radiotap header. 
    ### Often times the topmost header has the most extensive information
    hdr_list = Listify_Radiotap_Headers(pkt)
    if len(hdr_list) > 1:
      print("    Multiple signal readings detected (%d). Enable tricky case." % (len(hdr_list)))

    ## TODO: JC: Dynamically generate format string (or use a contant width with variable prefix?)
    ##### ---- Begin dynamic format string creation ----- #######
    ##Walk the present bitmask, generating a header list and a value list in parallel
    

    if (self.State.curr_avg_sig == self.State.prev_avg_sig):
      curr_color = Fore.WHITE
    elif (self.State.curr_avg_sig > self.State.prev_avg_sig):
      curr_color = Fore.GREEN
    elif (self.State.curr_avg_sig < self.State.prev_avg_sig):
      curr_color = Fore.RED

    delta = abs( self.State.prev_avg_sig) - abs(self.State.curr_avg_sig)
    ## Signal

    print("(##### Network: (%s%3d%s), %s ########" % (  curr_color, self.State.curr_avg_sig, Fore.WHITE, self.Config.SSID ))

    ## TODO: Make this output 'Tabular' (columnar)
    #print("    %s Signal: %s %02d %s " % (Fore.WHITE,  curr_color, self.State.curr_avg, Fore.WHITE))

    #self.RateSelf()


def ParseTargetBeacon(pkt):

  print("----- Analyzing beacon into target characteristics")
  T = TargetCharacteristics()
  T.init(pkt)
  print("-----  Target Summary above ----")
  input("")
  
def main():
  ## Misc platform setup: On Macos we need to explicitly enable libpcap for BPF to work correctly

  #conf.use_pcap = True #XXX This needs to be true on Macos, false on linux 
  #YYY: TODO wrap sniff() calls in conf.use_pcap cases

  A = MainAppC()
  A.Config.Parse_Args()

  bpfilter="type mgt and subtype beacon and wlan host %s " % ( A.Config.BSSID)
  ### Before we can get to the main loop, we need to catch atleast 1 beacon (so we know how many measurements are present etc)
  if A.Config.sniff_mode == "offline":
    pkt1=sniff(prn=ParseTargetBeacon, offline=A.Config.input_src, filter=bpfilter, monitor=1, store=1, count=1)

  else:
    pkt1=sniff(prn=ParseTargetBeacon, iface=A.Config.input_src, filter=bpfilter, monitor=1, store=1, count=1)

  if (len(pkt1) < 1):
    print("#### main(): Error. No Beacon received for BSSID: %s" % (A.Config.BSSID))
    exit(0)
  else:
    print("#### main(): Received initial beacon. Enter to continue")
    pkt1=pkt1[0]
    pkt1.summary()
    A.Config.SSID=pkt1.info.decode() 

  if A.Config.sniff_mode == "offline":
    sniff(prn=A.callback_main, offline=A.Config.input_src, filter=bpfilter, monitor=1, store=0, count=0)
  else:
     sniff(prn=A.callback_main, iface=A.Config.input_src, filter=bpfilter, monitor=1, store=0, count=0)

if __name__=='__main__':
  main()

