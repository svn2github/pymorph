import os
import sys
import pyfits
import config as c
from os.path import exists


class ConfigFunc:
    """The class making configuration file for GALFIT. The configuration file 
       consists of bulge and disk component of the object and only Sersic 
       component for the neighbours, if any. The sky is always fixed and has
       the value of SExtractor. The disk/boxy parameter is also fixed to zero.
       The initial value for Sersic index 'n' is 4.The configuration file has 
       the name G_string(galid).in. The output image has the name 
       O_string(galid).fits"""
    def __init__(self, cutimage, whtimage, size, line_s, psffile):
        self.cutimage = cutimage
        self.line_s  = line_s
	self.whtimage = whtimage
        self.size = size
        self.conf    = conf(cutimage, whtimage, size, line_s, psffile)
		

def conf(cutimage, whtimage, size, line_s, psffile):
    imagefile = c.imagefile
    sex_cata = c.sex_cata
    threshold = c.threshold
    thresh_area = c.thresh_area
    mask_reg = c.mask_reg
    values = line_s.split()
    outfile   = 'O_' + str(cutimage)[:-5] + '.fits'
    mask_file = 'M_' + str(cutimage)[:-5] + '.fits'
    config_file = 'G_' + str(cutimage)[:-5] + '.in' #Name of the GALFIT configuration file
    contrain_file = str(cutimage)[:-5] + '.con'
    f=open(config_file,'w')
    xcntr_o  = float(values[1]) #x center of the object
    ycntr_o  = float(values[2]) #y center of the object
    xcntr = size/2.0 + 1.0 + xcntr_o - int(xcntr_o)
    ycntr = size/2.0 + 1.0 + ycntr_o - int(ycntr_o)
    mag    = float(values[7]) #Magnitude
    radius = float(values[9]) #Half light radius
    mag_zero = c.mag_zero #magnitude zero point
    sky	 = float(values[10]) #sky 
    pos_ang = float(values[11]) - 90.0 #position angle
    axis_rat = 1.0/float(values[12]) #axis ration b/a
    major_axis = float(values[14])	#major axis of the object
    #Write configuration file
    f.write('# IMAGE PARAMETERS\n')
    f.writelines(['A) ', str(cutimage), '	# Input data image',\
                  ' (FITS file)\n'])
    f.writelines(['B) ', str(outfile), '		# Name for',\
                  ' the output image\n'])
    f.writelines(['C) ', str(whtimage), '		# Noise image name', \
                  ' (made from data if blank or "none")\n'])
    f.writelines(['D) ', str(psffile), '			# Input PSF', \
                  ' image for convolution (FITS file)\n'])
    f.writelines(['E) 1			# PSF oversampling factor relative',
                  ' to data\n'])
    f.writelines(['F) ', str(mask_file), '		# Bad pixel',
                  ' mask(FITS image or ASCII coord list)\n'])
    f.writelines(['G) ', str(contrain_file), '       # File with parameter',\
                  ' constraints (ASCII file)\n'])
    f.writelines(['H) 1 ', str(size), ' 1 ', str(size), '		#',\
                  ' Image region to fit (xmin xmax ymin ymax)\n'])
    f.writelines(['I) ', str(size), ' ', str(size),	'		#',\
                  ' Size of convolution box (x y)\n'])
    f.writelines(['J) ', str(mag_zero), '		# Magnitude',\
                  ' photometric zeropoint\n'])
    f.writelines(['O) both			# Display type',\
                  ' (regular, curses, both)\n'])
    f.writelines(['P) 0			# Create output image only?',\
                  ' (1=yes; 0=optimize)\n'])
    f.writelines(['S) 0			# Modify/create',\
                 ' objects interactively?\n\n\n'])
    f.write('# Sersic function\n\n')
    f.writelines([' 0) sersic		# Object type\n'])
    f.writelines([' 1) ', str(xcntr), ' ', str(ycntr),' 1 1	#',\
                  ' position x, y [pixel]\n'])
    f.writelines([' 3) ', str(mag), ' 1		# total magnitude\n'])
    f.writelines([' 4) ', str(radius), ' 1		# R_e [Pixels]\n'])
    f.writelines([' 5) 4.0 1		#Sersic exponent',\
                  ' (deVauc=4, expdisk=1)\n'])
    f.writelines([' 8) ', str(axis_rat), ' 1	# axis ratio (b/a)\n'])
    f.writelines([' 9) ', str(pos_ang), ' 1		# position angle (PA)',\
                  '[Degrees: Up=0, Left=90]\n'])
    f.writelines(['10) 0.0 0		# diskiness (< 0) or boxiness (> 0)\n'])
    f.writelines([' Z) 0 			# output image',\
                  ' (see above)\n\n\n']) 
    f.writelines(['# Exponential function\n\n'])
    f.writelines([' 0) expdisk 		# Object type\n'])
    f.writelines([' 1) ', str(xcntr), ' ', str(ycntr),' 1 1  #',\
                  ' position x, y [pixel]\n'])
    f.writelines([' 3) ', str(mag), ' 1     	# total magnitude\n'])
    f.writelines([' 4) ', str(radius), ' 1 		# R_e [Pixels]\n'])
    f.writelines([' 8) ', str(axis_rat), ' 1     # axis ratio (b/a)\n'])
    f.writelines([' 9) ', str(pos_ang), ' 1         	# position angle(PA) \
                 [Degrees: Up=0, Left=90]\n'])
    f.writelines(['10) 0.0 0         	# diskiness (< 0) or boxiness (> 0)\n']) 
    f.writelines([' Z) 0             	# output image (see above)\n\n\n'])
    f.writelines(['# sky\n\n']) 
    f.writelines([' 0) sky\n'])
    f.writelines([' 1) ', str(sky), ' 0	# sky background [ADU counts\n'])
    f.writelines([' 2) 0.000      0       # dsky/dx (sky gradient in x)\n',\
                  ' 3) 0.000      0       # dsky/dy (sky gradient in y)\n',\
                  ' Z) 0                  # output image\n\n\n'])
    f.writelines(['# Neighbour sersic function\n\n'])
    for line_j in open(sex_cata,'r'):
        try:
            values = line_j.split()
            xcntr_n  = float(values[1]) #x center of the neighbour
            ycntr_n  = float(values[2]) #y center of the neighbour
            mag    = float(values[7]) #Magnitude
            radius = float(values[9]) #Half light radius
            sky      = float(values[10]) #sky
            pos_ang = float(values[11]) - 90.0 #position angle
            axis_rat = 1.0/float(values[12]) #axis ration b/a
            area = float(values[13])
            maj_axis = float(values[14])#major axis of neighbour
            if(abs(xcntr_n - xcntr_o) < major_axis * threshold and \
               abs(ycntr_n - ycntr_o) < major_axis * threshold and \
               xcntr_n != xcntr_o and ycntr_n != ycntr_o):
                if((xcntr_o - xcntr_n) < 0):
                    xn = xcntr + abs(xcntr_n - xcntr_o)
                if((ycntr_o - ycntr_n) < 0):
                    yn = ycntr + abs(ycntr_n - ycntr_o)
                if((xcntr_o - xcntr_n) > 0):
                    xn = xcntr - (xcntr_o - xcntr_n)
                if((ycntr_o - ycntr_n) > 0):
                    yn = ycntr - (ycntr_o - ycntr_n)
                f.writelines([' 0) sersic               # Object type\n'])
                f.writelines([' 1) ', str(xn), ' ', str(yn), \
                             ' 1 1  # position x, y [pixel]\n'])
                f.writelines([' 3) ', str(mag), ' 1     	#',\
                              ' total magnitude\n'])
                f.writelines([' 4) ', str(radius), ' 1  		',\
                               '# R_e [Pixels]\n'])
                f.writelines([' 5) 4.0 1        	#Sersic exponent', \
                              ' (deVauc=4, expdisk=1)\n'])
                f.writelines([' 8) ', str(axis_rat), ' 1        # axis',\
                              ' ratio (b/a)\n'])
                f.writelines([' 9) ', str(pos_ang), ' 1 	       ',\
                              ' # position angle (PA)  [Degrees: Up=0,'\
                                ' Left=90]\n'])
                f.writelines(['10) 0.0 0         	# diskiness',\
                              ' (< 0) or boxiness (> 0)\n'])
                f.writelines([' Z) 0 	           	# output',\
                              ' image (see above)\n\n\n'])
            elif(abs(xcntr_n - xcntr_o) < size/2.0 - 1.0 and \
                 abs(ycntr_n- ycntr_o) < size/2.0 - 1.0 and \
                 area >= thresh_area):
                if(abs(xcntr_n - xcntr_o) >= major_axis * threshold or \
                   abs(ycntr_n - ycntr_o) >= major_axis):
                    if((xcntr_o - xcntr_n) < 0):
                        xn = xcntr + abs(xcntr_n - xcntr_o)
                    if((ycntr_o - ycntr_n) < 0):
                        yn = ycntr + abs(ycntr_n - ycntr_o)
                    if((xcntr_o - xcntr_n) > 0):
                        xn = xcntr - (xcntr_o - xcntr_n)
                    if((ycntr_o - ycntr_n) > 0):
                        yn = ycntr - (ycntr_o - ycntr_n)
                    f.writelines([' 0) sersic               # Object type\n'])
                    f.writelines([' 1) ', str(xn), ' ', str(yn), \
                                 ' 1 1  # position x, y [pixel]\n'])
                    f.writelines([' 3) ', str(mag), ' 1     	#',\
                                  ' total magnitude\n'])
                    f.writelines([' 4) ', str(radius), ' 1  	',\
                                  '	# R_e [Pixels]\n'])
                    f.writelines([' 5) 4.0 1        	#Sersic',\
                                  ' exponent (deVauc=4, expdisk=1)\n'])
                    f.writelines([' 8) ', str(axis_rat), ' 1     ',\
                                  ' # axis ratio (b/a)\n'])
                    f.writelines([' 9) ', str(pos_ang), ' 1 	       ',\
                                  ' # position angle (PA)  [Degrees:',\
                                  ' Up=0, Left=90]\n'])
                    f.writelines(['10) 0.0 0         	# diskiness (< 0)',\
                                  ' or boxiness (> 0)\n'])
                    f.writelines([' Z) 0 	           	',\
                                  ' # output image (see above)\n\n\n'])
        except:
            pass
    f.close()
#    f_fit = open('fit2.log','a')
#    if exists('fit.log'):
#        os.system('rm fit.log')
#Here the user should tell the location of the GALFIT excutable
#    os.system('/Vstr/vstr/vvinuv/galfit/modified/galfit "' + config_file + '"')
#    if exists('fit.log'):
#        for line in open('fit.log','r'):
#            f_fit.writelines([str(line)])
#    f_fit.close()
