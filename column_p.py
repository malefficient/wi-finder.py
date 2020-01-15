from Rtap_Char import  MeasureyM, RadiotapTable

from sys import exit
import random
from sty import Style, RgbFg, fg, bg, ef, rs  #(Foreground, BackGround, Effects, Reset)
from functools import reduce
from itertools import chain

### COlorscheme notes:
## Virdis (bokeh) purple->yellow
## Spectral (bokeh) red->yellow->purple
### Bokeh:  CategoricalColorMapper : https://docs.bokeh.org/en/latest/docs/user_guide/categorical.html#userguide-categorical
### source = ColumnDataSource(data=dict(fruits=fruits, counts=counts, color=Spectral6))
### factor_cmap('fruits', palette=Spectral6, factors=fruits)
### TODO: Should I pick a static coor map (or two), do the math to normalize dB myself, and just use offset?
####      Or, would it be better to let brokeh dynamically generate one based on the range itself?

#Additionally, you can also use any of the 256-color perceptually uniform Bokeh palettes from the external colorcet package, if it is installed.
#In the context of Bokeh, a palette is a simple plain Python list of (hex) RGB color strings. For example the Blues8 palette which looks like 
#['#084594', '#2171b5', '#4292c6', '#6baed6', '#9ecae1', '#c6dbef', '#deebf7', '#f7fbff']



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
    


def get_color():
    a,b,c=random.randint(0,255),random.randint(0,255),random.randint(0,255)
    cc = fg(a, b, c)
    return cc

class MeasureyM_text_Renderer:
    initialized=False
    cnt=0
    rtap_table_helper = RadiotapTable()
    header_list={}
    col_width={}
    num_entries={}
    num_cols=0
    column_order=[3,7,5,6,2]
    flat_column_headings = []
    flat_column_widths=[]
    flat_column_fmt_strs=""
    def init(self, M):
        self.header_list.clear()
        self.col_width.clear()
        self.num_entries.clear()
        self.flat_column_headings.clear()
        self.flat_column_widths.clear()
        self.num_cols=0
        self.flat_column_fmt_strs=""

        self.colors_enabled = 0
        self.left_margin="        "
        print("###MeasureyM_text_Renderer::Init()")
        self.initialized = True
        input("III")
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
                print("Pre:: %s" % (self.column_order))
                self.column_order.remove(b)
            
        print(self.column_order)
        print(self.num_entries)
        print(M.Measurey_Map)
        input("QQ")

        for b in self.column_order:
            curr_h = self.rtap_table_helper.bit_to_name_alt(b)
            if self.num_entries[b] == 0:
                print("Errror: Unexpected case in init. (0 length num entries. Should be handled earlier.)")
                sys.exit(0)
            elif self.num_entries[b] > 0:
                #print ("   XX Tricky case. Need to break b:(%d) (%s) in %d cols" % (b,curr_h, self.num_entries[b]))
                for idx in range(0, self.num_entries[b] ):
                    if (idx == 0):
                        c_h = '{}'.format(curr_h,idx)
                    else:
                        c_h = '{:.3}.{:d}'.format(curr_h,idx)  ## 'Antenna 1 -> Ant.1, Antenna2 -> Ant.2
                    self.flat_column_headings.append(c_h)
                    #print("    %s" % (c_h))
                    self.flat_column_widths.append(10)        #TODO: Compute this dynamically later
                    self.flat_column_fmt_strs += (rs.all + "|" + "{}" + "{:^10.8}" + rs.all)   #TODO: Also this.

        self.num_flat_headings = len(self.flat_column_headings)
        print("   Pretty_P::Init Generated %d Flattened headings: %s" % ( self.num_flat_headings, self.flat_column_headings))
        print("   Pretty_P::Init from %s %s" % (M, M.Measurey_Map))
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
        colors_l = []
        for idx in range(0, len(self.flat_column_headings)):
            colors_l.append ( get_color())
        

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