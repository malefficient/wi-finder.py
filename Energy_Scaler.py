
import sys
import random
from math import floor, ceil, fabs
from dbm_unit_conversion import *




    
class Energy_scale_class():
    """Handles scale / perspective on signal strengths """
    Initialized = False
    descr=""
    top_scale_in_dBm = None
    top_scale_in_mw = None
    
    center_scale_in_dBm = None
    center_scale_in_mw = None
    
    bottom_scale_in_dBm = None
    bottom_scale_in_mw = None

    span_in_mw=None
    span_in_dBm=None
    
    num_slots=None
    slot_width=None #in Mw
    SlotScale_l=[]
    def __init__(self):
        self.Initialized = True
        print("### Engery_Scale_class::Init()")
        #input('KYC')
    
    def _initialize_units_table(self, _mw_bottom, _mw_center, _mw_top):
        self.bottom_scale_in_mw = _mw_bottom
        self.bottom_scale_in_nw = milliwatt_to_nanowatt(_mw_bottom)        
        self.bottom_scale_in_dBm = milliwatt_to_dBm(_mw_bottom)

        self.center_scale_in_mw = _mw_center
        self.center_scale_in_nw  = milliwatt_to_nanowatt(_mw_center)
        self.center_scale_in_dBm = milliwatt_to_dBm(_mw_center)

        self.top_scale_in_mw = _mw_top
        self.top_scale_in_nw = milliwatt_to_nanowatt(_mw_top)
        self.top_scale_in_dBm = milliwatt_to_dBm(_mw_top)

        #Convenience variables derived from above
        self.span_in_mw = self.top_scale_in_mw - self.bottom_scale_in_dBm
        self.span_in_microwatts = milliwatt_to_microwatt(self.span_in_mw)
        self.span_in_nw = milliwatt_to_nanowatt(self.span_in_mw)
        self.span_in_dBm = milliwatt_to_dBm(self.span_in_mw)

       
          
    def init_center_scale5(self, dBm_in, multiplier=20):
        """ Scale will be defined as self.center_scale == dBm_in == 1X. top and bottom will be +/- center times X)"""  
        ### For now we assume a simple 1:1 mapping between num_slots:slot
        self.descr = "Scaling algorithm 1: (initial) set center_scale"
        _cent = dBm_to_milliwatt(dBm_in)
        _top =  multiplier * _cent
        _btm = (1/multiplier) * _cent
        self._initialize_units_table(_btm, _cent, _top)
        # Todo: follow up with other units
        
        print("#### Energy_scale_class: init_center_scale(%s, %d)" % (dBm_in, multiplier))
        return
    def init_linear_scale2(self, dBm_in, multiplier=20):
        """ Scale will be defined as self.center_scale == dBm_in == 1X. top and bottom will be +/- center times X)"""  
        ### For now we assume a simple 1:1 mapping between num_slots:slot
        self.descr = "Scaling algorithm 2: (slice_width = distance_in_mw(center,  center + 1 dBm). Scale out 20 x width in both directions"
        _cent = dBm_to_milliwatt(dBm_in)
        _top =  multiplier * _cent
        _btm = (1/multiplier) * _cent
        self._initialize_units_table(_btm, _cent, _top)
        
        # Todo: follow up with other units
        
        print("#### Energy_scale_class: init_linear_scale2(%s, %d)" % (dBm_in, multiplier))
        
        return

    
    def init_linear_scale(self, _center_dBm, multiplier=20):
        """ center_scale == dBm_in. top and bottom: center +/- delta(dBm_in, dBm_in+1) * X)"""  
        ### For now we assume a simple 1:1 mapping between num_slots:slot
        self.descr = "#3)init_linear_scale == dBm_in. top and bottom: center +/- delta(dBm_in, dBm_in+1) * X)"""
        self.scale_X=int(multiplier)
        # Todo: follow up with other units
        _cent = dBm_to_milliwatt(_center_dBm)
        _top =  multiplier * _cent
        _btm = (1/multiplier) * _cent
        self._initialize_units_table(_btm, _cent, _top)
        print("#### Energy_scale_class: init_linear_scale2(%s, %d)" % (_center_dBm,multiplier))
        return


    def process_input_dBm_ret_percent(self, in_dBm):
        """ returns a TBD named tuple that contains the results of input value in _T _B _D space"""
        a = dBm_to_milliwatt(in_dBm)
        
        ###                                             
        ### We need to treat the scale like this:  - 100.0%  <-----------|   | ------------->|  + > 100.0%
        ### That  means, comparing input to center, deciding which directio to go, then computing distance from center to input
        if (a >= self.center_scale_in_mw):
            delta_to_100=(self.top_scale_in_mw - self.center_scale_in_mw)
            delta_to_a=(a - self.center_scale_in_mw)
            print("#### Positive percent case:\n####center_in_mw=%3.7fmw in_dBm=%3.7fmw" %(self.center_scale_in_mw, a))
            ret_percent = (delta_to_a) / (delta_to_100)
        else:
            delta_to_100=(self.center_scale_in_mw - self.bottom_scale_in_mw)
            delta_to_a=(self.center_scale_in_mw - a)
            print("#### Negative percent case")
            ret_percent = (delta_to_a) / (delta_to_100)
        
        ret_percent *= 100.0  #Round return value up an convert to percent
        ret_percent=int(math.ceil(ret_percent)) 
        
        input("in_dBm (%d) is %s perent of scale" % (in_dBm,ret_percent))
        return ret_percent 
        

    def summary(self):
        ret_str=""
        left_margin="        "  
        x_in_nanowatts = milliwatt_to_nanowatt (dBm_to_milliwatt(self.center_scale_in_dBm + 1) -  dBm_to_milliwatt(self.center_scale_in_dBm))
        ret_str+= left_margin + "Scale summary: Center (0) = %3.1fdBm\n" % (self.center_scale_in_dBm)
        ret_str+= left_margin + "          'x': Δ(center + 1dBm, center) = %.4fnW\n" % (x_in_nanowatts) 
        ret_str+= left_margin + "        %d'x':  %.4fnW\n" % ( self.scale_X, self.scale_X * x_in_nanowatts) 
    

        ret_str +="##  Scale.span: %d(dBm)        %3.7f(mW)\n" % (self.span_in_dBm, self.span_in_mw)
        ret_str +="##  Scale.bottom: %d (dBm)  --->  Scale.top :%3.7f (dBm)\n" % (self.bottom_scale_in_dBm, self.top_scale_in_dBm)
        ret_str +="##  Scale.top:  %3.7f(mW)   --->  Scale.span:%3.7f (mW)\n" % (self.bottom_scale_in_mw, self.top_scale_in_mw)
        ret_str +="----------- <    %s(nanowatts)   %s(milliwatts)   %d[dBm]  >------\n" % (self.span_in_nw, self.span_in_mw, self.span_in_dBm)

        return ret_str
    def __str__(self, width=40):
        left_margin=' '*8
        width_2 = int(width/2)
        marker_str = "| " + int(floor(width/2) -1)*' ' + '|' + int(floor(width/2) -1)*' ' + ' |' + '\n'
        
        t="{: ^%d}\n" % (width+4)
        ret_str  = left_margin + t.format("Energy Scalar Table") 

        ret_str += left_margin
        t="{: ^%d}" % int(floor((width/2)))
        ret_str += t.format(' ')
        t="{:-^%d}" % int(ceil((width/2)+1))
        ret_str +='[' + t.format(  "  (%.1f) µW  "%(self.span_in_microwatts)  ) +']'
        ret_str += "\n"        

        
        
    
        #ret_str=l"###########Energe Scalar Table############\n"
        ###                                                 #| f="{:3.1f}dBm"
        ### -85                 -72                    -59  #| 
        ###  |                   |                      |   #
        ###  #################### ######################|   #
        ###  |                   |                      |
        ### -20x                 1x                   +20x  #

        f="{:3.1f}dBm"  ### Begin first line of scale 
        dbm_line_l= [ f.format(self.bottom_scale_in_dBm), f.format(self.center_scale_in_dBm), f.format(self.top_scale_in_dBm)]
        space_length = int(floor(width/2))  - len(dbm_line_l[0])
        ret_str += left_margin + dbm_line_l[0] + space_length*' ' + dbm_line_l[1] + space_length*' ' + dbm_line_l[2] + '\n'
        ret_str += left_margin + marker_str
       

        hashmark_line = "| " + int(floor(width/2) -1)*'#' + ' ' + int(floor(width/2) -1)*'#' + ' |' + '\n'
        ret_str += left_margin + hashmark_line
        ret_str += left_margin + marker_str
        f="{:+3d}x"  ### Multiplier line of scale
        x_line_l= [ f.format(-1 * self.scale_X), f.format(1), f.format(1 * self.scale_X)]
        space_length = int(floor(width/2))  - len(x_line_l[0])
        ret_str += left_margin + x_line_l[0] + space_length*' ' + x_line_l[1] + space_length*' ' + x_line_l[2] + '\n'


       
        return ret_str

def main():

    a=-72
    b=+20
    c=-69
    if (True == True):
        if len (sys.argv) > 4:
            print("Error. To many arguments passed to %s" % (sys.argv[0]))
            sys.exit(0)
        if (len(sys.argv) > 3):
            c=int(sys.argv[3])
        if (len(sys.argv) > 2):
            b=int(sys.argv[2])
        if (len(sys.argv) > 1):
            a=int(sys.argv[1])


    C = Energy_scale_class()
    C.init_linear_scale(a, b)
    print(" %s " % (C))
    C.process_input_dBm_ret_percent(  a + c)
    #C.process_input_dBm_ret_percent(a + 0)
    #C.process_input_dBm_ret_percent(a - 3)
    return
    
    print("%03d dBm is %07.8f micro_watts, or %7.8f nano-watts" % (curr, A, B))
    print("sys.argc = %d" % (len(sys.argv)))


   
if __name__ == '__main__':
    main()