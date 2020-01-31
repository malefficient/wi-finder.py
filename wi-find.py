#!/usr/bin/python
########################################
#
#  wi-find.py: Finds things with Wi-Fi!
#
# Copyright (C) 2019 Johnny Cache <johnycsh@gmail.com>
#


import sys, getopt, re, copy
from scapy.all import *
from color_code import *
from Energy_Scaler import Energy_scale_class
from rtap_ext_util import Listify_Radiotap_Headers
from ext_beacon_util import return_IE_by_tag, TargetCharacteristics
from Rtap_Char import  MeasureyM, MeasureyM_PrintShop
from dbm_unit_conversion import dBm_to_milliwatt, milliwatt_to_dBm
#from colorama import Fore, Back, Style
from render_tabular import Render_Tabular_C

def Usage():
  print("Usage: %s -b <BSSID> -i <input>" % (sys.argv[0]))
  sys.exit(0)


class ConfigC:  #Set-once configuration paramters (values do not change during main loop)
  BSSID=None
  SSID=None
  input_src=None    # 'en0', file.pcap, ...
  sniff_mode=None #  Valid options: 'offline' (pcap file) or 'iface' (self-descr)
  pkts_per_avg=5
  averages_per_header_print=10
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
  prev_measurement_sample_avgs = None
  curr_measurement_samples = MeasureyM()
  Pretty_Printer = Render_Tabular_C()
  E = Energy_scale_class()

  current_scale_center_in_dBm=-72
  current_scale_span_in_dBm=20

  global_sig_best=-100
  global_sig_worst=-20
  ### YYY: *Hmm*. What would be ideal is a simple Map of AntennaId->List(MeasureyM's)
  ### I think we should go this way, with the following caveat:
  ### The 'Top' Level radiotap measurement will be in AntennaMeasuryMap[0].
  ###Extended Radiotap records will be stored at AnteannaId+1. 
  ### //This accounts for the fact that 'Extended' Antenna rtap headers typically start
  ### with AntennaID 0.
  
  def init(self, pkt):
    #print("#### StateC::init") # forward StateC::init packet down to config as a MeasureyM")
    m = MeasureyM()
    m.ProcessExtendedRtap(pkt)
    self.Pretty_Printer.init(m)  
    self.E.init_linear_scale(-72, 20)
  def update_scaling_variables(self):
    print("####StateC::Updating scaling variables")
    print("Type:prev_mesaurement_Sample_avgs: %s" % (self.prev_measurement_sample_avgs))
    if (self.prev_measurement_sample_avgs):
      _hacky_hack= self.prev_measurement_sample_avgs.Measurey_Map[5][0]
      #print("JC: temporarily re-calibrating state.scale to static type 5: %d" % (_hacky_hack))
      print("State.global_sig_best: %d" %  (self.global_sig_best))
      self.global_sig_best = max(self.global_sig_best, _hacky_hack)
      self.global_sig_worst = min(self.global_sig_worst, _hacky_hack)
      self.approx_span_in_mx= 3.0 * math.fabs(self.global_sig_best - self.global_sig_worst)
      #print("Global spread in dBm ~~: 3 x fabs(%d, %d)" % (self.global_sig_best, self.global_sig_worst) )
      #print("Global spread in dBm ~~: %d " % (self.approx_span_in_mx))
      #input(self.prev_measurement_sample_avgs.Measurey_Map) #XYZ: hacky debugging 
      self.E.init_linear_scale(_hacky_hack, max(self.approx_span_in_mx,5))
      
    #sys.exit(0)
    #self.E.init_linear_scale(self.prev_measurement_sample_avgs[:-1][5], 20)
    #self.current_scale_center_in_dBm = self.prev_measurement_sample_avgs[:-1]
    #self.State.current_scale_span_in_dBm = math.fabs( self.State.)
   
    #print(self.prev_measurement_sample_avgs)
    #input("Kk?")
class MainAppC:

  State = StateC()
  Config = ConfigC()
  Target = TargetCharacteristics()
  
  #def __init__(self):
  #  self.State.init()

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
  
    ### Convert scapy-native radiotap layer into a more compact 'measurement' record  ###
    m = MeasureyM()
    m.ProcessExtendedRtap(pkt)
    
    self.State.curr_measurement_samples += (m)
    ll = len(self.State.curr_measurement_samples)

    if  ( ll < self.Config.pkts_per_avg):
      return
    else:
      
      ## PCODE: If (time to re-draw table headers), then time to adjust our scaling vars.
      self.State.update_scaling_variables()
      self.State.prev_measurement_sample_avgs = (self.State.curr_measurement_samples.Average())
      self.State.curr_measurement_samples = MeasureyM() # Clear current list
      #if (self.State.cnt == 1 or self.State.cnt % 50 == 0):
      #  print("%s" % (self.State.Pretty_Printer.ret_header()))
      if ((self.State.prev_measurement_sample_avgs) != None):
        #print("#### Most recent averages ####")
        #print("    (P) %s" % (self.State.prev_measurement_sample_avgs[-2].Measurey_Map))
        #print("    (C) %s" % (self.State.prev_measurement_sample_avgs[-1].Measurey_Map))
        #print("%s" % (self.State.Pretty_Printer.ret_header()))
        if (self.State.Pretty_Printer.cnt % 10 == 0):
          print("%s" % (self.State.Pretty_Printer.ret_header()))
        self.State.Pretty_Printer.print(self.State.prev_measurement_sample_avgs)
        
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
  #input("")
  
def main():
  ## Misc platform setup: On Macos we need to explicitly enable libpcap for BPF to work correctly

  conf.use_pcap = False # XXX This needs to be true on Macos, false on linux 
  #YYY: TODO wrap sniff() calls in conf.use_pcap cases
  retry_pkt1_sniff = False

  A = MainAppC()
  A.Config.Parse_Args()
  bpfilter="type mgt and subtype beacon and wlan host %s " % ( A.Config.BSSID)
  
  ### Before we can get to the main loop, we need to catch atleast 1 beacon (so we know how many measurements are present etc)
  try:
    if A.Config.sniff_mode == "offline":
      pkt1=sniff(prn=ParseTargetBeacon, offline=A.Config.input_src, filter=bpfilter, monitor=1, store=1, count=1)
    else:
      pkt1=sniff(prn=ParseTargetBeacon, iface=A.Config.input_src, filter=bpfilter, monitor=1, store=1, count=1)
  except: 
    retry_pkt1_sniff = True
    conf.use_pcap=True

  if (retry_pkt1_sniff):
    print ("detected exception calling scapy.sniff. Retrying with conf.use_pcap")
    try:
      if A.Config.sniff_mode == "offline":
        pkt1=sniff(prn=ParseTargetBeacon, offline=A.Config.input_src, filter=bpfilter, monitor=1, store=1, count=1)
      else:
        pkt1=sniff(prn=ParseTargetBeacon, iface=A.Config.input_src, filter=bpfilter, monitor=1, store=1, count=1)
    except: 
      print ("Unrecoverable exception in scapy .sniff Exiting")
      sys.exit(1)
 

  if (len(pkt1) < 1):
    print("#### main(): Error. No Beacon received for BSSID: %s" % (A.Config.BSSID))
    exit(0)
  else:
    print(sys.argv[0] + ": Target verified. Enter to continue.")
    pkt1=pkt1[0]
    pkt1.summary()
    A.Config.SSID=pkt1.info.decode() 
    A.State.init(pkt1)
  if A.Config.sniff_mode == "offline":
    sniff(prn=A.callback_main, offline=A.Config.input_src, filter=bpfilter, monitor=1, store=0, count=0)
  else:
     sniff(prn=A.callback_main, iface=A.Config.input_src, filter=bpfilter, monitor=1, store=0, count=0)

if __name__=='__main__':
  main()

