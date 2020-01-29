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
        self.top_span_in_dBm = math.fabs( self.top_scale_in_dBm - self.center_scale_in_dBm)
        self.top_span_in_mw = math.fabs(self.top_scale_in_mw - self.bottom_scale_in_mw)
        self.top_span_in_microwatts = milliwatt_to_microwatt(self.top_span_in_mw)
        self.top_span_in_nw = milliwatt_to_nanowatt(self.top_span_in_mw)
       
        self.bot_span_in_dBm = math.fabs( self.center_scale_in_dBm - self.bottom_scale_in_dBm)       
        self.bot_span_in_mw = math.fabs(self.center_scale_in_mw - self.bottom_scale_in_mw)
        self.bot_span_in_microwatts = milliwatt_to_microwatt(self.bot_span_in_mw)
        self.bot_span_in_nw = milliwatt_to_nanowatt(self.bot_span_in_mw)

        self.mw_in_hashmark = self.top_span_in_mw / self.top_span_in_hashmarks
        self.nw_in_hashmark =  milliwatt_to_nanowatt(self.mw_in_hashmark)


    def init_linear_scale(self, _center_dBm, multiplier=20, col_width=40):
        """ center_scale == dBm_in. top and bottom: center +/- delta(dBm_in, dBm_in+1) * X)"""  
        ### For now we assume a simple 1:1 mapping between num_slots:slot
        self.descr = "#3)init_linear_scale == dBm_in. top and bottom: center +/- delta(dBm_in, dBm_in+1) * X)"""
        self.scale_X=int(multiplier)
        self.col_width = col_width
        self.top_span_in_hashmarks = int(self.col_width / 2) #top and bottom n_hashmarks will vary by different scale types
        self.bot_span_in_hashmarks = int(self.col_width / 2)
        self.top_span_in_X = int(multiplier/2)
        self.bot_span_in_X = int(multiplier/2)
        # Todo: follow up with other units
        _cent = dBm_to_milliwatt(_center_dBm)
        _top =  multiplier * _cent
        _btm = (1/multiplier) * _cent
        self._initialize_units_table(_btm, _cent, _top)
        print("#### Energy_scale_class: init_linear_scale2(%s, %d)" % (_center_dBm,multiplier))
        print("%s" % (self.__str__()))
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
        
        print("in_dBm (%d) is %s perent of scale" % (in_dBm,ret_percent))
        return ret_percent 
        
    def summary(self, width=40):
        ret_str=""
        left_margin="        "  

        ##Okay, some assumptions: 
        ## 'width' divided by two on either side of zero hasmar
        n_hashmarks = width
        hashmarks_per_nw = self.top_span_in_nw / width
        hashmarks_per_mw = self.top_span_in_mw / width

        one_quarter_top_mark = self.top_span_in_hashmarks / 4
        one_quarter_top_mw =   self.top_span_in_mw / 4

        x_in_nanowatts = milliwatt_to_nanowatt (dBm_to_milliwatt(self.center_scale_in_dBm + 1) -  dBm_to_milliwatt(self.center_scale_in_dBm))
        ret_str+= left_margin + "Scale summary: Center (0) = %3.1fdBm\n" % (self.center_scale_in_dBm)
        ret_str +=left_margin + "#####    Scale.top.span: %3.1f(dBm) %3.3f(nW) %3d (hashmarks)\n" % (self.top_span_in_dBm, self.top_span_in_nw, 
        self.top_span_in_hashmarks)
        ret_str +=left_margin + "#####   1x'#':%2d    '#' ()\n" % ( (self.top_span_in_hashmarks / self.top_span_in_dBm))
#        ret_str +=left_margin + "#####            Scale.neg_one+_half_x_marks.span: %d(nW)\n" % (self.top_span_in_nw)

  


        ##ret_str+= left_margin + "          'x': Δ(center + 1dBm, center) = %.4fnW\n" % (x_in_nanowatts) 
        ##ret_str+= left_margin + "        %d'x': %.4fnW\n\n" % ( self.scale_X, self.scale_X * x_in_nanowatts) 
       
        
        return ret_str
    def __str__(self):


        left_margin=' '*8
        width=self.col_width
        width_2 = int(width/2)
        ref_marker_str = "| " + int(floor(width/2) -1)*' ' + '|' + int(ceil(width/2) -1)*' ' + ' |' + '\n'
        
        t="{: ^%d}\n" % (width+4)
        ret_str  = left_margin + t.format("Scale: '#': %3.1fnW  [Energy Scalar Table]" % (self.nw_in_hashmark) ) 

        ret_str += left_margin
        t="{: ^%d}" % int(floor((width/2)))
        ret_str += t.format(' ')
        t="{:-^%d}" % int(ceil((width/2)+1))
        ret_str +='[' + t.format(  "  (%.1f) nW  "%(self.top_span_in_nw)  ) +']'
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
        dbm_mark_str = dbm_line_l[0] + space_length*' ' + dbm_line_l[1] + space_length*' ' + dbm_line_l[2] + '\n'
        ret_str += left_margin +dbm_mark_str
        
        neg50_mark_str = ref_marker_str[:int(ceil(self.top_span_in_hashmarks/2))] + '|-50%' + ref_marker_str[int(ceil(self.bot_span_in_hashmarks/2))+5:] 
        ret_str += left_margin + neg50_mark_str
       

        hashmark_line = "| " + int(floor(width/2) -1)*'#' + ' ' + int(floor(width/2) -1)*'#' + ' |' + '\n'
        hashmark_line = ref_marker_str.replace(' ', '#')
        ret_str += left_margin + hashmark_line

      
        f="{:+2d}x"  ### Multiplier line of scale
        one_x_in_hashmarks= int(ceil(self.top_span_in_hashmarks / self.top_span_in_X))
        three_x_in_hashmarks= int(ceil(3 * self.top_span_in_hashmarks / self.top_span_in_X))
        x_line_l= [ f.format(-1 * self.bot_span_in_X), ' ', f.format(1 * self.top_span_in_X)]
        space_length = int(floor(width/2))  - len(x_line_l[0])
        X_line_str = x_line_l[0] + space_length*' ' + x_line_l[1] + (space_length)*' ' + x_line_l[2] + '\n'
        
        #ret_str += left_margin+ X_line_str
        plus_3_x_str = X_line_str[:self.bot_span_in_hashmarks + three_x_in_hashmarks] + '|+3x' +  X_line_str[0+self.bot_span_in_hashmarks + three_x_in_hashmarks:] 
        ret_str += left_margin + plus_3_x_str
       
        ret_str += "\n---------\n"
        
        ret_str += self.summary(width)
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
    C.init_linear_scale(a, b, c)
    #print(" %s " % (C))
    #print(" %s " % (C.summary()))

    C.process_input_dBm_ret_percent(  a + c)
    #C.process_input_dBm_ret_percent(a + 0)
    #C.process_input_dBm_ret_percent(a - 3)
    return
    
    print("%03d dBm is %07.8f micro_watts, or %7.8f nano-watts" % (curr, A, B))
    print("sys.argc = %d" % (len(sys.argv)))


   
if __name__ == '__main__':
    main()