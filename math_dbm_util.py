import math
import sys

from collections import namedtuple
from dbm_unit_conversion import dBm_to_milliwatt, milliwatt_to_dBm
########### milli/micro/nano/pico watt conversion table#
# | milliwatt (mW) | microwatt (uW) | nanowatt (nW)    |
# |  1.0           | 1,000 (1e+3)   |  1000000 (1e+6)  |
# |  0.001 (1e-3)  | 1.0            |  1000    (1e+3)  | 
# |  1e-6          | 1000           |  1.0             | 
########################################################


def dBm_as_percent(dBm_a, dBm_b):
    """ Express dBm_a as percentage of dBm_b"""
    milliwatt_a=dBm_to_milliwatt(dBm_a)
    milliwatt_b=dBm_to_milliwatt(dBm_b)
    return 100.0 * (milliwatt_a / milliwatt_b)


def mw_as_percent(milliwatt_a, milliwatt_b):
    """ Express dBm_a as percentage of dBm_b"""
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


def solve_for_x_factor(dBm_in, multiplier=20):
    microwatt_in=dBm_to_micro_watt(dBm_in)
    microwatt_in_20 = multiplier * microwatt_in
    dBm_out = micro_watt_to_dBm(microwatt_in_20)
    #print("#### Solving for x-factor(%s, %d)" % (dBm_in, multiplier))
    #print("    dBm_in: (%s) -> microwatts: (%s)" %(dBm_in, microwatt_in))
    #print("    microwatts_in: (%s) times %d =  %s" %(microwatt_in, multiplier, microwatt_in_20))
    #print("    %s microwatts  -> dBm %s" % ( microwatt_in_20, dBm_out))
    print("     %d times %s dBm = %s dBm " % (multiplier, dBm_in, dBm_out))
    x = dBm_out / dBm_in
    print("    'Cuz that would make our X-Factor %s" % (x))
    return x


def print_multiplication_table(in_dBm, multiplier):
    print("#### Generating multiplication table for: %3.2f, %d" % (in_dBm, multiplier))

    # Note the subtlety: the lval in this expression used to define a type.
    Record = namedtuple('Record',['base_dBm','base_mw','multiply_by', 'result_mw', 'result_dBm', 'scaled_mw_by', 'scaled_dBm_by']) 

    Results = [ Record(0,0,0,0,0,0,0)]
    y = in_dBm
    for i in range(1,10):  
        n = x_times_dBm(in_dBm, multiplier * i)
        #input("Que?")
        ## Tedious, but for testing store each field in record independently for print()
        if ( True ):
            base_dBm = in_dBm
            base_mw = dBm_to_milliwatt(in_dBm)
            multiply_by = i * multiplier
            result_mw = dBm_to_milliwatt(n)
            result_dBm = n
            scaled_mw_by  = result_mw  / base_mw
            scaled_dBm_by = result_dBm / base_dBm
            New_rec = Record(base_dBm,base_mw,multiply_by, result_mw, result_dBm, scaled_mw_by, scaled_dBm_by)
            Results.append ( New_rec  )
            ## XXX: Serious question. interpetation of 'scaled_mw_by' is obvious. But wtf does 'scaled_dBm_by' .. mean? Mayhe its just a unnecessary computation

        y = n
        #print("  %d)  %s " % (i, Results[-1]))
        #input(" Que ")
    
    input ("Trying to do some math on records[1] and [2]")
    rec1 = Results[1]
    rec2 = Results[2]
    r1=rec1.result_dBm
    r2=rec2.result_dBm
    print("Rec1 result_dBm: %3.3f" % (rec1.result_dBm) )
    print("Rec2 result_dBm: %3.3f" % (rec2.result_dBm) )
    print("Rec2 is %3f (linear) percent Rec1" % (dBm_as_percent(r2,r1)) )
    dbm_percent = ( r2 / r1 ) * 100.0
    print("Rec2 is %3f (..logarithmic?) percent Rec1" % ( dbm_percent ))
    
    input("Print table returning early.. Pretty soon we will want output an actual table")
    return
    ## JC TODO: replace format string, make this more useful
    ##f=' {:}\n'*len(twenty_x_ret_scale)
    ##s=f.format(*twenty_x_ret_scale)
    ##print("     %s" % (s))
    # JC start here
    print("--- in more english ---")
    print("   stepping up XXX  from %d dBm by linear multiplier of %d" % (in_dBm, multiplier))
    print(Results)
    #print("%3.7s" % (twenty_x_ret_scale))
    #return

def named_t_test():
    # Python code to demonstrate namedtuple() and 
    # Access by name, index and getattr() 
    
    
    # Declaring namedtuple() 
    # Note the subtlety: the lval in this expression used to define a type.
    Record = namedtuple('Record',['multiplier','result_dBm','dBm_delta']) 
    
    # Adding values 
    S = Student('Nandini','19','2541997') 
    
    # Access using index 
    print ("The Student age using index is : ",end ="") 
    print (S[1]) 
    
    # Access using name  
    print ("The Student name using keyname is : ",end ="") 
    print (S.name) 
    
def main():
    a=-55
    b=-7
    c=-75
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
