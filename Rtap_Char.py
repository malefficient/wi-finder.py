########################################
#
#  Rtap_Char.py --- Radiotap Characteristics
#  Copyright (C) 2019 Johnny Cache <johnycsh@gmail.com>
#
#######

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
    ##XXX: JC  Resume here !
    ## Todo:  YYY 
    ## * create a MeasureyM.Import(self, right)
    ## for each relevant_bit b
    ##   self.Measurey_Map[b] += right.Measurey_Map

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
      self.Measurey_Map[b] =  [] #Clear old lists
      

  
  
  ### Note: ProcessRtap must be passed the original RadioTap layer /with/ the ExtendedPresent bitmask(s) 
  ###       ProcessRtap will call Listify itself; allowing it to preserve the framing information when repeated antenna tags are present
  def ProcessExtendedRtap(self, R):
    rtap_table_helper = RadiotapTable()
    hdr_list = Listify_Radiotap_Headers(R)
    print("### ProcessRadioTap now down with its own listify")
    print("#### Listify returned %d headres" % (len(hdr_list)))
    idx=0

    for b in self._rt_relevant_bits:
      idx=0
      s=rtap_table_helper.bit_to_name(b)
      
      curr_l=[]
      idx=0
      for r in hdr_list:
        idx+=1
        #print("     ###ProcessExtRtap: Bit:(%d),  pkt_hdr:(%d)" % (b, idx))
        
        ## Does passed in RadioTap layer have a relevent field?
        v=r.getfieldval(s)
        if (v == None):
          continue
        else:
          #print("         ProcessExtRtap(%d) Bit(%d)" % (idx, b))
          #input("")
          curr_l.append(v)
          dirty=True
      #print("    XXX Aggregated %d packets, field: %d" % (idx, b))
      self.Measurey_Map[b].append(curr_l)
      #input(".")
      #print(self.Measurey_Map)
      # if (len(curr_l) > 0):
      #   self.Measurey_Map[b].append(curr_l)  ## /* list of lists */
    #print("#### Returning MEasureyMap: %s" % (self.Measurey_Map))
    #input(".")
  def Flatten(self):
    print("MeasureyM::Flatten()")
    for k in self.Measurey_Map.keys():
      print("    Processing bit:(%d)  num_entries:%d" % (k, len(self.Measurey_Map[k])))
      print("    %s" % (self.Measurey_Map[k]))
      for v in self.Measurey_Map[k]:
        print("       (%s)   MergeWithMAth()" % (v))
      print("    ---------------")

  def Absorb(self, im):
    print("#### MeasureyM::Absorb")

    print("    Self.Measurey_Map: %s" % (self.Measurey_Map))
    print("    + + + + + ")
    print("    im.Measurey_Map:   %s"    % (im.Measurey_Map))
    print("    -----------")

    for b in self._rt_relevant_bits:
      if (im.Measurey_Map[b] == None):
        print("    MeasureyM.Absorb:: Unexpected error accessing field %d in input" % (b))
        input("X")
        sys.exit(0)
      #print("   Bit:(%d) Absorb:: processing: type(%s)" % (b, type(im.Measurey_Map[b])))
      #input("")
      self.Measurey_Map[b] += im.Measurey_Map[b]

    print("    Merge results here.")
    print("Result: %s" % (self.Measurey_Map))    ### TODO: Wrap Mergey_Map[1] in an extra list dimension for grouping?
    input("####  ####")
    #ret_M = {**self.Measurey_Map, **im.Measurey_Map} #//https://stackoverflow.com/questions/38987/how-do-i-merge-two-dictionaries-in-a-single-expression
    # JC Start above ^^

    #RetM = MeasureyM()
   # RetM.Measurey_Map = ret_M
   # print("###Absormed cross product###")
   # print(RetM.Measurey_Map)
   # for b in self._rt_relevant_bits:
   #   self.Measurey_Map[b] = 


def test_measureym_import():
  M1 = MeasureyM()
  M2 = MeasureyM()
  RetM = MeasureyM()
  
  ##Read in test input
  pktlist=rdpcap(sys.argv[1], count=2)
  print("Two packets read in for test")
  RTL1=Listify_Radiotap_Headers(pktlist[0])
  RTL2=Listify_Radiotap_Headers(pktlist[1])

  ## Generate aggregated Measuremeny across Extended rtap fields
  M1.ProcessExtendedRtap(pktlist[0])
  print("####Packet 1 ######")
  print(M1.Measurey_Map)
  #input("Packet1 ?")
 
  M2.ProcessExtendedRtap(pktlist[1])
  print("####Packet 2 ######")
  print(M2.Measurey_Map)
  #input("Packet 2?")
  #sys.exit(0)
  ## First things first: Attempt 'Importing' (Absorbing?) M1 into empty RetM
  #M1.Absorb(M2)
  M3=M1
  M3.Absorb(M2)

  print("### M3 (Merged) : (%s)" % (M3.Measurey_Map))
  print("#### M3 (Flattened) :")
  M3.Flatten()
  print("     %s" % (M3.Measurey_Map))

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
  #C = RadioTap_Profile_C()
  sniff(prn=cb_function, offline=sys.argv[1], store=0, count=1)
  #YYY: JC: For MeasureyM.ImportM(, crea)
  sys.exit(0)

if __name__=='__main__':
  main()
