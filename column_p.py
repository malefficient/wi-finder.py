from Rtap_Char import  MeasureyM, RadiotapTable

from sys import exit
from functools import reduce




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
    
    
class MeasureyM_text_Renderer:
    initialized=False
    rtap_table_helper = RadiotapTable()
    header_list={}
    col_width={}
    num_entries={}
    num_cols=0
    column_order=[3,2,7,5,6]
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
        # Init should be passwd a MeasureyM that resembles those it is expected to later process and output.
        # We perform as much one-time-only formatting work here, so that print() can be relatively fast.
        # Code within the init function is optimized for clarity over performance. 

        ## First up. Iterate all of the fields we want to display. If a field contains multiple values (I.e., Signal reading from N antennas)
        ## Break the 'top' level header up into N numbered values (Signal -> Sig.0, Sig.1, Sig.2, ..)

        for b in self.column_order:
            self.num_entries[b]=len(M.Measurey_Map[b])
        #print("    MeasureyM_Renderer::Init. Num entries map:\n    %s" % (self.num_entries))
        for b in self.column_order:
            curr_h = self.rtap_table_helper.bit_to_name_alt(b)
            if self.num_entries[b] == 0:
                print("    Warning: Unexpected case. 0 data entries for field:(%d) (%s)" % (b,  curr_h))
                input("Q")

            elif self.num_entries[b] == 1:
                self.flat_column_headings.append(curr_h)
                self.flat_column_widths.append(10)
                self.flat_column_fmt_strs += ("|{:^10.8}")
            elif self.num_entries[b] > 1:
                #print ("   XX Tricky case. Need to break b:(%d) (%s) in %d cols" % (b,curr_h, self.num_entries[b]))
                for idx in range(0, self.num_entries[b]):
                    c_h = '{:.3}.{:d}'.format(curr_h,idx)
                    self.flat_column_headings.append(c_h)
                    #print("    %s" % (c_h))
                    self.flat_column_widths.append(10)        #TODO: Compute this dynamically later
                    self.flat_column_fmt_strs += ("|{:^10.8}")   #TODO: Also this.
        self.num_flat_headings = len(self.flat_column_headings)
        #print("   Generated %d Flattened headings: %s" % ( self.num_flat_headings, self.flat_column_headings))


    def ret_header(self):
        if (self.initialized == False):
            print(" Error. Measurey_M::Print  called before init() ")
            exit()
        #print("    #### header column length list: %s" % (self.flat_column_widths))
        header_fmtstr_complete="" 
        spacer_str=""
        if (self.colors_enabled):
            print("    Measurey_M_Renderer::Header TODO: Echo 'Normal' escape character to terminal")    
        for i in range(0,  len(self.flat_column_headings)):
            cell_w = self.flat_column_widths[i]
            curr_c_fmt_s= "|{: ^%d.%d}" % (cell_w, cell_w-2)   ##TODO: fill in '8' dynamically
            curr_c_spacer_s="|{:-^%d}" % (cell_w)
            blanks_f_t="|{:-^%d}" % (cell_w) 
            spacer_str += blanks_f_t.format("-")
            header_fmtstr_complete += curr_c_fmt_s
        #print("    ### Header column format string: (%s) " % (header_fmtstr_complete))
        #print("    ### Head column flat headers   : (%s) " % (self.flat_column_headings))
        
        ret =   self.left_margin + spacer_str + "|\n" +\
                self.left_margin + header_fmtstr_complete.format(*self.flat_column_headings) + "|\n" +\
                self.left_margin + spacer_str + "|"
        #print("%s" % (ret))
        #input("Kk")
        return ret
    def print(self, M):
        if (self.initialized == False):
            print(" Error. Measurey_M::Print  called before init() ")
            exit()
        #print("###MeasureyM_text_Renderer::Print()")
        #print("    Passed: %s" % (M.Measurey_Map))
       
        #need_header=True
        #if (need_header):
        #    print("%s" % self.ret_header(M))

        ### TODO: Flatten the arguments in M
        #print("%s" % (M.Measurey_Map))
        f_l = reduce(lambda x,y: x+y, list(M.Measurey_Map.values()))
        #print(" ### reduce result: %s" % (f_l))
        #print(" ### row fmt string: %s" % (self.flat_column_fmt_strs))
        out = self.left_margin + self.flat_column_fmt_strs.format(*f_l) +"|"
        print(out)
class column_MeasureyM_PrintShop:
    rtap_table_helper = RadiotapTable()
    
    #### TODO: Generate column headings from rtap_helper
    def print(self, M):
        header_list={}
        col_width={}
        num_entries={}
        num_cols=0
        column_order=[3,2,7,5,6]
        #for b in M.Measurey_Map.keys():
        ##Todo: Iterate over Measurey_Map.keys looking for empty data columns
        ##      Remove empty fields from column_order
        
        ### Step 1: Generate top level table header labels  "#| Chann | Rate  |  Lock  | ...."
        for b in column_order:
            header_list[b]=(self.rtap_table_helper.bit_to_name_alt(b))
            num_entries[b]=len(M.Measurey_Map[b])
            col_width[b]=(len(header_list[b]))
        print("###%2d)\n%s\n%s\n%s\n" % (b, header_list, num_entries, col_width))
        num_cols=len(list(header_list.values()))
        max_col_width = max( list(col_width.values()))+2 ##Todo: This needs to consider cases when num_entries[b] > 1
        print("Max col width: %s" %(max_col_width))
      
        h_f_t= '|{: ^%d.5}' % (max_col_width)
        fft  = num_cols * h_f_t
        formattedList = fft.format(*list(header_list.values())) + "|"
        print("%s" % (formattedList)) #---Line 1: column headers 
        #### End Step 1

        ### Step 1.2: Print pretty column header lines (" |---------|--------|....")
        blanks_f_t="|{:-^%d}" % (max_col_width) 
        B=blanks_f_t.format("X")
        Bb=num_cols*B + "|"
        ##print("  blanks_f_t:(%s)   B:(%s)   Bb:(%s)"% (blanks_f_t,B, Bb))
        

        ##
        ##  Mehr mehr mehr. In no particular order:
        ##  A) 'Flatten' the Signal Header by replacing it with len(Measurey_Map[5] Sig.0, Sig,1, Sig,2 ...)
        ##     Treat lists of length one as special case: Don't Append number, but to pull out of list
        curr_row_values=[]
        for b in column_order:
            curr_row_values.append(M.Measurey_Map[b])
        for c in curr_row_values:
            print("####  type:(%s)  len:(%s)  %s" % ( type(c), len(c), c))

        ##h_f_t= '|{}' 
        h_f_t='|{:-^9}'
        fft  = num_cols * h_f_t
        
        ##print("  h_f_t:( %s )  fft:( %s ) " % (h_f_t, fft))
        ##print("  %s  " % (curr_row_values))
        formattedList = fft.format(*list(curr_row_values))
        print("%s" % (formattedList)) #---Line 1: column headers 

        print("#### curr_row_data: %s ###" % (curr_row_values))
        return
        # Justification (left, centered, right)
        #      |
        # '{1:_^8.5}'.format('xylophone', 'mimikatz')
        #   | | | |___truncate to five    
        #   | | |__Pad to 8 characters (At least 3 padding characters, 8-5)
        #   | |__Padding char
        #   | 
        #   |_argument
        #   #
        #exit(0)
        #### Step 2: Actual data
        curr_row_values=[]
        for b in column_order:
            curr_row_values.append( M.Measurey_Map[b])
        #h_f_t= '|{: ^%d.5}' % (max_col_width)
        #fft  = num_cols * h_f_t
        #print(" %s " % (fft))
        formattedList = fft.format(*curr_row_values)
        #print("%s" % (formattedList))


def main():
    Pretty_P = MeasureyM_text_Renderer()
    Mac_M,Lin_M=generate_wifinder_samples()
    
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