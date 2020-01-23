import math

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
    print("dBm_to_microwatt(%d) = %s" % (sig, ret))
    return ret 

def milliwatt_to_dBm(mw_in):
    if (mw_in < 0.00000001) and (mw_in > -0.00000001):
        print("microwatt_to_dBm special case: passed ~0.0. Returning 1")
        return 1
    ret =  math.log(float(mw_in), 10) * 10.0  - 30
    return ret






