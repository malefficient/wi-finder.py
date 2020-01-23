import math
import sys
########### milli/micro/nano/pico watt conversion table#
# | milliwatt (mW) | microwatt (uW) | nanowatt (nW)    |
# |  1.0           | 1,000 (1e+3)   |  1000000 (1e+6)  |
# |  0.001 (1e-3)  | 1.0            |  1000    (1e+3)  | 
# |  1e-6          | 1000           |  1.0             | 
########################################################

def milliwatt_to_picowatt(_in):
    return 1e+9*_in
def microwatt_to_picowatt(_in):
    return 1e+6*_in
def nanowatt_to_picowatt(_in):
    return 1e+3*_in 
def picowatt_to_picowatt(_in):
    return 1e+0*_in 

def milliwatt_to_nanowatt(_in):
    return 1e+6*_in
def microwatt_to_nanowatt(_in):
    return 1e+3*_in
def nanowatt_to_nanowatt(_in):
    return 1e+0*_in 
def picowatt_to_nanowatt(_in):
    return 1e-3*_in 

def milliwatt_to_microwatt(_in):
    return 1e+3*_in
def microwatt_to_microwatt(_in):
    return 1e+0*_in
def nanowatt_to_microwatt(_in):
    return 1e-3*_in 
def picowatt_to_microwatt(_in):
    return 1e-6*_in 

def milliwatt_to_milliwatt(_in):
    return 1e+0*_in
def microwatt_to_milliwatt(_in):
    return 1e-3*_in
def nanowatt_to_milliwatt(_in):
    return 1e-6*_in 
def picowatt_to_milliwatt(_in):
    return 1e-9*_in 

#Note: If floating point precision becomes a problem, consider converting dBm -> picoWatts using fixed precision math; scale other calculations off results
def dBm_to_milliwatt(sig):
    x = sig / 10
    ret =  math.pow(10,x+3)
    #print("dBm_to_milliwatt(%d) = %s" % (sig, ret))
    return ret 

def milliwatt_to_dBm(mw_in):
    if (mw_in < 0.00000001) and (mw_in > -0.00000001):
        print("milliwatt_to_dBm special case: passed ~0.0. Returning 1")
        return 1
    ret =  math.log(float(mw_in), 10) * 10.0  - 30
    return ret

def dBm_as_percent(dBm_a, dBm_b):
    """ Express dBm_a as percentage of dBm_b"""
    milliwatt_a=dBm_to_milliwatt(dBm_a)
    milliwatt_b=dBm_to_milliwatt(dBm_b)
    return 100.0 * (milliwatt_a / milliwatt_b)

def x_times_dBm(dBm_in, _x):
    """ Multiply dBm_in by scalar value. Result returned in dBm""" #The entire reason this is a function is because we cant just multiply dBm and get actual results.
    milliwatt_in=dBm_to_milliwatt(dBm_in)
    milliwatt_in_times_x = _x * milliwatt_in
    dBm_out = milliwatt_to_dBm(milliwatt_in_times_x)
    print("#### multiply  (%2d dBm) times (x) %d = %3.2f" % (dBm_in, _x, dBm_out))
    return dBm_out

def dBm_to_milliwatt_test(dBm_l):
    """Converts a list of dBm values to milliwatts and back again"""
    milliwatt_l=[]
    synthesized_dBm_l=[]
    for r in dBm_l:
        milliwatt_l.append(dBm_to_milliwatt(r))

    f=' {:7.7f},'*len(dBm_l)
    s=f.format(*dBm_l)
    print("####          dBm in: [%s]" % (s))
    s= f.format(*milliwatt_l)

    print("#### milli-watt_out : [%s]" % (s))
    print("---------Flip side----------")
    s= f.format(*milliwatt_l)    
    print("#### milli-watt_in : [%s]" % (s))
    
    for m in milliwatt_l:
        synthesized_dBm_l.append(milliwatt_to_dBm(m))

    s=f.format(*synthesized_dBm_l)
    print("#### dBm out       : [%s]" % (s))

    return 0

### TODO: research storing results into named tuple
def print_multiplication_table(in_dBm, multiplier):
    print("#### Generating multiplication table for: %3.2f, %d" % (in_dBm, multiplier))

    twenty_x_ret_scale=[]
    delta_dbm_l = []

    y = in_dBm
    #while ( y < 0):  
    for i in range(1,10):   
        res = x_times_dBm(in_dBm, multiplier * i)
        twenty_x_ret_scale.append( (res))
        y = res
    
    ## JC TODO: replace format string, make this more useful
    ##f=' {:}\n'*len(twenty_x_ret_scale)
    ##s=f.format(*twenty_x_ret_scale)
    ##print("     %s" % (s))
    print("--- in more english ---")
    print("   stepping up from %d dBm by linear multiplier of %d" % (in_dBm, multiplier))
    
    #print("%3.7s" % (twenty_x_ret_scale))
    #return

def main():
    a=-55
    b=-7
    c=-75
    
    #
    #Parse args..
    if (1==1):
        print("sys.argc = %d" % (len(sys.argv)))
        if len (sys.argv) > 4:
            print("Error. To many arguments passed to %s" % (sys.argv[0]))
            sys.exit(0)
        if (len(sys.argv) > 3):
            c=int(sys.argv[3])
        if (len(sys.argv) > 2):
            b=int(sys.argv[2])
        if (len(sys.argv) > 1):
            a=int(sys.argv[1])
    
    #input("A:%d B:%d C:%d" % (a,b,c))
    #d = x_times_dBm(a, b)
    #dBm_to_milliwatt_test([a,b,c])
    print_multiplication_table(a, b)
    #e = s_for_x_factor(int(sys.argv[1]), 3)

    
    #print("%03d dBm is %07.8f micro_watts, or %7.8f nano-watts" % (curr, A, B))
   
if __name__ == '__main__':
    main()
