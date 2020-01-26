
import sys
import random
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
        input('KYC')
    
    def _initialize_units_table(self, _mw_bottom, _mw_center, _mw_top):
        self.bottom_scale_in_mw = _mw_bottom
        self.bottom_scale_in_nanowatts = milliwatt_to_nanowatt(_mw_bottom)        
        self.bottom_scale_in_dBm = milliwatt_to_dBm(_mw_bottom)

        self.center_scale_in_mw = _mw_center
        self.center_scale_in_nw  = milliwatt_to_nanowatt(_mw_center)
        self.center_scale_in_dBm = milliwatt_to_dBm(_mw_center)

        self.top_scale_in_mw = _mw_top
        self.top_scale_in_nw = milliwatt_to_nanowatt(_mw_top)
        self.top_scale_in_dBm = milliwatt_to_dBm(_mw_top)

        #Convenience variables derived from above
        self.span_in_mw = self.top_scale_in_mw - self.center_scale_in_mw
        self.span_in_nw = milliwatt_to_nanowatt(self.span_in_mw)
        self.span_in_dBm = milliwatt_to_dBm(self.span_in_mw)

       
    ##                                  [  -------Range------]
    ##                                    center plus slot_space_mw 
    ##                              Px0  Px(1/10) Range 
    ##  | -9 | ~~ | -3 | -2 | -1 |  0  | +1 | +2 | +3 |~~| + 9 |
    ##                             Mx1  Mx2  Mx3  Mx4 |~~| Mx10|
    ##                                                     Mx10 will be 10 times **center**. That is how the scale manages to stay relevant to the location in dBm space
    #      
    def init_center_scale(self, dBm_in, multiplier=20):
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
        # Todo: follow up with other units
        
        print("#### Energy_scale_class: init_linear_scale2(%s, %d)" % (dBm_in, multiplier))
        return

    def init_linear_scale3(self, _center_mw, _slice_width_mw, _slice_num=20):
        """ Scale will be defined as self.center_scale == dBm_in == 1X. top and bottom will be +/- center times X)"""  
        ### For now we assume a simple 1:1 mapping between num_slots:slot
        self.descr = "Scaling algorithm 3: repeat multiplier times slot_size out in both directions"
        # Todo: follow up with other units
        
        print("#### Energy_scale_class: init_linear_scale2(%s, %d)" % (dBm_in, multiplier))
        return


    def process_input_dBm_ret_percent(self, in_dBm):
        """ returns a TBD named tuple that contains the results of input value in _T _B _D space"""
        a = dBm_to_milliwatt(in_dBm)
        ###                                             
        ### We need to treat the scale like this:  - 100.0%  <-----------|   | ------------->|  + > 100.0%
        ### That  means, comparing input to center, deciding which directio to go, then computing distance from center to input
        if (a >= self.center_scale_in_mw):
            print("#### Positive percent case")
            ret_percent = (self.center_scale_in_mw + a) / (self.top_scale_in_mw)
        else:
            print("#### Negative percent case")
            ret_percent = (self.center_scale_in_mw - a) / (self.bottom_scale_in_mw)
        ret_percent *= 100.0
        input("in_dBm (%d) is %s perent of scale" % (in_dBm,ret_percent))
        return ret_percent 
        

        print("####ret_percent: dBm(%3.1f)/dBm(%3.1f))" % (in_dBm, milliwatt_to_dBm(self.span_in_mw)))
        print("    ret_percent: %3.1f%%" % (ret_percent))
        return ret_percent

    def __str__(self):
        ret_str=""
        f_simple_fmt="{:}  {:} dBm -> milliwatts:{:.9f}\n"
        ret_str += f_simple_fmt.format( *("Bottom_scale", int(self.bottom_scale_in_dBm), self.bottom_scale_in_mw))
        ret_str += f_simple_fmt.format( *("Center_scale", int(self.center_scale_in_dBm), self.center_scale_in_mw))
        ret_str += f_simple_fmt.format( *("   top_scale", int(self.top_scale_in_dBm), self.top_scale_in_mw))

        ret_str +="----------- <    %s(nanowatts)   %s(milliwatts)   %d[dBm]  >------\n" % (self.span_in_nw, self.span_in_mw, self.span_in_dBm)
        ret_str +="##  Scale.span: %d(dBm)\n##  Scale.span:%3.7f (mW)\n" % (self.span_in_dBm, self.span_in_mw)
        ret_str +="##  Scale.bottom: %d (dBm)  --->  Scale.top :%3.7f (dBm)\n" % (self.bottom_scale_in_dBm, self.top_scale_in_dBm)
        ret_str +="##  Scale.top:  %3.7f(mW)   --->  Scale.span:%3.7f (mW)\n" % (self.bottom_scale_in_mw, self.top_scale_in_mw)
        ret_str +="----------- <    %s(nanowatts)   %s(milliwatts)   %d[dBm]  >------\n" % (self.span_in_nw, self.span_in_mw, self.span_in_dBm)

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
    C.init_center_scale(a, b)
    print(" %s " % (C))
    C.process_input_dBm_ret_percent(  a + c)
    #C.process_input_dBm_ret_percent(a + 0)
    #C.process_input_dBm_ret_percent(a - 3)
    return
    
    print("%03d dBm is %07.8f micro_watts, or %7.8f nano-watts" % (curr, A, B))
    print("sys.argc = %d" % (len(sys.argv)))


   
if __name__ == '__main__':
    main()