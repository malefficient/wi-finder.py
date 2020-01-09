
########################################
#
#  rtap_ext_util.py
#  Copyright (C) 2019 Johnny Cache <johnycsh@gmail.com>
#
#  Utility functions for manipulating RadioTap headers that utilize Extended bitmasks
#
#################

import sys
from scapy.all import *


####
#
# Inputs: Either a full RadioTap layer (case1), or a RadioTapExtendedPresenceMask (case2)
# Returns: a byte array of length 4 suitable for use as RadioTap.present bitmask
#
def RoundPresentFlags2NoExtended(r):
  if ( type(r) == scapy.layers.dot11.RadioTap):
    #print("    Case1: Hacking present bytes out of radiotap")
    a=int(r.present)

  elif ( type(r) == scapy.layers.dot11.RadioTapExtendedPresenceMask):
    #print("    Case2: Converting RadioTapExtendedPresenceMask")
    z=raw(r)
    #print("    Z = Type:(%s) / len(%s))" % (type(z), len(z)))
    a= struct.unpack('I', z)[0]
  else:
    #print("Warning:RoundPresentFlags2NoExtended Passed invalid parameter ")
    input("Err/Continue")
    return(None)

  #print("    A = Type:(%s) / 0x%08x)" % (type(a), a))

  b =(a & 0x5FFFFFFF)
  #print("    B = Type:(%s) / 0x%08x)" % (type(b), b))
  return b
  ## c = struct.pack('>I', b) #Convert to Big-Endian u_int32_t
  ## print("    C = Type(%s), len(%d) )" % (type(c), len(c)))
  ## return c #byte array in big-endian format with len=4


####
## Input: A scapy packet with 0 or more radiotap headers/extended-headers
## Process: Performs basic sanity checking (most notably ensuring that the minimum set of fields required to generate a useful measurement are present)
##          'Useful' in this context means "contains the minimum amount of data to get a useful measurement"
## Returns: number of useful entries present in packet.
##          Expected value: between 0 and 5 (inclusive)
def CountUsefulRadiotapEntries(pkt):  #In this context 'Useful' is defined as
  ret = 0
  print("    ####CountUsefulRadiotapEntries::Start")
  #pkt.show2()
  if ( not pkt.haslayer(RadioTap)):
    return 0

  R = pkt[RadioTap]

  # if (  ('dBm_AntSignal'in R.present) or ('dBm_AntNoise' in R.present)):
  #   print("        Minimal threshold hit")
  # else:
  #   return 0

  if (not 'Ext' in R.present):
    #print("    Simple case: no extended bitmap")
    num_ext_antenna_ents = 0
    return 1

  num_extended_rtaps= len(R.Ext)
  #print("        OK: We see %d extended radiotap entries, with (%d) bytes unaccounted for (notdecodeD)" % (num_extended_rtaps, len(R.notdecoded)))
  #print("    ####CountUsefulRadiotapEntries::End. Returning %d\n" % (num_extended_rtaps+1))

  return num_extended_rtaps + 1


##  Listify_Radiotap_Headers:
##  Descr: RadioTap headers with 'Extended' present bitmask are poorly supported throughout much software
##         This function will iterate through these complex datatypes, returning a list of simple (not-extended)
##         RadioTap layers. These layers can then be accessed with the convenience of 'normal' RadioTap headers
##  Input: RadioTap layer with 'Extended' bitmap(s) present
##  Returns: a list of 'Basic' (aka, *not* 'Extended') RadioTap layers.
##
def Listify_Radiotap_Headers(pkt):
  if (not pkt.haslayer(RadioTap)):
    return list()

  R0=pkt.getlayer(RadioTap)
  R0=RadioTap(raw(R0)[:R0.len]) #Trim radiotap layer down to include only itself
  #print("####Listify_Radiotap_Headers::Start")
  fixed_list_ret = []

  num_useful_rtaps = CountUsefulRadiotapEntries(pkt)
  if (num_useful_rtaps == 0):
    return ()
  num_extended_rtaps = num_useful_rtaps - 1
  #print("####Listify_Radiotap_Headers:: Working with  extended %d rtap headers " % (num_extended_rtaps))
  ## Convert the 'top-level' RadioTap present bitmask first
  m = RoundPresentFlags2NoExtended(R0)

  ### Begin top-level header conversion
  #print("Raw: len:(%d) %s" % (len(raw(R0)), raw(R0)))
  R0.present=m       #patch in our new bitmask
  R0.notdecoded=None #Otherwise this would contain a copy of the [Ant1][Ant2]..bytes
  R0.len=None        #Scapy help me

  ##NOTE: Since scapy stores the Extended bitmask in 'Ext', we dont need to manually offset them ourselves.

  fixed_list_ret.append(RadioTap(raw(R0)))
  if (num_extended_rtaps == 0):
    print("Simple(er) case. No extended fields to parse")
    return fixed_list_ret

  ######### Start Parsing the extended headers
  #initialize counters
  nbytes_remaining_to_consume      = len(raw(pkt.getlayer(RadioTap).notdecoded))
  nbytes_consumed_so_far           = 0
  window_buff_backing_buff         = pkt.getlayer(RadioTap).notdecoded # XXX unceccesary copy, but easier to read/debug

  ######### Start Parsing the extended headers
  for idx in range(0,num_extended_rtaps):
    #print("nbytes_consumed_so_far: %d" %(nbytes_consumed_so_far))
    #print("nbytes_remainig_to_consume: %d" % (nbytes_remaining_to_consume))

    # Example: The top level radiotap contains 16 notdecoded bytes
    #          The top level radiotap contains 4 extended fields
    #          R0.notdecoded: [aaaabbbbcccccccc]
    #
    # Problem: We know that  R0.notdecoded needs to be split into 4 buffers,
    #          But we don't know the length of each one (and the are not fixed)
    #
    window_buff = window_buff_backing_buff[ nbytes_consumed_so_far: ]

    #print("#########Start parsing Ext R_%d #########" % (idx))
    #Convert the current 'Extended' Radiotap bitmask into /not/ extended version
    curr_bitmask=RoundPresentFlags2NoExtended(pkt.getlayer(RadioTap).Ext[idx])

    ##
    ## Problem:   We don't know the correct length for a radiotap header with the new bitmask we computed.
    ## Solution:  layout the packet in memory, with the remaining notdecoded bytes at the tail.

    lamb_r_buff = b"\x00\x00\x00\x00" #Dummy rtap header
    lamb_r_buff += struct.pack('<I', curr_bitmask)
    buff_notdecoded_yet = pkt.getlayer(RadioTap).notdecoded[nbytes_consumed_so_far:]
    lamb_r_buff += buff_notdecoded_yet
    ## We now have a buffer laid out that starts with a valid radiotap header,
    ## followed by an array of bytes that starts with the correct payload,

    ## ask scapy to interpret the newly refreshed bitmask. Compute RadioTap.len for us
    Lamb_R = RadioTap(raw(RadioTap(lamb_r_buff, len=None)))
    ## Scapy did the math, and has filled in the correct value
    correct_length_for_pkt        = Lamb_R.len
    ## We now know how many bytes have been properly decoded: sizeof(rtap_hdr) - rtap_hdr.len
    curr_buff_size       = correct_length_for_pkt - 8 #Sizeof(Radiotapheader)
    ## Trim the trailing bytes off the notdecoded buffer.
    small_window_buff   = buff_notdecoded_yet[:curr_buff_size]

    ## Create a final radiotap packet (to return), with no extraneous bytes
    full_r_buff = b"\x00\x00\x00\x00" #Dummy rtap header
    full_r_buff += struct.pack('<I', curr_bitmask)
    full_r_buff += small_window_buff
    Full_R=RadioTap(full_r_buff, len=correct_length_for_pkt)

    #Full_R.show()

    ## Update sliding window
    nbytes_consumed_so_far       += curr_buff_size
    nbytes_remaining_to_consume  -= curr_buff_size

    #print("\n\n\n####curr_buff_size: (length of most recent rtap header) :%d" %(curr_buff_size))
    #print("bytes_consumed_so_far: %d" %(nbytes_consumed_so_far))
    #print("bytes_remainig_to_consume: %d" % (nbytes_remaining_to_consume))
    #input("")

    fixed_list_ret.append(Full_R)

  #fixed_list_ret[-1]=fixed_list_ret[-1]/pkt.getlayer(Dot11)
  #wrpcap(filename='R1.pcap',  pkt=fixed_list_ret, linktype=DLT_IEEE802_11_RADIO )
  #print("Intermediate results wrriten to R1.pcap")

  return fixed_list_ret

output_packet_list=[]


#### Radiotap Helper table 
class RadiotapTable():
  ###YYY: Cut and Paste job from scapy/dot11.py
  _rt_present = ['TSFT', 'Flags', 'Rate', 'Channel', 'FHSS', 'dBm_AntSignal',
               'dBm_AntNoise', 'Lock_Quality', 'TX_Attenuation',
               'dB_TX_Attenuation', 'dBm_TX_Power', 'Antenna',
               'dB_AntSignal', 'dB_AntNoise', 'RXFlags', 'TXFlags',
               'b17', 'b18', 'ChannelPlus', 'MCS', 'A_MPDU',
               'VHT', 'timestamp', 'HE', 'HE_MU', 'HE_MU_other_user',
               'zero_length_psdu', 'L_SIG', 'b28',
               'RadiotapNS', 'VendorNS', 'Ext']
 
  ### 'Alternate' names used for brevity when updating display.
  _rt_present_alt = ['TSFT', 'Flags', 'Rate', 'Channel', 'FHSS', 'Signal',
               'Noise', 'Lock', 'TX_Attenuation',
               'dB_TX_Atten', 'dBm_TX_Power', 'Ant',
               'dB_Signal', 'dB_Noise', 'RXFlags', 'TXFlags',
               'b17', 'b18', 'ChannelPlus', 'MCS', 'A_MPDU',
               'VHT', 'timestamp', 'HE', 'HE_MU', 'HE_MU_other_user',
               'zero_length_psdu', 'L_SIG', 'b28',
               'RadiotapNS', 'VendorNS', 'Ext']

  def init(self, R):
    print("RadioTapTable::init")

  def name_to_bit(self, s):
    for i in range(0, len(self._rt_present)):
      if (str(self._rt_present[i])==str(s)):
        return i
    return None

  def alt_name_to_bit(self, s):
    for i in range(0, len(self._rt_present_alt)):
      if (str(self._rt_present_alt[i])==str(s)):
        return i
    return None

  def bit_to_name(self, b):
    print("RadioTapTable::bit_to_descr(%d): %s" % (b, self._rt_present[b]))
    return self._rt_present[b]

  def bit_to_name_alt(self, b):
    print("RadioTapTable::bit_to_name_alt(%d): %s" % (b, self._rt_present_alt[b]))
    return self._rt_present_alt[b]


#Call back argument for scapy.sniff, stores the results in g
def cb_function(pkt):
  global outfname
  my_helper_table = RadiotapTable()
  ret_list=Listify_Radiotap_Headers(pkt)

  for i in range(0, 8):
    s = my_helper_table.bit_to_name_alt(i)
    print("%d: %s" % (i, s))
    s = my_helper_table.alt_name_to_bit(s)
    print("%d: %s" % (i, s))
    print("---")
  
  return
  for r in ret_list:
    my_helper_table.init(r)

  return 
  wrpcap(filename=outfname, pkt=ret_list, append=True, linktype=DLT_IEEE802_11_RADIO )
  return

outfname=None
def main():
  global outfname
  
  if (len(sys.argv) == 3):
    infname = sys.argv[1]
    outname = sys.argv[2]
  
  elif (len(sys.argv) == 2):
    infname = sys.argv[1]
    outfname = "%s-out.pcap" % (infname)
  
  else:
    print("%s: input.pcap output.pcap" % (sys.argv[0]))
    sys.exit(0)
  
  sniff(prn=cb_function, offline=infname, store=0, count=1)
  
 
if __name__=='__main__':
  main()

