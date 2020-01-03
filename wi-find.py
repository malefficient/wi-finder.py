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
  SSID=None
  input_src=None    # 'en0', file.pcap, ...
  sniff_mode=None #  Valid options: 'offline' (pcap file) or 'iface' (self-descr) 
  Ref_dBm=-40   #Pick an arbitrary (but consistent) 'standard candle'

class StateC:  #All dynamic state associated with instance
  cnt=0
  curr_avg_sig = 0
  prev_avg_sig = 0
  curr_sigdBms = []
  
  curr_avg_noise = 0
  prev_avg_noise = 0
  curr_noisedBms = []
  
  ### Set of _Minimum_ fields present 
  
  ### Clever: create a dictionary that maps the fields bit-positin in RadioTap Present -> list of stored values
  present_bits_analyzed = [6,7] #//Sig_dBm,Noise_dBm
  readings = {}

  curr_c = 0     #TODO Replace with call to len

  num_times_before_reprinting_network_header=6
    

  def init(self):
    print("#### StateC::ctor::Start")
    input("Continue:")

###########


def RadiotapFieldDescrTable_C():
  Data=[]

  def field_descr(self, present_bit):
    Data[6]= ["dBm_AntSignal", "Signal strength", None, 6]
    Data[7]= ["dBm_AntNoise", "Noise", None, 7]
    try: 
      d=Data[present_bit]
    except:
      d=None

    return d

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
    print("    Rate: %d Channel:%d dBm_AntSignal: %d  Lock_Quality: %d" % (rtap.Rate, rtap.Channel,  rtap.dBm_AntSignal, rtap.Lock_Quality))


    if (  not ('dBm_AntSignal'in rtap.present)):
      print("Skiiped. No signal present")
      return

    # if (  not ('dBm_AntNoise'in rtap.present)):
    #   print("Skiiped. No _Noise_ reading present")
    #   return
    # #print("        Minimal threshold hit")

    hdr_list = Listify_Radiotap_Headers(pkt)

    if len(hdr_list) > 1:
      print("    Multiple signal readings detected (%d). Enable tricky case." % (len(hdr_list)))

    for h in hdr_list:
      print("   dBm_AntSignal: %d " % (h.dBm_AntSignal))

    
    input("Next:")


    pkts_per_avg=5
    if (len(self.State.curr_sigdBms) <pkts_per_avg):
        self.State.curr_sigdBms.append(rtap.dBm_AntSignal)
        self.State.curr_noisedBms.append(rtap.dBm_AntNoise)
        return

    #Else: Time to compute average
    self.State.num_times_before_reprinting_network_header-=1
    
    self.State.prev_avg_sig =self.State.curr_avg_sig
    self.State.curr_avg_sig = sum(self.State.curr_sigdBms) / pkts_per_avg

    self.State.prev_avg_noise =self.State.curr_avg_noise
    self.State.curr_avg_noise = sum(self.State.curr_noisedBms) / pkts_per_avg


    if (self.State.curr_avg_sig == self.State.prev_avg_sig):
      curr_color = Fore.WHITE
    elif (self.State.curr_avg_sig > self.State.prev_avg_sig):
      curr_color = Fore.GREEN
    elif (self.State.curr_avg_sig < self.State.prev_avg_sig):
      curr_color = Fore.RED

    delta = abs( self.State.prev_avg_sig) - abs(self.State.curr_avg_sig)
    snr =  self.State.curr_avg_sig  - self.State.curr_avg_noise #So says wireshark ?

    #print("%3s  Signal(dBm):(%2d)  Noise(dBm)(%2d)" % (Fore.WHITE,  self.State.curr_avg_sig, self.State.curr_avg_noise))

#    if (delta == 0):
 #     print("=")
 #     return
    # else:
    #   print("%sSNR:%d Signal(dBm):(%2d)  Noise(dBm)(%2d)" % (Fore.WHITE, snr,self.State.curr_avg_sig, self.State.curr_avg_noise))

    ## Signal

    print("(##### Network: (%s%3d%s), %s Noise:%3d, S/N:%3d ########" % (  curr_color, self.State.curr_avg_sig, Fore.WHITE, self.Config.SSID,self.State.curr_avg_noise, snr))

    #print("(%s %+02d %s) to Signal curr(dBm):(%s %2d %s)  Prev(dBm)(%2d)" % (curr_color, delta, Fore.WHITE,  Fore.WHITE, self.State.curr_avg_sig, Fore.WHITE, self.State.prev_avg_sig))

    ## Noise
    #print("(%s %+02d %s) to Noise curr:(%s %2d %s)  Prev:(%2d)" % (curr_color, delta, Fore.WHITE,  Fore.WHITE, self.State.curr_avg_noise, Fore.WHITE, self.State.prev_avg_noise))


    ## TODO: Make this output 'Tabular' (columnar)
    #print("    %s Signal: %s %02d %s " % (Fore.WHITE,  curr_color, self.State.curr_avg, Fore.WHITE))

    self.State.curr_sigdBms = [] # Clear lists
    self.State.curr_noisedBms = []
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


def return_IE_by_tag(pkt, tagno, list_enabled=False):
  print("#### return_IE_by_tag::Start")
  ret_l=[]
  P=pkt.getlayer(Dot11)
  dot11elt = P.getlayer(Dot11Elt)
  while dot11elt:
    #print("dot11eltID: %d, len:%d info:%s" % (dot11elt.ID, dot11elt.len, dot11elt.info[:8]))
    if (dot11elt.ID == tagno and list_enabled == False):
      return dot11elt
    if (dot11elt.ID == tagno and list_enabled == True):
        ret_l.append(dot11elt)    
    dot11elt = dot11elt.payload.getlayer(Dot11Elt)
  
  if (list_enabled and len(ret_l) == 0):
    return None
  if (list_enabled and len(ret_l) == 1):
    return ret_l[0]
  if (list_enabled and len(ret_l) > 1):
    print("QQQQ Highlight! Are you sre you are okay returning a list of (%d) IES of type %d" % ( len(ret_l), tagno))
    input("")
    return ret_l



class rates_descriptor_t:
  # Very wordy class that tracks state re: rates / basic rates 
  min_rate=None
  min_Basic_rate=None
  max_rate=None
  max_Basic_rate=None
  
  def process(self, b):
    if (type(b) != bytes):
      print("Error. rates_decriptor_t expected type:bytes as argument. Passed %s" % (type(b)))
      return
    
    print("#### rates_descriptor_t::process")
    for c in b:
      if (c & 0x80): #Rate is marked as 'Basic' (all client must support)
        m_b = True
        c = c & 0x7f
      else:
        m_b = False
      
      c = c / 2 #Convert value into Mbps (input is 500kbps)
      print(" Basic:%d curr_rate Mbps %d" %(m_b, c))
      
      ##Base case (uninitialized)
      if (self.min_rate == None):
        self.min_rate = c
      if (self.min_Basic_rate == None and m_b):  #'m_b' read as 'matches basic' 
          self.min_Basic_rate=c
      if (self.max_rate == None):
        self.max_rate = c
      if (self.max_Basic_rate == None and m_b):
        self.max_Basic_rate = c

      ## Safe to proceed. All values initialized to int's by this line
      if (m_b and c > self.max_Basic_rate):
        self.max_Basic_rate = c
      if (m_b and c < self.min_Basic_rate):
        self.min_Basic_rate = c
      if ( c > self.max_rate):
        self.max_rate = c
      if ( c < self.min_rate):
        self.min_rate = c
      
      
  def __str__(self):
    ret=""
    ret+= "min_rate:%d min_basic_rate:%d max_rate:%d max_basic_rate:%d" % (self.min_rate, self.min_Basic_rate, self.max_rate, self.max_Basic_rate)
    return ret
  

class TargetCharacteristics:
  # These values excep num_ext_antennas/related are parsed/deduced from Beacon Info Elements (not the radiotap meta header)
  _initialized = False
  tags = {}

  #0
  ssid_hidden = False
  ssid= None
  
  #3
  curr_channel = None
  
  #1,50
  rate_info = rates_descriptor_t()
  #GHz5_enabled = False
  #MHz40_enabled = False
  #tx_beamform_enabled = False

  num_ext_antennas = 0
  ext_antenna_list = []
  _inital_beacon = None




  ####
  ## Targetcharachteristics::process_infoelements()
  ## Parse 802.11 __Beacon__ Fields / InfoElements and pull out what we will consider 'static' information for the duration of execution.
  ## (I.e., this is the detailed 'first-pass' over a beacon, and while we expect values to change over execution, the existence of these fields will not vary. If they do, then hopefully we throw an execption real quick to catch wtf is going on.)

  def summary(self):
    ret = ""

    ret += ("Chan:%02d" %  self.curr_channel)

    if (self.ssid_hidden):
      ret += "SSID: <HIDDEN>"
    else:
      ret += " SSID: %s" % (self.ssid)
    
    ret += "\n     Rates:%s" % (self.rate_info)
    print(ret)
    input("summary end")


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

    ## ID=03: DS ParamSet (Channel)
    tag_3_channel=return_IE_by_tag(pkt, 3)
    if (tag_3_channel == None):
      print("Error: Insufficient beacon information. Channe (3) Missing.")
      return 
    self.tags[3]= tag_3_channel
    self.curr_channel = struct.pack('c', tag_3_channel.info)[0]



    ## ID=(01,50): RATES, Extended Supported Rates (ESR): 
        #      https://dox.ipxe.org/ieee80211_8h_source.html
        #      * The first 8 rates go in an IE of type RATES (1), and any more rates
        #      * go in one of type EXT_RATES (50). Each rate is a byte with the low
        #      * 7 bits equal to the rate in units of 500 kbps, and the high bit set
        #      * if and only if the rate is "basic" (must be supported by all
        #      * connected stations).
    ## ID=01 (Rates)
    tag_1_rates = return_IE_by_tag(pkt, 1, list_enabled=False)
    if (tag_1_rates == None):
      input("QQQQ Curious. No rates (tag=1) found.. ")
    else:
      self.rate_info.process(tag_1_rates.info)
    ## ID=50 (Extended-Rates)
    ## Start at the 'high end' of rates. Notice that some APs include multiple 'Extended Rates (tagn0=50).
    tag_50_extrates = return_IE_by_tag(pkt, 50, list_enabled=True)
    tag50_bytestr=None
    print("QQQQQQQQ: type_tag50_Extrates: %s" % (type(tag_50_extrates)))
   # sys.exit(0)
    if type(tag_50_extrates) == None:
      input("Yikes. No tag50 returned")
    if type(tag_50_extrates) == Dot11Elt:
      tag50_bytestr=tag_50_extrates.info
      print("Simnle case, 1 tag50 returned")
    if type(tag_50_extrates) == list:
      print("Tricky case. tag50 list returned")
      if len(tag_50_extrates) > 1:
        print("QQQQ: Intersting. Multiple(%d) ESR (tag 50) present" % (len(tag_50_extrates)))
      tag50_bytestr = tag_50_extrates[-1:].info
    else:
      tag50_bytestr=tag_50_extrates.info

    if (tag50_bytestr != None):
      self.rate_info.process(tag50_bytestr)
    

   
    
    #print("## Rates: len:(%d), %s" % (tag_1_rates.len, tag_1_rates.info))
    #input("")

   
    ## ID=11: "QBSS Load element" (sta_count, channel utilization, )
    ## ID=23: TPC (TransmitSignal Strength report? ?) #QQQ  
    ## ID=33:  IEEE80211_IE_POWER_CAPAB        33
  
    ## ID=45: HT Capabilites (802.11N D1.10). Complicated.
    ##      \ TxBeamForming, AntennaSelection, HTCapabilites(20Mhz only, 40MHz intolerant), MCS Set, SecondarychjannelOffset
    ##
    ## 221/50:6f:9a: (WiFi alliance)/Type 9: WiFi alliance P2P info? 


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
    sys.exit(0)   
    print("####-TODO: following line, parse (at least hte 'top' level RTap headre)")
    ARrrs= Listify_Radiotap_Headers(pkt)
    top_rtap = ARrrs.pop() 
    self.num_extra_measurements = len(ARrrs)
    print ("Num extra measurement on target:%d" % (self.num_extra_measurements))
    print("##Channel precuror input: ")

    idx=0
    for p in ARrrs:
      print("Ext-%d: AntSignal:(%d)" % (idx,p.dBm_AntSignal))
      idx+=1

    input("")


def GetFirstBeacon(pkt):
  print("####GetFirstBeacon::Start")
  #ret = Listify_Radiotap_Headers(pkt)
  #print("#####GetFirstBeacon::ListifyResults")
 
  print("----- Analyzing beacon into target characteristics")
  T = TargetCharacteristics()
  T.init(pkt)
  
  input("###^^How does that look in terms of meta info?")
  sys.exit(0)
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
  conf.use_pcap = True
 
  A = MainAppC()
  A.Parse_Args()
  C = RadioTap_Profile_C()

  bpfilter="type mgt and subtype beacon and wlan host %s " % ( A.Config.BSSID)

  print(bpfilter)
  #input ("Enter")
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
