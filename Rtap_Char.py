########################################
#
#  Rtap_Char.py --- Radiotap Characteristics
#  Copyright (C) 2019 Johnny Cache <johnycsh@gmail.com>
#
#######

import sys
import numpy
sys.path.append("./scapy")
from scapy.all import *
from rtap_ext_util import RadiotapTable, Listify_Radiotap_Headers


class MeasureyM:
  rtap_table = RadiotapTable()
  _rt_relevant_bits= [2,3,5,6,7]
  num_updates=0

  Measurey_Map={}
  
  def __init__(self):  
    #print("####MeasureyM::init")
    self.Measurey_Map = {}

    for b in self._rt_relevant_bits:
      self.Measurey_Map[b] =  [] #Clear old listsrf
      
  def __len__(self):
    ret = len(list(self.Measurey_Map.values())[0]) ## ("Ret: %d (len of arbitray value in dict)" % (ret))
    return ret
    
  ### Note: ProcessRtap must be passed the original RadioTap layer /with/ the ExtendedPresent bitmask(s) 
  ###       ProcessRtap will call Listify itself; allowing it to preserve the framing information when repeated antenna tags are present
  def ProcessExtendedRtap(self, R):
    rtap_table_helper = RadiotapTable()
    hdr_list = Listify_Radiotap_Headers(R)
    #print("### ProcessRadioTap now down with its own listify")
    #print("#### Listify returned %d headres" % (len(hdr_list)))
    idx=0

    for b in self._rt_relevant_bits:
      idx=0
      s=rtap_table_helper.bit_to_name(b)
      
      curr_l=[]
      idx=0
      for r in hdr_list:
        idx+=1
        
        ## Does passed in RadioTap layer have a relevent field?
        v=r.getfieldval(s)
        if (v == None):
          continue
        else:
          curr_l.append(v)
          dirty=True
      #print("    XXX Aggregated %d packets, field: %d" % (idx, b))
      self.Measurey_Map[b].append(curr_l)

  def Average(self):
    #print("####MeasureyM::Flatten/Average()")
    RetM=MeasureyM() 
    for b in self._rt_relevant_bits:
      n=len(self.Measurey_Map[b])
      #print("    Flattening field:(%d) - (%d) entries" % (b,n))
      res = [sum(i) for i in zip(*self.Measurey_Map[b])]        # Fancy way to sum lists w/o requiring numpy
      RetM.Measurey_Map[b] =  list(numpy.array(res)/n)          # temporarily convert results into numpy array for convenient list division
    return(RetM)                                                # NOTE: In the future we could perform more specific mathematic operations on a per field basis                                                                        # But for now, simple average is fine. 
   
  def __add__(self, im):
    #print("#### MeasureyM::__add__")
    RetM = MeasureyM()

    # print("    Self.Measurey_Map: %s" % (self.Measurey_Map))
    # print("    + + + + + ")
    # print("    im.Measurey_Map:   %s"    % (im.Measurey_Map))
    # print("    -----------")

    for b in self._rt_relevant_bits:
      if (im.Measurey_Map[b] == None):
        print("    MeasureyM.Absorb:: Unexpected error accessing field %d in input" % (b))
        input("X")
        sys.exit(0)
      RetM.Measurey_Map[b] = self.Measurey_Map[b] +  im.Measurey_Map[b]
    return RetM


def test_measureym_import():
  M1 = MeasureyM()
  M2 = MeasureyM()
  Pretty_P = MeasureyM_PrintShop()
  ##Read in test input
  pktlist=rdpcap(sys.argv[1], count=2)
  
  #print("####Packet 1 # #####")
  M1.ProcessExtendedRtap(pktlist[0])
  
  #print("####Packet 2 ######")
  M2.ProcessExtendedRtap(pktlist[1])
  
  M3= M1 + M2
  M3 = M3.Average()

  print("##### Packet 3")
  Pretty_P.print(M3)
  return
  print("### M3 (M1 + M2) : (%s)" % (M3.Measurey_Map))
 
  M4 = M3.Average()
  print("#### M4 (M3.Average()) (%s) :" %  (M4.Measurey_Map))
  Pretty_P.print(M4)

class MeasureyM_PrintShop:
  colors=0 #//16,256,...
  def print(self, M):
    Mmm = M.Measurey_Map   #This just gets to take a lot of column inches
 
    print("## %s ##" % (Mmm))
    #print("Noise: %d" %(Mmm[6][0][0]))

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
  test_measureym_import()
  print("main() Exiting.")
  sys.exit(0)
  
if __name__=='__main__':
  main()
