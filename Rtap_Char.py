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
from rtap_ext_util import RadiotapTable, Listify_Radiotap_Headers





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


class RadioTap_Profile_C:
  rtap_prfile_type=1

  def RadioTap_Profile_C(self, R):
    self.rtap_prfile_type=2
    print("#### RadioTap_Profile_Char::")
    R.summary()

class MeasureyM:
  rtap_table = RadiotapTable()
  _rt_relevant_bits= [2,3,5,6,7]

  Measurey_Map={}


  def init(self):  
    print("####MeasureyM::init")
    for i in self._rt_relevant_bits:
      self.Measurey_Map[i] = [] #Clear old lists
  def Update(self, R):
    #print("MeasureyM::Update()")
    #Request all revelent rtap fields
    for b in self._rt_relevant_bits:
      s=self.rtap_table.bit_to_name(b)
      #print("####MeasuryMap: Looking for rtap bit num: %d (%s)" % (b,s))
      ##Seems kind of silly, but I do not think native RadioTap layers in scapy can be easily retrieved by the relevent bit number in present.
      ## Does passed in RadioTap layer have a relevent field?
      v=R.getfieldval(s)
      if (v == None):
        continue

      self.Measurey_Map[b].append(v)
   


def cb_function(pkt):
  global outfname
  my_helper_table = RadiotapTable()
  ret_list=Listify_Radiotap_Headers(pkt)
  M = MeasureyM()
  M.init()
  for r in ret_list:
    M.Update(r)
  print("#### MeasureyMap to String:%s" % (M.Measurey_Map))
if __name__=='__main__':
  print("### Radiotap Characterizer:: Main")
  C = RadioTap_Profile_C()
  sniff(prn=cb_function, offline=sys.argv[1], store=0, count=1)
  sys.exit(0)
#  C.init(r)

