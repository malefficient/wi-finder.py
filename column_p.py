from Rtap_Char import  MeasureyM, RadiotapTable

from sys import exit




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
    
    

class column_MeasureyM_PrintShop:
    rtap_table_helper = RadiotapTable()
    
    def print(self, M):
        print("## %s ##" % (M.Measurey_Map))

def main():
    Pretty_P = column_MeasureyM_PrintShop()
    print("##Mac sample data::")
    Mac_M,Lin_M=generate_wifinder_samples()
    for m in Mac_M:
        Pretty_P.print(m)
    print("")
    print("##Linux sample data::")
    for m in Lin_M:
        Pretty_P.print(m)
    print("")

if __name__=='__main__':
    main()
    ascii_print_example_columns()