##  RadioTap headers have evolved significantly. Some drivers include per-antenna signal / noise information
##  Others provide 'overall' signal/noise, but also include exended Antenna fields.
##
##  When comparing signal strength, the details of how and where this information is encoded can by significant.
##
##

    top_scale_in_dBm = None
    top_scale_in_milliwatts = None
    top_scale_in_microwatts = None
    top_scale_in_nanowatts = None
    top_scale_in_picowatts = None    

    center_scale_in_dBm = None
    center_scale_in_milliwatts = None
    center_scale_in_microwatts = None
    center_scale_in_nanowatts = None
    center_scale_in_picowatts = None

    bottom_scale_in_dBm = None
    bottom_scale_in_milliwatts = None
    bottom_scale_in_microwatts = None
    bottom_scale_in_nanowatts = None
    bottom_scale_in_picowatts = None

if ('Lock_Quality' in R.present):
      header_list.append("Lock:%3d")
      argslist.append(str(R.Lock_Quality))
      colorlist.append(Fore.WHITE)
    if ('dBm_AntSignal' in R.present):
      header_list.append("Signal:%3d")
      argslist.append(str(R.dBm_AntSignal))
      colorlist.append(Fore.GREEN)
    

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




## 1999 - 802.11b  2.4GHz, DSSS, 22MHz, 11MBps 
## 1999 - 802.11a 5GHz, OFDM, 20MHz, 54Mbps
## 2003 - 802.11g 2.4GHzm OFDM, 20MHz, 54Mbps
#### Tag 1 (Rates):        Covers required rate   info from  1999-2003 inclusive 
#### Tag 3 (DS Param set): Covers required chanel info from  1999-2003 inclusive

### if (Tag1.Rates only goes to 11MBps) : 1999 802.11b   :  2.4
### if (Tag1.Rates contains 54MBps)     : 2003 802.11g   : 
### if (Tag3.channel > 11 (i.e. 149,etc): 2003 802.11a   : +5GHz


## 2009 - 802.11n 2.4/5Ghz, MIMO-OFDM, 20,40mhz, 600MBps : +40MHz channels 4x4 mimo 
## 2013 - 802.11AC 5GHz, MIMO-OFDM, 20,40,80,160MHZ,     : +80,160 MHz channsels 8x8 mimo

### if (Tag61 present)                  : 2009 802.11N ()
### if (Tag192 present)                 : 2013 802.11AC 


class xxx_TargetCharacteristics:
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
    print("#### TargetCharacteristiscs::init_main::start")
  
    ## ID=00, SSID.             If SSID.len=0, or SSID is curiously completely missing, assume 'hidden' BSSID. 
    tag_0_ssid=return_IE_by_tag(pkt, 0)
    if (tag_0_ssid == None or tag_0_ssid.len == 0 or (tag_0_ssid.len == 1 and tag_0_ssid.info =="")):
        self.hidden_ssid = True
        self.tags[0] = None
    else:
      self.tags[0]=tag_0_ssid
      self.ssid=tag_0_ssid.info.decode()

   
    self.modulation_info.process_pkt(pkt)
    
    ## ID=161,92, ... many for 802.11AC/N/G/
    #self.modulation_info.process(pkt, self.rate_info, self.curr_channel) # Both the current channel (IE3) and supported rates (IE1,50)  req'd input
    #### Okay, So: Channel, SSID, Rates/ExtendedRates are done.
    #### What should be next?
    #### 802.11 5Ghz/2Ghz detection? What does the channel say for an 11a network?

   
   
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



