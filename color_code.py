import math
import sys
import sty

class ColorClass():
    """Class that can convert between different color formats.
       Internally stored as a floats between 0.0 and 1.0 of 4 elements (alpha, blue, green, red)"""
    def __init__(self):
        self.val = [1.0, 1.0, 1.0, 1.0]

    def set_float(self, f):
        """Set color with a list of abgr floating point values between 0.0 and 1.0
        if  a list of len 3 is passed in, a default alpha of 1.0 will be used"""
        if (len(f) == 4): 
            #Alpha value included
            self.val = f
        if (len(f) == 3): 
            #Alpha value not passed in
            self.val = f
            self.val[0] = 1.0
            self.val[1] = f[0]
            self.val[2] = f[1]
            self.val[3] = f[2]
    def set_int(self, i):
        """Set color with a list of abgr floating point values between 0.0 and 1.0
        if  a list oi len 3 is passed in, a deiault alpha oi 1.0 will be used"""
        if (len(i) == 4): 
            #Alpha value included
            for j in range(0, 4):
                if (i[j] < 0):
                    self.val[j] = 0.0
                if (i[j] > 255):
                    self.val[j] = 1.0
                else:
                    self.val[j] = float(i[j]/255.0)

        if (len(i) == 3): 
            #Alpha value not passed in
            self.val[0] = 1.0
            for j in range(1, 4):
                self.val[j] = float(i[j-1]/255.0)

    def str_bgr(self):
       """ Return a tuple of strings to be used in KML plots. Always sets alpha to full"""
       return "ff%02x%02x%02x" % (self.val[1]*255, self.val[2]*255, self.val[3]*255)
    def str_abgr(self):
       """Alpha Blue Green Red representation, suitable for KML"""
       return "%02x%02x%02x%02x" % ( int(self.val[0]*255), int(self.val[1]*255), int(self.val[2]*255), int(self.val[3]*255))
    def str_rgb(self):
       """Red Green Blue representation, suitable for almost everything"""
       return "%02x%02x%02x" % ( int(self.val[3]*255), int(self.val[2]*255), int(self.val[1]*255))
    def sty_color(self):
        """Return sty.register.FgRegister color"""
        r = int(self.val[3] * 255)
        g = int(self.val[2] * 255)
        b = int(self.val[1] * 255)
        c=sty.fg(r,g,b)
        return(c)
    def __str__(self):
        """Default to conole escape character """

        return str(self.sty_color());



def generate_colorband(mag, m_min, m_max, DistanceScaling='Linear'):
    if (DistanceScaling == 'Linear'):
        print("#### Generating colorband(%d,%d%d) with Linear scaling" % (mag, m_min, m_max))
    elif (DistanceScaling=='Exponential'):
        print("#### Generating colorband(%d,%d%d) with Exponential scaling" % (mag, m_min, m_max))


def normalize_sig_linear(self, sig, MaxSig, MinSig):
    """Given a signal and a range , will return a ratio between 0.0 and 1.0 representing where
        sig falls between P.MinSignalLeven and P.MaxSignalLevel"""
    a = -1.0 * MaxSig
    b = -1.0 * MinSig
    range_to_cover = b - a
    SigOffsetFromBottom = b + sig

    ratio_covered = SigOffsetFromBottom / b
    return ratio_covered
def exponentialize_sig(self, sig, MaxSig, MinSig):
    """ turn sig into expoential distance..Halve MetersToMaxSig for ever 3dB between sig and MaxSig"""
    a = -1.0 * MaxSig
    b = -1.0 * MinSig
    c = -1.0 * sig
    range_to_cover = b - a

    #print ("a:%d b:%d c:%d" % (a,b,c))
    db_from_top =   c - a

    y = db_from_top / 3
    #print("y: %f" % (y))
    ret = math.pow(2, (P.exp_max- y))
    #ret += P.MeterFloor
    #print("Sig = %d, db_rom_top= %d", sig, db_from_top)
    #print("ret = %f" % (ret))
    #sys.stdin.read(1)
    return ret
  
  
def compute_signal_intensity(mag, m_max, m_min):
    #positivify these annoying negative numbers
    m_min = math.fabs(m_min)
    m_max = math.fabs(m_max)
    my_spread = math.fabs(m_min - m_max)
    db_above_min = m_min - math.fabs(mag)
    if (db_above_min > my_spread):
        print("compute_signal_color: Warning input value (%d) > max (%d)" %(mag, m_max))

    numerator = 3.0 * db_above_min
    denominator = my_spread
    if (denominator != 0):
        intensity = numerator/denominator
    else:
        intensity = 1 #Theres only one signal reading.
    print("###Return intensity from 0.0->3.0")
    return intensity

def compute_signal_color(mag, m_max, m_min):
    """Takes in mag, m_max, m_min  in dB. returns a color scaled approriately"""
    intensity = compute_signal_intensity(mag, m_max, m_min)
    blue_percent = green_percent = red_percent = 0.0
    print("#### comput_signal_color::\n  #### Intensity(%d,%d,%d) = %3.2f" % (mag, m_max, m_min, intensity))
    print("    #### Intensity varies from 0.0-3.0. ")
    if (intensity > 2.0):
        blue_percent = intensity - 2.0;
        intensity -= blue_percent;
    if (intensity > 1.0):
        green_percent = intensity - 1.0;
        intensity -= green_percent;
    red_percent =  intensity;
    C = ColorClass()
    C.set_float ([1.0, blue_percent, green_percent, red_percent])
    return C


### dBm_to_ArrRSSI(in, ref=-75) (dBm to Arrbitrary RSSI)
### return scalar value expressing input in terms of reference value.

### dBm_to_ArrRSSI(-55, -75) =  100.0
### dBm_to_ArrRSSI(-62, -75)    20.0
### dBm_to_ArrRSSI(-65, -75) =   10.0
### dBm_to_ArrRSSI(-75, -75) =    1.0
### dBm_to_ArrRSSI(-85, -75) =  -10.0
### dBm_to_ArrRSSI(-95, -85) = -100.0

#Diverging color scheme:
###   (#################   ref   #####################)

#color codes will end up being /logarithmic/ of deltas. Otherwise:
### (dBm_to_ArrRSSI(-65, -75)) = 10       (ref) ########## (10)
### (dBm_to_ArrRSSI(-62, -75)) ~ 20       (ref) ########## (10) ########## (20) ########## (30) ########## (40) ....
### (dBm_to_ArrRSSI(-59, -75)) ~
# What we want. (Or at least, the best we can do as human beings with limited capacity for scale is:)
### (dBm_to_ArrRSSI(-65, -75)) = 10       (ref) # (1)
### (dBm_to_ArrRSSI(-55, -75)) = 100      (ref) ## (2)

#   Q: What is a 'human' sized chunk of dBm window? 
#  Or: What is a human sized linear scale that we can express 
#
#    Lets say a slider bar or '20' hashes to the right.

## delta = 10, 
## dBm_to_ArrRSSI(-55, -75)        # =  100.0  // (delta = 20)
## ArrRSSI_to_dBm(100) = 20
## ArrRSSI_to_dBm(10)  = 10
## ArrRSSI_to_dBm(1)   = 0
## ArrRSSI_to_dBM(0.1) = -10
## ArrRSSI_to_dBm(0.001) = -20
   
#### ArrRSSI (Arrrbitrary-RSSI) is a unit defined by the following convserions
## ArrRSSI_to_dBm(100) = 20      dBm_toArrRSSI(20) = 100
## ArrRSSI_to_dBm(10)  = 10      dBm_toArrRSSI(10) = 10
## ArrRSSI_to_dBm(1)   = 0       dBm_toArrRSSI(0)  = 1
## ArrRSSI_to_dBM(0.10) = -10    dBm_toArrRSSI(-10) = 0.10
## ArrRSSI_to_dBm(0.01) = -20    dBm_toArrRSSI(-20) = 0.01



def ArrRSSI_to_dBm(arrRSSI):
    
    if (arrRSSI < 0.000001) and (arrRSSI > -0.000001): #Special case: 0
        print("#### ArrRSSI_to_dBm:(%d)~~(0)   = (1) (special case)" % (arrRSSI))
        return 1
    
    if (arrRSSI < 0.000001):  #Special case: negative argument.  return 1/ret.
        ret =  math.log(-1*arrRSSI, 10) * 10.0
        print("#### ArrRSSI_to_dBm:(%d) = %3.2f" % (arrRSSI, -1 * ret))
        return -1 * ret
    else:
        ret =  math.log(arrRSSI, 10) * 10.0
        print("#### ArrRSSI_to_dBm:(%d)=%3.2f " % (arrRSSI, ret))
        return ret


def dBm_to_ArrRSSI(sig, ref):
    return_negative = False
    delta =  (-1 * ref) - (-1 * sig) 
    if (delta < 0.00000001) and (delta > -0.00000001):  #special case: 0 dBm delta
        print("#### dBm_toArrRSSI:(%d, %d)  :: special case (0). Returning 1  " % (sig, ref))      
        return 1 #
    if (delta < 0): #special case, negative
        return_negative = True
        delta *= -1.0
    x = delta / 10
    ret =  math.pow(10,x)
    if (return_negative):
        print("#### dBm_toArrRSSI:(%d, %d)  :: delta = %d  x = %d, ret = 10^x :: %3.2f" % (sig, ref, delta, x, -1*ret))
        return (-1 * ret)
    else:
        print("#### dBm_toArrRSSI:(%d, %d)  :: delta = %d  x = %d, ret = 10^x :: %3.2f" % (sig, ref, delta, x, ret))
        return ret 



def main():
    max=-55
    min=-75
    curr=-55
    
    print("sys.argc = %d" % (len(sys.argv)))
    if len (sys.argv) > 4:
        print("Error. To many arguments passed to %s" % (sys.argv[0]))
        sys.exit(0)
    if (len(sys.argv) > 3):
        min=int(sys.argv[3])
    if (len(sys.argv) > 2):
        max=int(sys.argv[2])
    if (len(sys.argv) > 1):
        curr=int(sys.argv[1])

    delta_l=[30, 25, 21, 20, 19, 16, 13, 10, 0, -10, -13, -16, -19, -20, -21, -25, -30]
    rssi_l = []
    ret_delta_l=[]
    #Workaround expecting reference
    for d in delta_l:
        r = dBm_to_ArrRSSI(min + d, min)
        rssi_l.append(r)

    for r in rssi_l:
        d=ArrRSSI_to_dBm(r)
        ret_delta_l.append(d)
    return
    # dBm_to_ArrRSSI(-55, -75)        # =  100.0  // (delta = 20)
    # dBm_to_ArrRSSI(-56, -75)        # ~~  80.0  // (delta = 19)
    # dBm_to_ArrRSSI(-59, -75)        # ~~  40.0  // (delta = 16)
    # dBm_to_ArrRSSI(-62, -75)        # ~~  20.0  // (delta = 13)
    # dBm_to_ArrRSSI(-65, -75)        # =   10.0  // (delta = 10)
    # dBm_to_ArrRSSI(-75, -75)        # =    1.0  // (delta = 0.0)
    # dBm_to_ArrRSSI(-85, -75)        # =  -10.0  // (delta = -10)
    # dBm_to_ArrRSSI(-95, -75)        # = -100.0

    dbm_l  = [ 30, 23, 21, 20, 10, 9, 6, 3, 1, 0, 'X', 0, -1, -3, -6, -9,  -10, -20, -21, -23, -30  ]         #// equivalent to 20 dBm .    is equivalent to 10 dBm  ~ .00000 dBm    ~-0.00000 dBm       -10
     
    for l in rssi_l:
        r = ArrRSSI_to_dBm(l)
        print("ArrRSSI_to_dBm(%d)=%3.2f"% (l, r))
        print("Aka:  A delta of %d ArrRSSI required %3.2f dBm delta" % (l, r))
        input("Y/n?")
        
    delta_l = [20, 19, 16, 13, 10, 0.0, -10, -20]
    for d in delta_l:
        dBm_to_ArrRSSI() 
    return    
    generate_colorband(curr, max, min)
    return
    c = compute_signal_color(curr, max, min)
    print(" Color(RGB): 0x%s" % (c))
    i = compute_signal_intensity(curr, max, min)
    print(" Intensity: %3.2f" % (i))
    #i = compute_signal_intensity_n(curr, max, min)
    print ("type returned: %s" % (type(i)))
    print("'Normalized' intensity: %3.2f" % (i))

    print("#### TODO: Get a sty.fg generated from (within?) compute_signal_color. Maybe make default to_str return a sty.fg.color?")
    return
if __name__ == '__main__':
    main()