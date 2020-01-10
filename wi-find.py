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
import copy
from colorama import Fore, Back, Style
from scapy.all import *
from rtap_ext_util import Listify_Radiotap_Headers
from ext_beacon_util import rates_descriptor_t, modulation_descriptor_t, return_IE_by_tag

from Rtap_Char import RadioTap_Profile_C, MeasureyM, Flatten_and_Average_MeasureM_list

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
  SSID=None
  input_src=None    # 'en0', file.pcap, ...
  sniff_mode=None #  Valid options: 'offline' (pcap file) or 'iface' (self-descr)
  Ref_dBm=-40   #Pick an arbitrary (but consistent) 'standard candle'

  pkts_per_avg=3


### JC: TODO: 
### In the global State variable StateC, add:
### StateC.AntennaMeasureList = []
##### StateC.AntennaMeasureList[BitB] = list(measurements for Rtap field BitB)


class StateC:  #All dynamic state associated with instance
  cnt=0

  RecordList=[]
  ### TODO: 
  ### YYY: *Hmm*. What would be ideal is a simple Map of AntennaId->List(MeasureyM's)
  ### I think we should go this way, with the following caveat:
  ### The 'Top' Level radiotap measurement will be in AntennaMeasuryMap[0].
  ###Extended Radiotap records will be stored at AnteannaId+1. 
  ### //This accounts for the fact that 'Extended' Antenna rtap headers typically start
  ### with AntennaID 0.
  ### So:
  ### AntennaMeasureList[0] = TopLevelRadiotapHeader
  ### AntennaMeasureList[1] = AntennaId.0
  ### AntennaMeasureList[2] = AntennaID.1, ..
  ### AntennaMeasureList[3] = AntennaId.2
  ### AntennaMeasureList[4] = AntennaId.3
  ### AntennaMeasureList[X] = 1-Dimensional list, offset=AntennaId
  ### AntennaMeasureList[X].MtoL[RtapBitId] = list()
  ### AntennaMeasureList[0] = MeasureyM
  ### AntennaMeasurey_Ma
  ### Measurey_Map
  ### MeasureyM.update(R)
  ### ## M.cnt+=1
  ### ## M.AntSignal_List = []

  
  curr_avg_sig = 0
  prev_avg_sig = 0
  curr_sigdBms = []

  curr_avg_noise = 0
  prev_avg_noise = 0
  curr_noisedBms = []


  pkt_measurements_curr = []
  avg_pkt_measurements_curr = None
  pkt_measurements_prev = None
  avg_pkt_measurements_prev = None
  

  #curr_measurement_avg = MeasureyM()

  ### Set of _Minimum_ fields present

  ### Clever: create a dictionary that maps the fields bit-positin in RadioTap Present -> list of stored values
  present_bits_analyzed = [6,7] #//Sig_dBm,Noise_dBm
  readings = {}

  curr_c = 0     #TODO Replace with call to len

  num_times_before_reprinting_network_header=3


  def init(self):
    print("#### StateC::ctor::Start")
    input("Continue:")





class MainAppC:

  State = StateC()
  Config = ConfigC()
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
        Usage()
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
          print("asdf")
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
    header_list=[]
    argslist=[]
    colorlist=[]

    if (not pkt.haslayer(RadioTap)):
      print("Error. Wrong DLT (not radiotap). Exiting")
      sys.exit(0)

    R=pkt[RadioTap]
    R=RadioTap(raw(R)[:R.len]) ## Trim  Radiotap down to only itself

    ### Convert scapy-native radiotap layer into a more compact 'measurement' record  ###
    m= MeasureyM()
    #m.init()
    
    hdr_list = Listify_Radiotap_Headers(pkt)
    idx=0
    for h in hdr_list:
      m.ProcessRtap(h)
      idx+=1
    #print(m.Measurey_Map)
    #print("####### End rtap header list. Signal should have _Five_ values  #######")
    #input("    ##OK?")

    #self.State.pkt_measurements_curr.append(copy.deepcopy(m)) #XXX Do a deep copy? 
    self.State.pkt_measurements_curr.append(m)

    ll = len(self.State.pkt_measurements_curr)
    if  ( ll < self.Config.pkts_per_avg):
      return
    else:
      ##print(" Hit length = num_pkts_to_avg case.  ll:(%d)" % (ll))
      ##input("About to go through the list before calling average.")
      ##idx=0
      ##for x in  self.State.pkt_measurements_curr:
      ##  print ("_____(%d):   %s" % (idx, x.Measurey_Map))
      ##input(".")
      ##print("-------- Oka. Were those unique?----")
      ##input("?")
      ##input("         ---About to call Flatten_and_Average_lsit: ")
      self.State.pkt_measurements_prev = self.State.pkt_measurements_curr                 #Store unflattened data
      self.State.avg_pkt_measurements_prev = self.State.avg_pkt_measurements_curr         #Store flattened data

      f = Flatten_and_Average_MeasureM_list(self.State.pkt_measurements_curr)  #Compute / Flatten into new average
      #print ("     Flatten and average returned: type:(%s)" % (type(f)))
      self.State.avg_pkt_measurements_curr = f
      #print ("     Flatten and average returned: type:(%s)" % (type(f)))
      #input("Asigned f to State.avg_pkt_measurements_curr")
      print(self.State.avg_pkt_measurements_curr.Measurey_Map)
      self.State.pkt_measurements_curr = []                                     #Clear readings

  
     ######## 
    if (self.State.avg_pkt_measurements_prev == None):
      return

    print("    Prev_Avg: (%s) %s " % (self.State.avg_pkt_measurements_prev, self.State.avg_pkt_measurements_prev.Measurey_Map))
    print("    Curr_Avg: (%s) %s " % (self.State.avg_pkt_measurements_curr, self.State.avg_pkt_measurements_curr.Measurey_Map))
    input("How do those compare?Good?")

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
    
    # 
    
#     print(fmt_str % map(str, argslist))



    #self.State.prev_avg_noise =self.State.curr_avg_noise
    #self.State.curr_avg_noise = sum(self.State.curr_noisedBms) / pkts_per_avg


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










class TargetCharacteristics:
  # These values excep num_ext_antennas/related are parsed/deduced from Beacon Info Elements (not the radiotap meta header)
  _initialized = False
  tags = {}

  #0
  ssid_hidden = False
  ssid= None


  modulation_info = modulation_descriptor_t()

  num_ext_antennas = 0
  ext_antenna_list = []
  _inital_beacon = None

  ####
  ## Targetcharachteristics::process_infoelements()
  ## Parse 802.11 __Beacon__ Fields / InfoElements and pull out what we will consider 'static' information for the duration of execution.
  ## (I.e., this is the detailed 'first-pass' over a beacon, and while we expect values to change over execution, the existence of these fields will not vary. If they do, then hopefully we throw an execption real quick to catch wtf is going on.)

  def summary(self):
    ret = ""

    ret += ("Chan:%02d" %  self.modulation_info.curr_channel)

    if (self.ssid_hidden):
      ret += "SSID: <HIDDEN>"
    else:
      ret += " SSID: %s" % (self.ssid)

    #ret += "\n     Rates:%s" % (self.rate_info)

    ret += "\n    Modulation:%s" % (self.modulation_info)
    print(ret)
    

  def init_main(self, pkt):
    P=pkt.getlayer(Dot11)
    print("#### TargetCharacteristiscs::Interpret_Beacon_IEs::start")

    ## ID=00, SSID.             If SSID.len=0, or SSID is curiously completely missing, assume 'hidden' BSSID.
    tag_0_ssid=return_IE_by_tag(pkt, 0)
    if (tag_0_ssid == None or tag_0_ssid.len == 0 or (tag_0_ssid.len == 1 and tag_0_ssid.info =="")):
        self.hidden_ssid = True
        self.tags[0] = None
    else:
      self.tags[0]=tag_0_ssid
      self.ssid=tag_0_ssid.info.decode()

   ## ID=1,3,50, <HT/vht>
    self.modulation_info.process_pkt(pkt)


    ## ID=11: "QBSS Load element" (sta_count, channel utilization, )
    ## ID=23: TPC (TransmitSignal Strength report? ?) #QQQ
    ## ID=33:  IEEE80211_IE_POWER_CAPAB        33
    ## ID=45: HT Capabilites (802.11N D1.10). Complicated.
    ##      \ TxBeamForming, AntennaSelection, HTCapabilites(20Mhz only, 40MHz intolerant), MCS Set, SecondarychjannelOffset
    ## ID=72: "20/40 MHz BSS CoExistence info"

  def init(self, pkt): # Targetcharacteristics
    self._inital_beacon = pkt
    print("####TargetCharecteristics::init")
    R=pkt.getlayer(RadioTap)
    r=RadioTap( raw(R)[:R.len] )

    #### Iterate through info-elements, storing/caching relevant info
    self.init_main(pkt)
    print("#### 2) OK. Beacon data parsed. Shown bewlow")
    self.summary()
    ######################################

    ARrrs= Listify_Radiotap_Headers(pkt)
    top_rtap = ARrrs.pop()
    self.num_extra_measurements = len(ARrrs)
    print ("Num extra measurement on target:%d" % (self.num_extra_measurements))

    # idx=0
    # for p in ARrrs:
    #   print("Ext-%d: AntSignal:(%d)" % (idx,p.dBm_AntSignal))
    #   idx+=1

    


def GetFirstBeacon(pkt):
  print("####GetFirstBeacon::Start")
  #ret = Listify_Radiotap_Headers(pkt)
  #print("#####GetFirstBeacon::ListifyResults")

  print("----- Analyzing beacon into target characteristics")
  T = TargetCharacteristics()
  T.init(pkt)

  print("###^^How does that look in terms of meta info?")
  #T.init(pkt)
  #ssid=str(pkt.getlayer(Dot11).info) #XXX This conveniently contains SSID (IELement 0. But this isnt a great approach)
  #print("SSID: %s" % (ssid))
  #input("")
  #return ssid
  #print(ret)
  #wrpcap("out2.pcap", ret)
  #sys.exit(0)

def main():
  ## Misc platform setup: On Macos we need to explicitly enable libpcap for BPF to work correctly

  #conf.use_pcap = True #XXX This needs to be true on Macos, false on linux 
  #YYY: TODO wrap sniff() calls in conf.use_pcap cases

  A = MainAppC()
  A.Parse_Args()
  C = RadioTap_Profile_C()

  bpfilter="type mgt and subtype beacon and wlan host %s " % ( A.Config.BSSID)
  ### Before we can get to the main loop, we need to catch atleast 1 beacon (so we know how many measurements are present etc)
  if A.Config.sniff_mode == "offline":
    pkt1=sniff(prn=GetFirstBeacon, offline=A.Config.input_src, filter=bpfilter, monitor=1, store=1, count=1)

  else:
    pkt1=sniff(prn=GetFirstBeacon, iface=A.Config.input_src, filter=bpfilter, monitor=1, store=1, count=1)

  if (len(pkt1) < 1):
    print("#### main(): Error. No Beacon received for BSSID: %s" % (A.Config.BSSID))
    exit(0)
  else:
    #print("#### main(): Received initial beacon. Enter to continue")
    pkt1=pkt1[0]
    pkt1.summary()
    A.Config.SSID=pkt1.info.decode()
#  x = x.decode().encode('ascii',errors='ignore')

 # pkt1.show()
  #input("")
  if A.Config.sniff_mode == "offline":
    sniff(prn=A.Simpl_Process_Radiotap, offline=A.Config.input_src, filter=bpfilter, monitor=1, store=0, count=0)
  else:
     sniff(prn=A.Simpl_Process_Radiotap, iface=A.Config.input_src, filter=bpfilter, monitor=1, store=0, count=0)


#  sniff(prn=A.Simpl_Process_Radiotap, offline="png.pcap", filter=bpfilter, monitor=1, store=0, count=0)



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

# # The snark is strong in this one: https://dox.ipxe.org/ieee80211_8h_source.html
#  /** 802.11 Robust Security Network ("WPA") information element
#   781  *
#   782  * Showing once again a striking clarity of design, the IEEE folks put
#   783  * dynamically-sized data in the middle of this structure. As such,
#   784  * the below structure definition only works for IEs we create
#   785  * ourselves, which always have one pairwise cipher and one AKM;
#   786  * received IEs should be parsed piecemeal.
#   787  *
#   788  * Also inspired was IEEE's choice of 16-bit fields to count the
#   789  * number of 4-byte elements in a structure with a maximum length of
#   790  * 255 bytes.
#   791  *
