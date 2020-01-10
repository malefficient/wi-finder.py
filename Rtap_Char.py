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


### For now, we only handle cases where the type/number of measurements are equivalent
def Flatten_and_Average_MeasureM_list(L):
    print("####MeasureyM::Average:")
    print("#### Averaging a List of length:(%d)" %(len(L)))
    for l in L:
      print("    %s" % (l.Measurey_Map))
    
    print ("#### Okay dummy. Just for dummy math purposes, returning  last measure for now")
    ret_m = L[0]
    return ret_m

class MeasureyM:
  rtap_table = RadiotapTable()
  _rt_relevant_bits= [2,3,5,6,7]
  num_updates=0

  Measurey_Map={}
  
  def __init__(self):  
    print("####MeasureyM::init")
    self.Measurey_Map = {}
    self.num_processed_rtaps=0
    for b in self._rt_relevant_bits:
      self.Measurey_Map[b] = [] #Clear old lists

   
  def Flatten(self):
    print("MeasureyM::AverageSelf()")
    print("    Averaging:(%d) unique records" % (self.num_updates))
    print(self.Measurey_Map)
    input("?")
  
  def ProcessRtap(self, R):
    rtap_table_helper = RadiotapTable()
    for b in self._rt_relevant_bits:
      dirty=False
      s=rtap_table_helper.bit_to_name(b)
      ## Does passed in RadioTap layer have a relevent field?
      v=R.getfieldval(s)
      if (v == None):
        continue
      else:
        self.Measurey_Map[b].append(v)
        dirty=True
      print("#### MeasuryM::ProcessRtap: Finished")
      print(self.Measurey_Map)
      
    if (dirty):
      self.num_processed_rtaps+=1


def cb_function(pkt):
  global outfname
  my_helper_table = RadiotapTable()
  ret_list=Listify_Radiotap_Headers(pkt)
  M = MeasureyM()
  for r in ret_list:
    M.ProcessRtap(r)
  print("#### MeasureyMap to String:%s" % (M.Measurey_Map))

def main():
  print("### Radiotap Characterizer:: Main")
  #C = RadioTap_Profile_C()
  sniff(prn=cb_function, offline=sys.argv[1], store=0, count=1)
  sys.exit(0)

if __name__=='__main__':
  main()
