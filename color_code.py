
import sys
import sty
import random
from colorcet import CET_L17 as isolum
from dbm_unit_conversion import *
from Energy_Scaler import Energy_scale_class
class color_w():
    """Color wrapper: Provides simple abstraction layer for expressing an RGB(A) color in common formats"""
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

def compute_signal_color_from_ppi_viz(mag, E):
    """Takes in mag, m_max, m_min  in dB. returns a color scaled approriately"""
    intensity = E.process_input_dBm_ret_percent(mag)
    intensity=math.fabs(intensity * 3/100.0)
    print("####compute_signal_color_from_ppi_viz: doctred intensity level set to: %f" % (intensity))
    input("")
    blue_percent = green_percent = red_percent = 0.0
    #print("    #### Intensity varies from 0.0-3.0. ")
    if (intensity > 2.0):
        blue_percent = intensity - 2.0;
        intensity -= blue_percent;
    if (intensity > 1.0):
        green_percent = intensity - 1.0;
        intensity -= green_percent;
    red_percent =  intensity;
    C = color_w()
    C.set_float ([1.0, blue_percent, green_percent, red_percent])
    return C

def compute_signal_color_from_colorcet(mag, E):
    """Takes in mag, scale E. Should probably makeit simply take a percent later though."""
    intensity = E.process_input_dBm_ret_percent(mag)
    C=color_w()

    if (intensity > 100.0 or intensity < -100.0):
        print("Warning: compute_signal_color input is (literally) off the charts")
        C.set_float ([1.0, 0.5, 0.8, 0.2])

        return C
    intensity = int(math.floor(2.55 * intensity))
    h=isolum[intensity].lstrip('#') #RGB encoded as hex string
    _rgb=tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    C.set_int(_rgb)
    print(_rgb)
    print("RGB as tuple" )
    input("Ck")
    return C


def ret_color_from_percent(mag):
    """Takes in mag, scale E. Should probably makeit simply take a percent later though."""
    intensity=mag
    C=color_w()

    if (intensity > 100.0 or intensity < -100.0):
        print("Warning: compute_signal_color input is (literally) off the charts")
        C.set_float ([1.0, 0.5, 0.8, 0.2])
        return C
    intensity = int(math.floor(2.55 * intensity))
    h=isolum[intensity].lstrip('#') #RGB encoded as hex string
    _rgb=tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    C.set_int(_rgb)
    return C


class parallell_color_scale():
    S=None #S is for 'Scale'
    def __init__(self, _s, _pal=None):
        print("####parallell_color_scale:__init__()")
        self.S = _s
        self.palette_name=_pal
    def __str__(self):
        return super().__str__()
    def init(self, p=None):
        self.pallete_name=p
        return


def print_pallete(_pal):
    C=color_w()
    ret_s=""
    for i in range(0, 255):
        h=_pal[i].lstrip('#') #RGB encoded as hex string
        _rgb_pal=tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        C.set_int(_rgb_pal)
        ret_s+= "%s@" %  (C)
    ret_s += sty.rs.all
    print(ret_s)
    return ret_s
def test_color(a, b, c):
    print("#### %s:test_color(%d,%d,%d)"  % (sys.argv[0],a,b,c))
    E = Energy_scale_class()
    E.init_linear_scale(a,b,c)
    P = parallell_color_scale(E)
    P.init("A")
    print("%s" % (E))
    print("%s" % (E.summary()))


    C=color_w()
    ret_s=""
    for i in range(0, 100):        
        c=ret_color_from_percent(i)
        ret_s+= "%s#" %  (c)
    ret_s+=sty.rs.all
    print(ret_s)
    return ret_s

def main():
    a=-75
    b=20
    c=40
    if (True == True): #For  folding
        if len (sys.argv) > 4:
            print("Error. To many arguments passed to %s" % (sys.argv[0]))
            sys.exit(0)
        if (len(sys.argv) > 3):
            c=int(sys.argv[3])
        if (len(sys.argv) > 2):
            b=int(sys.argv[2])
        if (len(sys.argv) > 1):
            a=int(sys.argv[1]) 

    print_pallete(isolum)
    test_color(a,b,c)

 
if __name__ == '__main__':
    main()