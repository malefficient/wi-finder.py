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