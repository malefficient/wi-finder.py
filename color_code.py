import math
import sys
class ColorClass():
    """Class that can convert between different color formats.
       Internally stored as a floats between 0.0 and 1.0 of 4 elements (alpha, blue, green, red)"""
    def __init__(self):
        self.val = [1.0, 1.0, 1.0, 1.0]

    def set_float(self, f):
        """Set color with a list of abgr floating point values between 0.0 and 1.0
        if  a list of len 3 is passed in, a default alpha of 1.0 will be used"""
        if (len(f) == 4): 
            #Alpha value included
            self.val = f
        if (len(f) == 3): 
            #Alpha value not passed in
            self.val = f
            self.val[0] = 1.0
            self.val[1] = f[0]
            self.val[2] = f[1]
            self.val[3] = f[2]
    def set_int(self, i):
        """Set color with a list of abgr floating point values between 0.0 and 1.0
        if  a list oi len 3 is passed in, a deiault alpha oi 1.0 will be used"""
        if (len(i) == 4): 
            #Alpha value included
            for j in range(0, 4):
                if (i[j] < 0):
                    self.val[j] = 0.0
                if (i[j] > 255):
                    self.val[j] = 1.0
                else:
                    self.val[j] = float(i[j]/255.0)

        if (len(i) == 3): 
            #Alpha value not passed in
            self.val[0] = 1.0
            for j in range(1, 4):
                self.val[j] = float(i[j-1]/255.0)

    def str_bgr(self):
       """ Return a tuple of strings to be used in KML plots. Always sets alpha to full"""
       return "ff%02x%02x%02x" % (self.val[1]*255, self.val[2]*255, self.val[3]*255)
    def str_abgr(self):
       """Alpha Blue Green Red representation, suitable for KML"""
       return "%02x%02x%02x%02x" % ( int(self.val[0]*255), int(self.val[1]*255), int(self.val[2]*255), int(self.val[3]*255))
    def str_rgb(self):
       """Red Green Blue representation, suitable for almost everything"""
       return "%02x%02x%02x" % ( int(self.val[3]*255), int(self.val[2]*255), int(self.val[1]*255))

    def __str__(self):
        """Default to RGB format"""

        return self.str_rgb();


def compute_signal_intensity_n(mag, m_max, m_min):
    """Returns intensity of signal mag scaled from 0.0->1.0, relative to m_max and m_min"""
    i = compute_signal_intensity(mag, m_max, m_min)
    i = i / 3.0
    if (i > 1.0):
        print("compute_signal_intensity: Warning input value (%d) < max (%d). Return ceiling of 1.0. Discard %3.2f" % (mag, m_max, i - 1.0))
        i=1.0
    if (i < 0.0):
        print("compute_signal_intensity: Warning input value (%d) < min (%d). Return floor of 0.0. Discarding %3.2f" % (mag, m_min, math.fabs(i)))
        i=0.0
    return i
def compute_signal_intensity(mag, m_max, m_min):
    #positivify these annoying negative numbers
    m_min = math.fabs(m_min)
    m_max = math.fabs(m_max)
    my_spread = math.fabs(m_min - m_max)
    db_above_min = m_min - math.fabs(mag)
    if (db_above_min > my_spread):
        print("compute_signal_color: Warning input value (%d) > max (%d)" %(mag, m_max))

    numerator = 3.0 * db_above_min
    denominator = my_spread
    if (denominator != 0):
        intensity = numerator/denominator
    else:
        intensity = 1 #Theres only one signal reading.
    print("###Return intensity from 0.0->3.0")
    return intensity
def compute_signal_color(mag, m_max, m_min):
    """Takes in mag, m_max, m_min  in dB. returns a color scaled approriately"""
    intensity = compute_signal_intensity(mag, m_max, m_min)
    blue_percent = green_percent = red_percent = 0.0
    print("#### comput_signal_color::\n  #### Intensity(%d,%d,%d) = %3.2f" % (mag, m_max, m_min, intensity))
    print("    #### Intensity varies from 0.0-3.0. ")
    if (intensity > 2.0):
        blue_percent = intensity - 2.0;
        intensity -= blue_percent;
    if (intensity > 1.0):
        green_percent = intensity - 1.0;
        intensity -= green_percent;
    red_percent =  intensity;
    C = ColorClass()
    C.set_float ([1.0, blue_percent, green_percent, red_percent])
    return C

def main():
    print("#### unit testing of color_code.py")
    max=-55
    min=-75
    curr=-55
    print("sys.argc = %d" % (len(sys.argv)))
    if len (sys.argv) > 4:
        print("Error. To many arguments passed to %s" % (sys.argv[0]))
        sys.exit(0)
    if (len(sys.argv) > 3):
        min=int(sys.argv[3])
    if (len(sys.argv) > 2):
        max=int(sys.argv[2])
    if (len(sys.argv) > 1):
        curr=int(sys.argv[1])
        
    c = compute_signal_color(curr, max, min)
    print(" Color: %s" % (c))
    i = compute_signal_intensity(curr, max, min)
    print(" Intensity: %3.2f" % (i))
    i = compute_signal_intensity_n(curr, max, min)
    print ("type returned: %s" % (type(i)))
    print("'Normalized' intensity: %3.2f" % (i))
    return
if __name__ == '__main__':
    main()