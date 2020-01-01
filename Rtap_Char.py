########################################
#
#  Rtap_Char.py --- Radiotap Characteristics
#  Copyright (C) 2019 Johnny Cache <johnycsh@gmail.com>
#
#######

##  RadioTap headers have evolved significantly. Some drivers include per-antenna signal / noise information
##  Others provide 'overall' signal/noise, but also include exended Antenna fields.
##
##  When comparing signal strength, the details of how and where this information is encoded can by significant.
##
##
import sys
sys.path.append("./scapy")
from scapy.all import *

###########Organize me#####
class RadiotapMeasurement1Dimensional():
  Initialized = False
  Antenna_Number = 0  #Ranges from 0-4. This value will be inferred from radiotap extended antenna field order when identifier is missing
  dBm_AntSignal = None
  dBm_AntNoise = None
  Lock_Quality = None

  #These fields seem like they should only be in a single dimension
  Rate=1
  Channel=None
  def init(self, R):
    if (type(R) != scapy.layers.dot11.RadioTap):
      print("Error: RadiotapMeasurement1Dimensional passed invalid argument. ")
      return


class RadiotapMeasurementNDimensional():
  Initialized = False
  TotalDimensions = 0
  TopLevelReadings = RadiotapMeasurement1Dimensional()
  IndividualAntennaReadings = []

  def Init(self, R):
    if (type(R) != scapy.layers.dot11.RadioTap):
      print("Error: RadiotapMeasurementNDimensional passed invalid argument. ")
      return

    print("####RadiotapMeasurementNDimensional::Init")
    R.show()

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

class RadioTap_Profile_C:
  rtap_prfile_type=1

  def RadioTap_Profile_C(self, R):
    self.rtap_prfile_type=2
    print("#### RadioTap_Profile_Char::")
    R.summary()

if __name__=='__main__':
  print("### Radiotap Characterizer:: Main")
  C = RadioTap_Profile_C()
  #sniff(prn=A.Simpl_Process_Radiotap, offline=A.Config.infile, store=0, count=60)
  pktlist=rdpcap("tst.pcap")
  p=pktlist[0]
  p.show2()
#  C.init(r)

