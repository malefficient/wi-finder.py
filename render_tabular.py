from Rtap_Char import  MeasureyM, RadiotapTable
from color_code import color_w
from sys import exit
import sty
import random
import math
from Energy_Scaler import Energy_scale_class
from colorcet import isolum as isolum
from sty import Style, RgbFg, fg, bg, ef, rs  #(Foreground, BackGround, Effects, Reset)
from functools import reduce
from itertools import chain

##render_tabular todo: 
## Figure out an easy way to map each column in the output table to an associated/appropriate color palette.
## (Quick and easy approach: if (curr_header_name.begins_with(Sig)) -> use heatmap.) if (Lock) -> other scale. Else: Pick a static color,theme.
## The column heading->color pallete map can / should(?) be shared between the tabular render engine, and the _tbd_ histogram renderer.
##

def generate_wifinder_samples():

    ## To speed development, sample data already stored in dictionary form
    ### Mac Measurements contain both Signal and Noise
    m_d_1={2: [12.0], 3: [2412.0], 5: [-64.5], 6: [-96.0], 7: []}
    m_d_2={2: [12.0], 3: [2412.0], 5: [-56.5], 6: [-98.0], 7: []}
    mac_m = [m_d_1, m_d_2]
    Mac_m=[]
    for m in mac_m:
        M=MeasureyM()
        M.Measurey_Map = m
        Mac_m.append(M)

    ### Lin measurements contain Lock_Quality, Signal *n_antenna (but no noise)
    l_i_1={2: [12.0], 3: [2462.0], 5: [-47.5, -46.0, -44.0, -47.0, -51.0], 6: [], 7: [73.0]}
    l_i_2={2: [12.0], 3: [2462.0], 5: [-44.5, -45.0, -42.0, -42.0, -56.0], 6: [], 7: [78.0]}
    lin_m = [l_i_1, l_i_2]
    Lin_m=[]
    for m in lin_m:
        M=MeasureyM()
        M.Measurey_Map=m
        Lin_m.append(M)
    return Mac_m, Lin_m


def ascii_print_example_columns():
    data = [['NAME', 'AGE', 'HANDEDNESS', 'SCORE (%)'],
        ['Martin', 38, 'L', 54.123],
        ['Marty', 33, 'L', 32.438],
        ['Martyne', 49, 'R', 24.472],
        ['Marteen', 91, 'L', 1.128]]

    rows = [('apple', '$1.09', '80'), ('truffffle', '$58.01', '2')]
    dash = '-' * 40
    lens = []
 
    print("#####Method one: Constant whitespace padding and varied alignment")
    for i in range(len(data)):
        if i == 0:
            print(dash)
            print('{:<10s}{:>4s}{:>12s}{:>12s}'.format(data[i][0],data[i][1],data[i][2],data[i][3]))
            print(dash)
        else:
            print('{:<10s}{:>4d}{:^12s}{:>12.1f}'.format(data[i][0],data[i][1],data[i][2],data[i][3]))
   
    print("###Method tw0: Cleverly generate format string dynamically.")
    for col in zip(*rows):                         #ZIP: Return a list of tuples, where each tuple contains the i-th element. Exactly what we want!
        lens.append(max([len(v) for v in col]))
    #print("lens: %s" % (lens))
    format = "  ".join(["{:<" + str(l) + "}" for l in lens])
    for row in rows:
        print(format.format(*row))
    

#YYY: field_selector is a generalization from 'bit_no'. Antenna0.Sig, Antenna1,sig, Antenna2.sig share bit numbers. 
#     Later we will (hopefully) have a nice map of (header_index, or _bitno_fieldno) -> colorcet_pallete.
#     For now field_selector is a placeholder. 
def colorcet_wrapper_ret_color(intensity, field_selector):
    """Given intensity (in percent), return appropriate color given currently selected pallete"""
    C=color_w()
    intensity = int(math.floor(2.55 * intensity))
    #print("####colorcet_wrapper_ret_color((%s))" % (intensity))
    h=isolum[intensity].lstrip('#')                   #RGB encoded as hex string
    _rgb=tuple(int(h[i:i+2], 16) for i in (0, 2, 4))  #Magic list comprehension turns hex into decimal.
    C.set_int(_rgb)
    return C

def new_get_color(bitno, _val_in):
    """ Temporary shim so that we have an (almost) drop in replacement for old_get_color TODO: needs to consider the field type (by 'bitno' or other means"""
    E = Energy_scale_class()
    E.init_linear_scale(-52, 20) # XXX: Obvs, this cant/wont stay here. 
    C=color_w()
    #print("####new_get_color: bit_no:(%d)  _val_in:(%d)" % (bitno, _val_in))
    if (bitno != 5): #If not signal, return early. (E_NOT_HANDLED_YET)
        C.set_int([255,255,255])
        return C

    if (bitno == 5):
        intensity = E.process_input_dBm_ret_percent(_val_in) 
        #input("####new_get_color: Handing base case (Signal. val:(%d), intensity(%f)" % (_val_in, intensity))
        if (intensity > 100.0 or intensity < -100.0):
            print("Signal dBm_in registers as %f percent (_literally_ off the scale)" % (intensity))
            print("Returning constant: red")
            C.set_int([255,0,0])
            return C
        else:
            C = colorcet_wrapper_ret_color(intensity, field_selector=bitno) # See YYY above
            return C
def old_get_color():
    a,b,c=random.randint(0,255),random.randint(0,255),random.randint(0,255)
    r = sty.fg(a,b,c)
    return r

##YYY: JC: TODO: The end goal should be to have two different 'rendering engines'.
##               The 'classic' tabular/column based output, (initially implemented in the MeasureyM_text_Renderer)
##               And the alternate 'histogram' approach.  
##               Conceptually these two visualizations are rendering/require access to the exact same state across both.
##               It remains unclear how much potential there is for code reuse 
class Render_Tabular_C:
    initialized=False
    cnt=0
    rtap_table_helper = RadiotapTable()
    header_list={}
    col_width={}
    num_entries={}
    num_cols=0
    column_order=[3,7,5,6]

    #TODO:  re-factor:  we can replace these various flat_column_attribue_N data structures as single NamedTuple
    #                   This would also make the rever mapping (from flattened header display name) to actual rtap bitno less weird
    flat_column_headings = []
    flat_column_widths=[]
    flat_column_fmt_strs=""
    flat_column_reverse_bitno=[]
    def init(self, M):
        self.header_list.clear()
        self.col_width.clear()
        self.num_entries.clear()
        self.flat_column_headings.clear()
        self.flat_column_widths.clear()
        self.flat_column_reverse_bitno.clear()
        self.flat_column_fmt_strs=""
        
        self.num_cols=0
        self.colors_enabled = 0
        self.left_margin="        "
        #print("###MeasureyM_text_Renderer::Init()")
        self.initialized = True
        
        # Init should be passed a MeasureyM that resembles those it is expected to later process and output.
        # We perform as much one-time-only formatting work here, so that print() can be relatively fast.
        # Code within the init function is optimized for clarity over performance. 

        ## First up. Iterate all of the fields we want to display. If a field contains multiple values (I.e., Signal reading from N antennas)
        ## Break the 'top' level header up into N numbered values (Signal -> Sig.0, Sig.1, Sig.2, ..)

        
        for b in self.column_order:  
            self.num_entries[b]=len(*M.Measurey_Map[b])
        
        for b in self.column_order:# First pass: Figure out if any expected fields are missing values.
            if self.num_entries[b] == 0:
                print("    Warning: Unexpected case. 0 data entries for field:(%d)" % (b))
                print (" EXPERIMENTAL: Removing bit b (%d) from self.column_orders)" % (b))
                #print("Pre:: %s" % (self.column_order))
                self.column_order.remove(b)
            
        ##print(self.column_order)
        ##print(self.num_entries)
        ##print(M.Measurey_Map)
        ##input("QQ")

        for b in self.column_order:
            curr_h = self.rtap_table_helper.bit_to_name_alt(b)
            if self.num_entries[b] == 0:
                print("Errror: Unexpected case in init. (0 length num entries. Should be handled earlier.)")
                sys.exit(0)
            elif self.num_entries[b] > 0:
                print ("   XXZ Render_Table_C::init Tricky case. Need to break b:(%d) (%s) into %d cols" % (b,curr_h, self.num_entries[b]))
                for idx in range(0, self.num_entries[b] ):
                    if (idx == 0):
                        c_h = '{}'.format(curr_h,idx)
                    else:
                        c_h = '{:.3}.{:d}'.format(curr_h,idx)  ## 'Antenna 1 -> Ant.1, Antenna2 -> Ant.2
                    self.flat_column_headings.append(c_h)
                    self.flat_column_reverse_bitno.append(b)
                    #print("    %s" % (c_h))
                    self.flat_column_widths.append(10)        #TODO: Compute this dynamically later
                    self.flat_column_fmt_strs += (rs.all + "|" + "{}" + "{:^10.8}" + rs.all)   #TODO: Also this.

        self.num_flat_headings = len(self.flat_column_headings)
        print("   Pretty_P::Init Generated %d Flattened headings: %s" % ( self.num_flat_headings, self.flat_column_headings))
        ##print("   Pretty_P::Init from %s %s" % (M, M.Measurey_Map))
        input("Pretty_P::Init::end")


    def ret_header(self):
        if (self.initialized == False):
            print(" Error. Measurey_M::Print  called before init() ")
            exit()
        #print("    #### header column length list: %s" % (self.flat_column_widths))
        header_fmtstr_complete="" 
        spacer_str=""
        for i in range(0,  len(self.flat_column_headings)):
            cell_w = self.flat_column_widths[i]
            
            curr_c_fmt_s= rs.all +  "|" +  fg.white + "{: ^%d.%d}" % (cell_w, cell_w-2)   ##TODO: fill in '8' dynamically
            blanks_f_t=rs.all + "|" + "{:-^%d}" % (cell_w) 
            
            spacer_str += blanks_f_t.format("-")
            header_fmtstr_complete += curr_c_fmt_s
        #print("    ### Header column format string: (%s) " % (header_fmtstr_complete))
        #print("    ### Head column flat headers   : (%s) " % (self.flat_column_headings))
        ret  =  rs.all + self.left_margin + spacer_str + "|\n" +\
                rs.all + self.left_margin + header_fmtstr_complete.format(*self.flat_column_headings) +  rs.all + "|\n" +\
                rs.all + self.left_margin + spacer_str + "|"
        return ret
    def print(self, M):
        if (self.initialized == False):
            print(" Error. Measurey_M::Print  called before init() ")
            exit()
       
      
        ##print("%s" % (M.Measurey_Map))
        ### Flatten the arguments in M
        ## The simple / naive approach to flattening Measurey_Map to flat_values_list is below
        ##values_l = reduce(lambda x,y: x+y, list(M.Measurey_Map.values()))  # Flatten measurey_map
        values_l=[]
        ## However, this approach forgets to take column order into account.
        ## Unsure if there is a more efficient way to do this. I'm sure there is a less verbose one though.
        
        for b in self.column_order:    #self.column_order has been minified by init() to skip fields that were empty in init()
            curr_f = M.Measurey_Map[b]
            if (len(curr_f) == 0):
                input("Error Print asked to format field (%d), but no values included in input" % (b))
                sys.exit(0)
                continue
            else:
                values_l.extend(curr_f)
        #print("#### len(values_l):(%d)  values_l:(%s) <--should be flattened M.map" %  (len(values_l), values_l))
        #print("#### len(flat_column_headings):(%d),   (%s)" % (len(self.flat_column_headings), self.flat_column_headings))
        if len(values_l) != len(self.flat_column_headings):
            print("#### Warning: print() passed Measurey_M with %d entries. Expected %d" % (len(values_l), len(self.flat_column_headings)))
            input("Kk")

       
       
       
        ### TODO: We need to iterate over each field,value, in a manner that we can reasonably fill in the selected Renderer 
        ###       on the type of data. (I.e., 'Signal', 'Lock', or ?)
        colors_l = []
        for idx in range(0, len(self.flat_column_headings)):
            colors_l.append ( new_get_color( self.column_order[idx], values_l[idx]))
        

        ### colors for a given value (colors_l, values_l) 
        ### Interleave the color codes and corresponding values in a single list.
        colorized_data = list(chain.from_iterable(zip(colors_l, values_l))) #Interleave computed colors with actual row contents
        #row_string=pffft.format(*colorized_data)
        #print("%s" % (row_string))
   
        out = self.left_margin + self.flat_column_fmt_strs.format(*colorized_data) + rs.all + "|"
        self.cnt += 1
        print(out)

def basic_tst(M):
    print("#### Basic_tst::start Generate some parallel colormaps")
    cell_w=10

    value_list=[12, 2412, -68, -97]
    colors_list=[]
    num_cols=len(value_list)
    start_cell=rs.all + "|"
    for idx in range (0, num_cols):
        c,d,e=random.randint(0,255),random.randint(0,255),random.randint(0,255)
        cc = fg(c, d, e)
        colors_list.append(cc)

    cell_data_fmtstr=str(rs.all + "|" + '{}' +  "{: ^%d}"%(cell_w)  + rs.all)
    pffft = num_cols * cell_data_fmtstr
    colorized_data = list(chain.from_iterable(zip(colors_list, value_list))) #Interleave computed colors with actual row contents
    row_string=pffft.format(*colorized_data)
    print("%s" % (row_string))
    return row_string
def main():
    Pretty_P = MeasureyM_text_Renderer()
    Mac_M,Lin_M=generate_wifinder_samples()

    #basic_tst(Mac_M[0])
    #
    # clexit(0)    
    ### Mac Data ###
    Pretty_P.init(Mac_M[0])
    print( Pretty_P.ret_header())
    #Pretty_P.print(Mac_M[1])

    for m in Mac_M:
        Pretty_P.print(m)
    # sys.exit(0)
    ### Linux data ###
    Pretty_P.init(Lin_M[0])
    print( Pretty_P.ret_header())
    #Pretty_P.print(Lin_M[1])
    for m in Lin_M:
        Pretty_P.print(m)
    #print("")

if __name__=='__main__':
    main()
    #ascii_print_example_columns()