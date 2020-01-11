from Rtap_Char import  MeasureyM, MeasureyM_PrintShop

from sys import exit



def pretty_p(data):
    dash = '-' * 40

    for i in range(len(data)):
        if i == 0:
            print(dash)
            print('{:<10s}{:>4s}{:>12s}{:>12s}'.format(data[i][0],data[i][1],data[i][2],data[i][3]))
            print(dash)
        else:
            print('{:<10s}{:>4d}{:^12s}{:>12.1f}'.format(data[i][0],data[i][1],data[i][2],data[i][3]))










data=data = [['NAME', 'AGE', 'HANDEDNESS', 'SCORE (%)'],
        ['Martin', 38, 'L', 54.123],
        ['Marty', 33, 'L', 32.438],
        ['Martine', 25, 'R', 71.128],
        ['Martyn', 59, 'R', 50.472],
        ['Mart', 23, 'L', 2.438],
        ['Martyne', 15, 'R', 71.128],
        ['Marlyn', 101, 'R', 0.472],
        ['Marti', 2, 'L', 55.438],
        ['Mardi', 9, 'R', 81.128],
        ['Martyne', 49, 'R', 24.472],
        ['Marteen', 91, 'L', 1.128]]

pretty_p(data)

print("\n\n#######Approach numero 2 #######")
rows = [('apple', '$1.09', '80'), ('trufffffffle', '$58.01', '2')]

Pretty_P = MeasureyM_PrintShop()
def generate_samples():

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


def main():
    print("##Mac sample data::")
    Mac_M,Lin_M=generate_samples()
    for m in Mac_M:
        Pretty_P.print(m)
    print("")
    print("##Linux sample data::")
    for m in Lin_M:
        Pretty_P.print(m)
    print("")

    ###
    lens = []
    for col in zip(*rows):                         #ZIP: Return a list of tuples, where each tuple contains the i-th element. Exactly what we want!
        lens.append(max([len(v) for v in col]))
    print("lens: %s" % (lens))
    format = "  ".join(["{:<" + str(l) + "}" for l in lens])
    for row in rows:
        print(format.format(*row))


if __name__=='__main__':
  main()