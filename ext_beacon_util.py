#!/usr/bin/python
########################################
#
#  ext-beacon-util.py: Extensive beacon parsing utility
#
# Copyright (C) 2019 Johnny Cache <johnycsh@gmail.com>
#

from scapy.all import *
from rtap_ext_util import Listify_Radiotap_Headers



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
  

  if (len(ret_l) > 1):
    print("QQQQ Highlight! Are you sre you are okay returning a list of (%d) IES of type %d" % ( len(ret_l), tagno))
    input("")

  return ret_l


class rates_descriptor_t:
  # Very wordy class that tracks state re: rates / basic rates 
  minnie_rate=None
  min_Basic_rate=None
  max_rate=None
  max_Basic_rate=None
  
  rates_list=[]
  def process(self, pkt):
    ## ID=(01,50): RATES, Extended Supported Rates (ESR): 
        #      https://dox.ipxe.org/ieee80211_8h_source.html
        #      * The first 8 rates go in an IE of type RATES (1), and any more rates
        #      * go in one of type EXT_RATES (50). Each rate is a byte with the low
        #      * 7 bits equal to the rate in units of 500 kbps, and the high bit set
        #      * if and only if the rate is "basic" (must be supported by all
        #      * connected stations).
    ## ID=01,50 (Rates/Extended_Rates)
    tag_1_rates = return_IE_by_tag(pkt, 1, list_enabled=False)
    if (tag_1_rates == None):
      input("QQQQ Curious. No rates (tag=1) found.. ")
    else:
      self.process_rate(tag_1_rates.info)
    ## ID=50 (Extended-Rates)
    ## Start at the 'high end' of rates. Notice that some APs include multiple 'Extended Rates (tagn0=50).
    tag_50_extrates = return_IE_by_tag(pkt, 50, list_enabled=True)
    for t in tag_50_extrates:
        self.process_rate(t.info)

    print("    rates_descriptor_t::process() done.  Curr min/max: %s %s" % (self.minnie_rate, self.min_Basic_rate)) 

  def __str__(self):
    print("    rates_descriptor_t::toString::Start")
    print("     Sanity check min/max: %s %s" % (self.minnie_rate, self.min_Basic_rate)) 
    ret=""
    ret+= "min_rate:%s min_basic_rate:%s max_rate:%s max_basic_rate:%s" % (self.minnie_rate, self.min_Basic_rate, self.max_rate, self.max_Basic_rate)
    ret+="Rates_List: %s" % (self.rates_list)
    return ret
 
  def process_rate(self, b):
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
      self.rates_list.append(c)
      
      ##Base case (
      # uninitialized)
      if (self.minnie_rate == None):
        self.minnie_rate = c
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
      if ( c < self.minnie_rate):
        self.minnie_rate = c
      
      
  
  ###Notes of complex IE rates / modulations:


class modulation_descriptor_t:

  rates_info = rates_descriptor_t()
  curr_channel = None

  Dot11A_support = False
  Dot11B_support = False
  Dot11G_support = False
  Dot11N_support = False
  Dot11AC_support= False
  MftrYear = 1999

  Band5GHz_suport = False
  Band2Ghz_support = False

  CWidth_40_support = False
  CWidth_80_support = False

  def process_pkt(self, pkt):
    print("Modulation descriptior type::main loop:: start")
  
    ## ID=(01, 50): Rates/ExtRates
    self.rates_info.process(pkt)

    ## ID=03: DS ParamSet (Channel)
    tag_3_channel=return_IE_by_tag(pkt, 3)
    if (tag_3_channel == None):
      print("Error: Insufficient beacon information. Channel (3) Missing.")
      return 
    self.curr_channel = struct.pack('c', tag_3_channel.info)[0]


    tag_61_HT = return_IE_by_tag(pkt, 61)
    if (tag_61_HT != None):
      print("This is where we process Dot11N Rates")
      #tag_61_HT.show2()
      #input("")
      
    ##
  def do_dot11_letter_soup(self, pkt):
    print("#### Modulation_descriptor_t :: Start")
    #print("### Rates info argument %s" % (rates_info))
    #print("### Curr_channel argument: %d" % (curr_channel))
    #sys.exit(0)
    
    
    if (rates_info.max_rate > 1):
      self.Dot11B_support=True
    if (rates_info.max_rate > 11):
      self.Dot11G_support = True 
      if (curr_channel > 11):
        self.Dot11A_support = True

    if ( return_IE_by_tag(pkt, 61) != None):
      self.Dot11N_support = True
      self.Dot11A_support = True
    if ( return_IE_by_tag(pkt, 191) != None):
      self.Dot11AC_support = True

      # if (Dot11AnythingSupport)
      # self.2GHZ_enabled=true
      # if (Dot11AlmostAnythingSupport)
      # self.5GHz_enabled-true

  def __str__(self):
    print("####modulation descriptor_t :: toString start")
    ret=""
    if (self.Dot11A_support):
      ret+="/A"
      self.MftrYear=1999
    if (self.Dot11B_support):
      ret+="/B"
      self.MftrYear=1999
    if (self.Dot11G_support):
      ret+="/G"
      self.MftrYear=2003
    if (self.Dot11N_support):
      ret+="/N"
      self.MftrYear=2009
    if (self.Dot11AC_support):
      ret+="/AC"
      self.MftrYear=2013
    ret += " MftrYear: %d" % (self.MftrYear)

    ret += " %s" % (self.rates_info)
    return ret


class TargetCharacteristics:
  # These values excep num_ext_antennas/related are parsed/deduced from Beacon Info Elements (not the radiotap meta header)
  _initialized = False
  tags = {}

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

    #ret += "    Rates:%s" % (self.rate_info)
    ret += "    Modulation:%s" % (self.modulation_info)
    print(ret)
    return ret
    

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

############# ext_beacon_util::main ####
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




if __name__=='__main__':
  main()
