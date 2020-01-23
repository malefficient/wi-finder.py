
import sys
import sty
import random

from math_dbm_util import *
class ColorClassW():
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


#### ArrRSSI (Arrrbitrary-RSSI) is a unit I toyed with before setting on micro-watts
##   It is defined  by the following convserions
## ArrRSSI_to_dBm(100) = 20      dBm_toArrRSSI(20) = 100
## ArrRSSI_to_dBm(10)  = 10      dBm_toArrRSSI(10) = 10
## ArrRSSI_to_dBm(1)   = 0       dBm_toArrRSSI(0)  = 1
## ArrRSSI_to_dBM(0.10) = -10    dBm_toArrRSSI(-10) = 0.10
## ArrRSSI_to_dBm(0.01) = -20    dBm_toArrRSSI(-20) = 0.01

# Micro-watt to dBm/ dBm_to_micro-watt: self-describing



def dBm_to_microwatt_test(dBm_l):
    microwatt_l=[]
    synthesized_dBm_l=[]
    for r in dBm_l:
        microwatt_l.append(dBm_to_micro_watt(r))

    f=' {:7.7f},'*len(dBm_l)
    s=f.format(*dBm_l)
    print("####          dBm in: [%s]" % (s))
    s= f.format(*microwatt_l)

    print("#### micro-watt_out : [%s]" % (s))
    print("---------Flip side----------")
    s= f.format(*microwatt_l)    
    print("#### micro-watt_in : [%s]" % (s))
    
    for mw in microwatt_l:
        synthesized_dBm_l.append(micro_watt_to_dBm(mw))

    s=f.format(*synthesized_dBm_l)
    print("#### dBm out       : [%s]" % (s))

    return 0

def microwatt_to_dBm_test(mw_l):
    synthesized_dBm_l=[]
    for m in mw_l:
        synthesized_dBm_l.append(micro_watt_to_dBm(m))

    f=' {:7.7f},'*len(mw_l)
    s=f.format(*mw_l)
    print("####          micro-watt in: [%s]" % (s))
   
    s= f.format(*synthesized_dBm_l)

    print("#### dBm out          : [%s]" % (s))
    return 0
    print("---------Flip side----------")
    s= f.format(*microwatt_l)    
    print("#### micro-watt_in : [%s]" % (s))
    
    for mw in microwatt_l:
        synthesized_dBm_l.append(micro_watt_to_dBm(mw))

    s=f.format(*synthesized_dBm_l)
    print("#### dBm out       : [%s]" % (s))

def solve_for_x_factor(dBm_in, multiplier=20):
    microwatt_in=dBm_to_micro_watt(dBm_in)
    microwatt_in_20 = multiplier * microwatt_in
    dBm_out = micro_watt_to_dBm(microwatt_in_20)
    print("#### Solving for x-factor(%s, %d)" % (dBm_in, multiplier))
    print("    dBm_in: (%s) -> microwatts: (%s)" %(dBm_in, microwatt_in))
    print("    microwatts_in: (%s) times %d =  %s" %(microwatt_in, multiplier, microwatt_in_20))
    print("    %s microwatts  -> dBm %s" % ( microwatt_in_20, dBm_out))
    print("     %d times %s dBm = %s dBm " % (multiplier, dBm_in, dBm_out))
    x = dBm_out / dBm_in
    print("    'Cuz that would make our X-Factor %s" % (x))
    return x
    
def test_x_factor(in_dBm, multiplier):
    print("#### Test x factor: %3.2f, %d" % (in_dBm, multiplier))
    y = in_dBm

    twenty_x_ret_scale=[]
    delta_dbm_l = []
   
    while ( y < 0):
        x = solve_for_x_factor(y, multiplier)
        y = y * x
        twenty_x_ret_scale.append( (y))
      
    
    f=' {:}\n'*len(twenty_x_ret_scale)
    s=f.format(*twenty_x_ret_scale)
    print("     %s" % (s))
    print("--- in more english ---")
    print("   stepping up from %d dBm by linear multiplier of %d" % (in_dBm, multiplier))
    
    #print("%3.7s" % (twenty_x_ret_scale))
    #return

def gen_color_scale(dBm_center, scaleFactor=30, stepsize=3):
    print("#### gen_color scale(%d, %d %d)" % (dBm_center, scaleFactor, stepsize))
    
    color_scale={}

    for x in range(1, scaleFactor + stepsize, stepsize):
        print("    %d" % (x))
    exit(0)    
    uW_in=dBm_to_micro_watt(in_dBm)
    microwatt_in_times_x = scale_factor * uW_in
    dBm_max = micro_watt_to_dBm(microwatt_in_times_x)

    #in_uW=dBm_to_micro_watt(in_dBm)
    microwatt_in_divided_by_x = (1/in_multiplier) * uW_in
    dBm_min = micro_watt_to_dBm(microwatt_in_divided_by_x)


    #uW_max = dBm_to_micro_watt(dBm_max)
    #uW_min = dBm_to_micro_watt(dBm_min)
    print("    gen_color_range(): dBm_min:(%3.2f) dBm_in:(%3.2f) dBm_max:(%3.2f)" % (dBm_min, in_dBm, dBm_max))
    
    input("")
    ### Okay
    return


def print_conversion_table(dBm_in):
    print("#### Conversion table")
    a = dBm_to_milliwatt(dBm_in)

    b = milliwatt_to_microwatt(a)

    c = milliwatt_to_nanowatt(a)
    
    d = milliwatt_to_picowatt(a)

    print ("%d (dBm) |  %f (mw)  |  %3.7f (uw)  |  %3.7f (nw)  | %3.7f (pw) |" %(dBm_in,a,b,c,d))


    return

def gen_color_range(in_dBm, in_multiplier):
    print("#### gen_color range(%d, %d)" % (in_dBm, in_multiplier))
   
    uW_in=dBm_to_micro_watt(in_dBm)
    dBm_max = micro_wattz_to_dBm(microwatt_in_times_x)

    #in_uW=dBm_to_micro_watt(in_dBm)
    microwatt_in_divided_by_x = (1/in_multiplier) * uW_in
    dBm_min = micro_watt_to_dBm(microwatt_in_divided_by_x)

    #uW_max = dBm_to_micro_watt(dBm_max)
    #uW_min = dBm_to_micro_watt(dBm_min)
    print("    gen_color_range(): dBm_min:(%3.2f) dBm_in:(%3.2f) dBm_max:(%3.2f)" % (dBm_min, in_dBm, dBm_max))
    
    input("")
    ### Okay
    return
 
class Color_scale_class():
    """Maps signal strength (in dBm) to three different dimensions: Color (over CoverPallete), Scalar, and percent. """
    color_scale = {} 
    color_pallete = "pastel" #YYY map these to the 'colorcet' (or similar) equivalents


    #YYY: Replace these variables with a named_tuple class. Equally readable, more maintainable
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

   

    ###  ---  ###
    def __init__(self, pallete_name="default"):
        self.color_pallete = pallete_name
    def _initialize_units_table(self, _mw_bottom, _mw_center, _mw_top):
        print("#### Conversion table")
        a = _mw_bottom
        b = milliwatt_to_microwatt(a)
        c = milliwatt_to_nanowatt(a)
        d = milliwatt_to_picowatt(a)
        self.bottom_scale_in_milliwatts  = a
        self.bottom_scale_in_microwatts  = b
        self.bottom_scale_in_nanowatts   = c
        self.bottom_scale_in_picowatts   = d
        self.bottom_scale_in_dBm = milliwatt_to_dBm(a)

        a = _mw_center
        b = milliwatt_to_microwatt(a)
        c = milliwatt_to_nanowatt(a)
        d = milliwatt_to_picowatt(a)
        self.center_scale_in_milliwatts  = a
        self.center_scale_in_microwatts  = b
        self.center_scale_in_nanowatts   = c
        self.center_scale_in_picowatts   = d
        self.center_scale_in_dBm = milliwatt_to_dBm(a)

        a = _mw_top
        b = milliwatt_to_microwatt(a)
        c = milliwatt_to_nanowatt(a)
        d = milliwatt_to_picowatt(a)
        self.top_scale_in_milliwatts  = a
        self.top_scale_in_microwatts  = b
        self.top_scale_in_nanowatts   = c
        self.top_scale_in_picowatts   = d
        self.top_scale_in_dBm = milliwatt_to_dBm(a)

    def init_center_scale(self, dBm_in, multiplier=20):
        """ Scale will be defined as self.center_scale == dBm_in == 1X. top and bottom will be +/- center times X)"""  
          
        _a = dBm_to_milliwatt(dBm_in)
        _t =  multiplier * _a
        _b = (1/multiplier) * _a
        self._initialize_units_table(_b, _a, _t)
        # Todo: follow up with other units
        
        print("#### Color_scale_class: init_center_scalee(%s, %d)" % (dBm_in, multiplier))
        
        ## f_ext_fmt="{:}  {:} dBm -> milliwatts:{:.3f} -> microwatts:{:.3f} ->nanowatts:{:.3f} ->picowatts:{:.3f}"
        ## s=f_ext_fmt.format( *("Bottomsies", int(self.bottom_scale_in_dBm), self.bottom_scale_in_milliwatts, self.bottom_scale_in_microwatts, self.bottom_scale_in_nanowatts, self.bottom_scale_in_picowatts))
        ## s=f_ext_fmt.format( *("Centerdoo", int(self.center_scale_in_dBm), self.center_scale_in_milliwatts, self.center_scale_in_microwatts, self.center_scale_in_nanowatts, self.center_scale_in_picowatts))
        ## s=f_ext_fmt.format( *("Toppletop", int(self.top_scale_in_dBm), self.top_scale_in_milliwatts, self.top_scale_in_microwatts, self.top_scale_in_nanowatts, self.top_scale_in_picowatts))
        f_simple_fmt="{:}  {:} dBm -> milliwatts:{:.9f}"
        s=f_simple_fmt.format( *("Bottom_scale", int(self.bottom_scale_in_dBm), self.bottom_scale_in_milliwatts))
        print("%s" % (s))
        s=f_simple_fmt.format( *("center_scale", int(self.center_scale_in_dBm), self.center_scale_in_milliwatts))
        print("%s" % (s))
        s=f_simple_fmt.format( *("   top_scale", int(self.top_scale_in_dBm), self.top_scale_in_milliwatts))
        print("%s" % (s))
        return

            
    def ret_percent(self, in_dBm):
        """ return a value between 0-100 that represents the input parameters location ranging from self.bottom to self.top """
        # I.e. set
        a = dBm_to_milliwatt(in_dBm)
        ret_percent = (a/self.top_scale_in_milliwatts) * 100.0      
        print("####ret_percent: dBm(%3.1f)/dBm(%3.1f))" % (in_dBm, milliwatt_to_dBm(self.top_scale_in_milliwatts)))
        print("    ret_percent: %3.1f%%" % (ret_percent))
        return ret_percent
        
    def __str__(self):
        ret_str =  ("ColorScale_(uW)  bottom:(%s)  (%s) top:(%s)" % (self.bottom_in_microwatts, self.microwatt_center, self.top_in_microwatts))
        ret_str += ("ColorScale_(dBm) bottom:(%s)  (%s) top:(%s)" % (self.bottom_in_dBm, self.dBm_center, self.top_in_dBm))
        return ret_str
def main():
    max=-55
    min=-75
    curr=-75
    
    C = Color_scale_class()
    C.init_center_scale(int(sys.argv[1]), int(sys.argv[2]))
    d = C.ret_percent(int(sys.argv[1]) + 10)
    #C.print_conversion_table(curr)
    return
    
    print("%03d dBm is %07.8f micro_watts, or %7.8f nano-watts" % (curr, A, B))
    return
    #C = Color_scale_class()
    #C.set_scale(-75, 20) ###YYY: TODO: round these values to either int()'s or output them cleaner
    #print("%s" % (C))
    #gen_color_scale(-67, 20, 1)
    #return
    test_x_factor(-82, 20 )
    return
    #x = solve_for_x_factor(-90, 18)
    return
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
    #print("############ Delta dBm to microwatt comparison########")
    #delta_dbm_l=[ -75, -67, 45  -1, 0, 1, 3, 10]
    #dBm_to_microwatt_test(delta_dbm_l)
    
    print("")
    print("###########  microwatt to dBm comparison#########")
    milliwatt_test_l = [1, 1.25892]
    microwatt_test_l = [1000*x for x in milliwatt_test_l]
    microwatt_to_dBm_test(microwatt_test_l)
    return
    ### After studying the previous tables, I think that a colorbar should resemble:
    ###         -13.01dBm                                +13.01dBm
    ###          CCCCCCCCCCCCCCC   [REF]    CCCCCCCCCCCCCCC
    ###         -20 rRSSI                               +20  rRSSI
    return
    ### YYY JC pickup here YYY
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