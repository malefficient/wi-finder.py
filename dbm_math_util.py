import sys, random
from dbm_unit_conversion import dBm_to_milliwatt, milliwatt_to_dBm
def dBm_as_percent(dBm_a, dBm_b):
    """ Express dBm_a as percentage of dBm_b"""
    milliwatt_a=dBm_to_milliwatt(dBm_a)
    milliwatt_b=dBm_to_milliwatt(dBm_b)
    return 100.0 * (milliwatt_a / milliwatt_b)

def dBm_divide_by_x(dBm_in, _x):
    return (dBm_multiply(dBm_in, (1/_x)))

def x_times_dBm(dBm_in, _x):
    """ Multiply dBm_in by scalar value. Result returned in dBm""" #The entire reason this is a function is because we cant just multiply dBm and get actual results.
    milliwatt_in=dBm_to_milliwatt(dBm_in)
    milliwatt_in_times_x = _x * milliwatt_in
    dBm_out = milliwatt_to_dBm(milliwatt_in_times_x)
    print("#### multiply  (%2d dBm) times (x) %d = %3.2f" % (dBm_in, _x, dBm_out))
    return dBm_out

    #print("    dBm_in: (%s) -> milliwatts: (%s)" %(dBm_in, milliwatt_in))
    #print("    miliwatts_in: (%s) times %d =  %s" %(milliwatt_in, multiplier, milliwatt_in_20))
    #print("    %s milliwatts  -> dBm %s" % ( milliwatt_in_20, dBm_out))
    #print("     %d times %s dBm = %s dBm " % (multiplier, dBm_in, dBm_out))
    #x = dBm_out / dBm_in
    #print("    'Old timey X-Factor %2.2f" % (x))
    
def s_for_x_factor(dBm_in, multiplier):
    x_dBm = x_times_dBm(dBm_in, multiplier)
    ret_dBm = x_dBm /dBm_in
    print("    'Cuz that would make our X-Factor %2.2f" % (ret_dBm))
    return (x_dBm / dBm_in)


def dbm_times_table(center=0,  in_range=5, stepsize=1):
    c_line=""
    #TODO: print out table headers first, (like column_print does), 
    for d in range( (center - in_range * stepsize), (center + in_range * stepsize), stepsize):
        for x in range( (stepsize * -4), (stepsize * 4), stepsize):
            c_line +=("%ddBm x %d(x) = " % (d, x))
        c_line+=("\n")
    print("%s" % (c_line))
    return
def test_dbm_math(a,b,c):
    dbm_times_table()
    d = x_times_dBm(int(sys.argv[1]),  int(sys.argv[2]))
    return
    e = s_for_x_factor(int(sys.argv[1]), 3)


def main():
    a,b,c =random.randint(-10,-3),random.randint(0,20),random.randint(0,20)
    

    if len (sys.argv) > 4:
        print("Error. To many arguments passed to %s" % (sys.argv[0]))
        sys.exit(0)
    if (len(sys.argv) > 3):
        c=int(sys.argv[3])
    if (len(sys.argv) > 2):
        b=int(sys.argv[2])
    if (len(sys.argv) > 1):
        a=int(sys.argv[1])
    test_dbm_math(a,b,c)
    return    
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