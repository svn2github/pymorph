# import relevant python module
import os
import sys
import pyfits
from os.path import exists
from numpy import log10
import numpy as n
import copy
import numpy.ma as ma

# import pymorph-specific modules 
import config as c
from runsexfunc import *
from readlog import ReadLog
from cosmocal import cal
try:
    from utilities import WriteDbDetail
except:
    print 'No database'


# declare the class

class ConfigIter:
    """The class making configuration file for GALFIT. The configuration file 
       consists of bulge and disk component of the object and only Sersic 
       component for the neighbours, if any. The sky is always fixed and has
       the value of SExtractor. The disk/boxy parameter is also fixed to zero.
       The initial value for Sersic index 'n' is 4.The configuration file has 
       the name G_string(galid).in. The output image has the name 
       O_string(galid).fits"""
    def __init__(self, cutimage, whtimage, xcntr, ycntr, NXPTS, NYPTS, line_s, psffile, z):
        self.cutimage = cutimage
        self.line_s  = line_s
	self.whtimage = whtimage
        self.xcntr = xcntr
        self.ycntr = ycntr
        self.NXPTS = NXPTS
        self.NYPTS = NYPTS 
        self.psffile = psffile

        # check whether the variable is defined, if not, define it 
        try: 
            c.center_constrain = c.center_constrain
        except:
            c.center_constrain = 2.0
        # run the fitting iteration
        self.confiter    = confiter(cutimage, whtimage, xcntr, ycntr, NXPTS, NYPTS, line_s, psffile, z)
        
#end of class definitions

# function definitions 



def confiter(cutimage, whtimage, xcntr, ycntr,
             NXPTS, NYPTS, line_s, psffile, z):
    # Run SExtractor 
    RunSex(c.datadir+cutimage, c.datadir+whtimage,
           'TEMP.SEX.cat', 9999, 9999, 0)
    # define improtant variables in the namespace
    imagefile = c.imagefile
    sex_cata = c.sex_cata
    threshold = c.threshold
    thresh_area = c.thresh_area
    mask_reg = c.mask_reg
    c.sersic_loc  = 1
    try:
        ComP = c.components 
    except:
        ComP = ['bulge', 'disk']
    if len(ComP) == 0:
        ComP = ['bulge', 'disk']
    values = line_s.split()
    # create filenames
    outfile   = 'O_' + str(cutimage)[:-5] + '.fits' # galfit output
    mask_file = 'M_' + str(cutimage)[:-5] + '.fits' # mask file
    config_file = 'G_' + str(cutimage)[:-5] + '.in' #GALFIT configuration file
    constrain_file = str(cutimage)[:-5] + '.con' #galfit constraint file


    xcntr_o  = xcntr  #x center of the object
    ycntr_o  = ycntr  #y center of the object
    mag    = float(values[7]) #Magnitude
    radius = float(values[9]) #Half light radius
    mag_zero = c.mag_zero #magnitude zero point
    sky	 = float(values[10]) #sky 
    pos_ang = float(values[11]) - 90.0 #position angle
    axis_rat = 1.0/float(values[12]) #axis ration b/a
    area_o = float(values[13])   # object's area
    major_axis = float(values[14])  #major axis of the object

    # define initial fitting parameters for single sersic fit
    ParamDict = {}
    ErrDict = {}
    ParamDict[0] = {}
    ErrDict[0] = {}
    # Add components
    AdComp = 1
    if 'bulge' in ComP:
        ParamDict[0][AdComp] = {}
        #Bulge Parameters
        ParamDict[0][AdComp][1] = 'sersic'
        ParamDict[0][AdComp][2] = [xcntr_o, ycntr_o]
        ParamDict[0][AdComp][3] = mag 
        ParamDict[0][AdComp][4] = radius 
        ParamDict[0][AdComp][5] = 4.0
        ParamDict[0][AdComp][6] = axis_rat
        ParamDict[0][AdComp][7] = pos_ang
        ParamDict[0][AdComp][8] = 0
        ParamDict[0][AdComp][9] = 0
        ParamDict[0][AdComp][11] = 'Main'
        AdComp += 1
    if 'disk' in ComP:
        #Disk parameters
        ParamDict[0][AdComp] = {}
        ParamDict[0][AdComp][1] = 'expdisk'
        ParamDict[0][AdComp][2] = [xcntr_o, ycntr_o]
        ParamDict[0][AdComp][3] = 9999#mag 
        ParamDict[0][AdComp][4] = 9999#radius
        ParamDict[0][AdComp][5] = 9999#axis_rat
        ParamDict[0][AdComp][6] = 9999#pos_ang
        ParamDict[0][AdComp][7] = 9999
        ParamDict[0][AdComp][8] = 9999
        ParamDict[0][AdComp][11] = 'Main'
        AdComp += 1
    if 'bar' in ComP:
        ParamDict[0][AdComp] = {}
        #Bulge Parameters
        ParamDict[0][AdComp][1] = 'bar'
        ParamDict[0][AdComp][2] = [xcntr_o, ycntr_o]
        ParamDict[0][AdComp][3] = mag + 2.5 * log10(2.0)
        ParamDict[0][AdComp][4] = radius
        ParamDict[0][AdComp][5] = 0.5
        ParamDict[0][AdComp][6] = 0.3
        ParamDict[0][AdComp][7] = pos_ang
        ParamDict[0][AdComp][8] = 0
        ParamDict[0][AdComp][9] = 0
        ParamDict[0][AdComp][11] = 'Main'
        AdComp += 1
    if 'point' in ComP:
        ParamDict[0][AdComp] = {}
        #Point Parameters
        ParamDict[0][AdComp][1] = 'psf'
        ParamDict[0][AdComp][2] = [xcntr_o, ycntr_o]
        ParamDict[0][AdComp][3] = mag + 2.5 * log10(6.0)
        ParamDict[0][AdComp][4] = 0
        ParamDict[0][AdComp][11] = 'Main'
        AdComp += 1

    isneighbour = 0
    f_constrain = open(constrain_file, 'ab')
    for line_j in open('TEMP.SEX.cat','r'):
        try:
            values = line_j.split()
            xcntr_n  = float(values[1]) #x center of the neighbour
            ycntr_n  = float(values[2]) #y center of the neighbour
            mag    = float(values[7]) #Magnitude
            radius = float(values[9]) #Half light radius
            sky      = float(values[10]) #sky
            pos_ang = float(values[11]) - 90.0 #position angle
            axis_rat = 1.0/float(values[12]) #axis ration b/a
            area_n = float(values[13]) # neighbour area
            maj_axis = float(values[14])#major axis of neighbour
            NotFitNeigh = 0
            if abs(xcntr_n - xcntr_o) > NXPTS / 2.0 + c.avoidme or \
               abs(ycntr_n - ycntr_o) > NYPTS / 2.0 + c.avoidme or \
               abs(xcntr_n - xcntr_o) < 5.0 and abs(ycntr_n - ycntr_o) < 5.0:
                NotFitNeigh = 1
            if(abs(xcntr_n - xcntr_o) <= (major_axis + maj_axis) * \
               threshold and \
               abs(ycntr_n - ycntr_o) <= (major_axis  + maj_axis) * \
               threshold and area_n >= thresh_area * area_o and \
               xcntr_n != xcntr_o and ycntr_n != ycntr_o and NotFitNeigh == 0):
                if((xcntr_o - xcntr_n) < 0):
                    xn = xcntr + abs(xcntr_n - xcntr_o)
                if((ycntr_o - ycntr_n) < 0):
                    yn = ycntr + abs(ycntr_n - ycntr_o)
                if((xcntr_o - xcntr_n) > 0):
                    xn = xcntr - (xcntr_o - xcntr_n)
                if((ycntr_o - ycntr_n) > 0):
                    yn = ycntr - (ycntr_o - ycntr_n)
                ParamDict[0][AdComp] = {}
                ParamDict[0][AdComp][1] = 'sersic'
                ParamDict[0][AdComp][2] = [xn, yn]
                ParamDict[0][AdComp][3] = mag
                ParamDict[0][AdComp][4] = radius
                ParamDict[0][AdComp][5] = 4.0
                ParamDict[0][AdComp][6] = axis_rat
                ParamDict[0][AdComp][7] = pos_ang
                ParamDict[0][AdComp][8] = 0
                ParamDict[0][AdComp][9] = 0
                ParamDict[0][AdComp][11] = 'Other'

                isneighbour = 1
                AdComp += 1
        except:
            pass
    f_constrain.close()
    #Sky component
    ParamDict[0][AdComp] = {}
    ParamDict[0][AdComp][1] = 'sky'
    ParamDict[0][AdComp][2] = c.SexSky
    ParamDict[0][AdComp][3] = 0
    ParamDict[0][AdComp][4] = 0
    ParamDict[0][AdComp][5] = 0
    ParamDict[0][AdComp][11] = 'Other'
    #Write Sersic function
    ErrDict[0][1] = {}
    ErrDict[0][1][1] = [9999, 9999]
    ErrDict[0][1][2] = 9999
    ErrDict[0][1][3] = 9999
    ErrDict[0][1][4] = 9999
    ErrDict[0][2] = {}
    ErrDict[0][2][1] = [9999, 9999]
    ErrDict[0][2][2] = 9999
    ErrDict[0][2][3] = 9999

    c.SkyNo = AdComp
    c.Chi2DOFArr = []
    c.FitArr = []
    c.RadArr = []
    c.CntrDevArr = []
    c.ErrArr = []
    c.ParamDictBook = copy.deepcopy(ParamDict)
    bad_fit = 0
    #Write configuration file. RunNo is the number of iteration
    for RunNo in range(3):
        if exists('fit.log'):
            os.system('rm fit.log')

        print "RunNo ", RunNo
        f_constrain = open(constrain_file, 'w')
        f_constrain.close()
        f=open(config_file,'w')
        f.write('# IMAGE PARAMETERS\n')
        f.writelines(['A) ', c.datadir+str(cutimage), '	# Input data image',\
                      ' (FITS file)\n'])
        f.writelines(['B) ', str(outfile), '		# Name for',\
                      ' the output image\n'])
        f.writelines(['C) ', c.datadir + str(whtimage), '		# Noise image name', \
                      ' (made from data if blank or "none")\n'])
        f.writelines(['D) ', c.datadir+str(psffile), '			# Input PSF', \
                      ' image for convolution (FITS file)\n'])
        f.writelines(['E) 1			# PSF oversampling factor '\
                      'relative to data\n'])
        f.writelines(['F) ', str(mask_file), '		# Bad pixel',
                      ' mask(FITS image or ASCII coord list)\n'])
        f.writelines(['G) ', str(constrain_file), '       # File with'\
                      ' parameter constraints (ASCII file)\n'])
        f.writelines(['H) 1 ', str(NXPTS), ' 1 ', str(NYPTS), '		#',\
                      ' Image region to fit (xmin xmax ymin ymax)\n'])
#        f.writelines(['I) ', str(NXPTS), ' ', str(NYPTS),	'	#',\
#                      ' Size of convolution box (x y)\n'])
        f.writelines(['I) ', str(120), ' ', str(120),      '       #',\
                      ' Size of convolution box (x y)\n'])
        f.writelines(['J) ', str(mag_zero), '		# Magnitude',\
                      ' photometric zeropoint\n'])
        f.writelines(['O) regular			# Display type',\
                      ' (regular, curses, both)\n'])
        f.writelines(['P) 0			# Create output image only?',\
                      ' (1=yes; 0=optimize)\n'])
        f.writelines(['S) 0			# Modify/create',\
                     ' objects interactively?\n\n\n'])
        f.close()
        FitDict = DecideFitting(ParamDict, RunNo, bad_fit)
        for i in range(len(ParamDict[RunNo])):
            if ParamDict[RunNo][i + 1][1] == 'sersic':
                SersicFunc(config_file, ParamDict, FitDict, i+1, RunNo)
                if ParamDict[RunNo][i + 1][11] == 'Main':
                    if RunNo > 0 and not bad_fit: # later runs 
                        SersicMainConstrain(constrain_file, i + 1, 2.0 , 0)#ParamDict[c.sersic_loc][1][4]+1)
                    else:
                        SersicMainConstrain(constrain_file, i + 1, c.center_constrain, 0)
                else:
                    SersicConstrain(constrain_file, i + 1)
 
            if ParamDict[RunNo][i + 1][1] == 'expdisk':
                if RunNo == 0:
                    pass
                else:
                    ExpFunc(config_file, ParamDict, FitDict, i + 1, RunNo)
                    if RunNo > 0 and not bad_fit: # later runs 
                        ExpdiskConstrain(constrain_file, i + 1, 2.0)
                    else:
                        ExpdiskConstrain(constrain_file, i + 1, c.center_constrain)
            if ParamDict[RunNo][i + 1][1] == 'bar':
                if RunNo == 0:
                    pass
                else:
                    BarFunc(config_file, ParamDict, FitDict, i+1, RunNo)
                    BarConstrain(constrain_file, i + 1)

            if ParamDict[RunNo][i + 1][1] == 'psf':
                if RunNo == 0:
                    pass
                else:
                    PsfFunc(config_file, ParamDict, FitDict, i+1, RunNo)
                    PsfConstrain(constrain_file, i + 1)

            if  ParamDict[RunNo][i + 1][1] == 'sky':
                if RunNo > 0 and not bad_fit: 
                    SkyConstrain(constrain_file, i + 1, ParamDict[c.sersic_loc][i+1][2])
                SkyFunc(config_file, ParamDict, FitDict, i+1, RunNo) 
        
        cmd = str(c.GALFIT_PATH) + ' ' + config_file
        os.system(cmd)
        # ReadLog(ParamDict, 2) => this function reads fig.log
        # depends on whether, for example, the expdisk function
        # is the only one function for fitting. It can happends,
        # for example, the first fitting where we can find the best
        # initial values for the rest of it. ReadLog(ParamDict, 1)
        # reads the fit.log in the order, ie. sersic,
        # expdisk, other sersic etc
        ParamDict, ErrDict, Chi2DOF = ReadLog(ParamDict, ErrDict, 1, RunNo)
        c.ParamDictBook[RunNo+1] = copy.deepcopy(ParamDict[RunNo+1])
        try:
            c.ErrArr.append(FractionalError(ParamDict, ErrDict, RunNo + 1))
        except:
            c.ErrArr.append(9999.0)
        c.Chi2DOFArr.append(Chi2DOF)
        
        if RunNo < 2:
            bad_fit = DecideHowToMove2(ParamDict, RunNo + 1, z) 
            try:
                WriteDbDetail(cutimage.split('.')[0], c.ParamDictBook[RunNo+1], ErrDict[RunNo + 1], c.SexSky, c.ParamDictBook[RunNo+1][c.SkyNo][2], RunNo, c.Flag, c.Chi2DOFArr[RunNo], model_type = str(RunNo))
            except:
                print 'No database'

        if RunNo == 0:
            fit_log = 'fit_ser.log'
        elif RunNo == 1:
            fit_log = 'fit1.log'
        else:
            fit_log = 'fit2.log'
        
        f_fit = open(fit_log,'a')
        if exists('fit.log'):
            for line in open('fit.log','r'):
                f_fit.writelines([str(line)])
        f_fit.close()

        
        for mv_file_nm in [outfile, config_file, constrain_file]:
            os.system('cp %s %s_%d.%s' %(mv_file_nm, mv_file_nm.split('.')[0],
                                          RunNo, mv_file_nm.split('.')[1]))

def SersicMainConstrain(constrain_file, cO, cen_con, re_con):
    f_constrain = open(constrain_file, 'ab')
    f_constrain.write(str(cO) + '      n      ' + str(c.LN) + \
                      ' to ' + str(c.UN) +  '\n')
    f_constrain.write(str(cO) + '      x      ' + \
                      str(-cen_con) + '     ' + \
                      str(cen_con) + '\n')
    f_constrain.write(str(cO) + '      y      ' + \
                      str(-cen_con) + '     ' + \
                      str(cen_con) + '\n')
    f_constrain.write(str(cO) + '     mag     ' + str(c.UMag) + \
                      ' to ' + str(c.LMag - 2.0) + '\n')
    if re_con == 0:
        f_constrain.write(str(cO) + '      re     ' + str(0.2) +\
                          ' to ' + str(c.URe) + '\n')
    else:
        f_constrain.write(str(cO) + '      re     ' + str(0.5) +\
                          ' to ' + str(re_con) + '\n')
        
    f_constrain.write(str(cO) + '      q       0.05 to 0.95\n')
    f_constrain.write(str(cO) + '      pa       -360.0 to 360.0\n')
    f_constrain.close()

def ExpdiskConstrain(constrain_file, cO, cen_con):
    f_constrain = open(constrain_file, 'ab')
    f_constrain.write(str(cO) + '       x       ' + \
                      str(-cen_con) + '     ' + \
                      str(cen_con) + '\n')
    f_constrain.write(str(cO) + '       y       ' + \
                      str(-cen_con) + '     ' + \
                      str(cen_con) + '\n')
    f_constrain.write(str(cO) + '     mag     ' + str(c.UMag) + \
                      ' to ' + str(c.LMag) + '\n')
    f_constrain.write(str(cO) + '      rs     ' + str(c.LRd) + \
                      ' to ' + str(c.URd) + '\n')
    f_constrain.write(str(cO) + '      q       0.0 to 1.0\n')
    f_constrain.write(str(cO) + '      pa       -360.0 to 360.0\n')
    f_constrain.close()

def BarConstrain(constrain_file, cO):
    f_constrain = open(constrain_file, 'ab')
    f_constrain.write(str(cO) + '      n      ' + str(0.01) + \
                      ' to ' + str(2.2) +  '\n')
    f_constrain.write(str(cO) + '      x      ' + \
                      str(-(c.center_constrain - 1.0)) + '     ' + \
                      str(c.center_constrain - 1.0) + '\n')
    f_constrain.write(str(cO) + '      y      ' + \
                      str(-(c.center_constrain - 1.0)) + '     ' + \
                      str(c.center_constrain + 1.0) + '\n')
    f_constrain.write(str(cO) + '     mag     ' + str(c.UMag) + \
                      ' to ' + str(c.LMag) + '\n')
    f_constrain.write(str(cO) + '      re     ' + str(c.LRe) +\
                      ' to ' + str(c.URe) + '\n')
    f_constrain.write(str(cO) + '      q       0.0 to 0.6\n')
    f_constrain.write(str(cO) + '      pa       -360.0 to 360.0\n')
    f_constrain.close()

def PsfConstrain(constrain_file, cO):
    f_constrain = open(constrain_file, 'ab')
    f_constrain.write(str(cO) + '       x       ' + \
                      str(-c.center_constrain) + '     ' + \
                      str(c.center_constrain) + '\n')
    f_constrain.write(str(cO) + '       y       ' + \
                      str(-c.center_constrain) + '     ' + \
                      str(c.center_constrain) + '\n')
    f_constrain.write(str(cO) + '     mag     ' + str(c.UMag) + \
                      ' to ' + str(c.LMag) + '\n')
    f_constrain.close()

def SersicConstrain(constrain_file, cO):
    f_constrain = open(constrain_file, 'ab')
    f_constrain.write(str(cO) + '      n      0.02 to 20.0  \n')
    f_constrain.write(str(cO) + '     mag    -100.0 to 100.0\n')
    f_constrain.write(str(cO) + '      re      0.0 to 500.0\n')
    f_constrain.write(str(cO) + '      q       0.0 to 1.0\n')
    f_constrain.write(str(cO) + '      pa    -360.0 to 360.0\n')
    f_constrain.close()
    
def SkyConstrain(constrain_file, cO, SkyValToCon):
    f_constrain = open(constrain_file, 'ab')
    f_constrain.write(str(cO) + '      sky      ' +
                      str(SkyValToCon * 1.0-0.008) + ' to   ' +
                      str(SkyValToCon * 1.0+0.008) + '  \n')
    f_constrain.close()


def SersicFunc(conffile, ParamDict, FitDict, No, RunNo):
    f=open(conffile, 'ab')
    f.write('# Sersic function\n\n')
    f.writelines([' 0) sersic \n'])
    f.writelines([' 1) ', str(ParamDict[RunNo][No][2][0]), ' ', \
                          str(ParamDict[RunNo][No][2][1]), ' ', \
                          str(FitDict[No][1][0]),   ' ', \
                          str(FitDict[No][1][1]),   '\n'])
    f.writelines([' 3) ', str(ParamDict[RunNo][No][3]), ' ', \
                          str(FitDict[No][2]),  '\n'])
    f.writelines([' 4) ', str(ParamDict[RunNo][No][4]), ' ', \
                          str(FitDict[No][3]),  '\n'])
    f.writelines([' 5) ', str(ParamDict[RunNo][No][5]), ' ',\
                          str(FitDict[No][4]),  '\n'])
    f.writelines([' 8) ', str(ParamDict[RunNo][No][6]), ' ', \
                          str(FitDict[No][5]),  '\n'])
    f.writelines([' 9) ', str(ParamDict[RunNo][No][7]), ' ', \
                          str(FitDict[No][6]),  '\n'])
    if c.bdbox or c.bbox:
        f.writelines(['10) 0.0 1		\n'])
    else:
        f.writelines(['10) 0.0 0            \n'])
    f.writelines([' Z) 0 			\n\n\n'])
    f.close()
def ExpFunc(conffile, ParamDict, FitDict, No, RunNo):
    f=open(conffile, 'ab')
    f.writelines(['# Exponential function\n\n'])
    f.writelines([' 0) expdisk \n'])
    f.writelines([' 1) ', str(ParamDict[RunNo][No][2][0]), ' ', \
                          str(ParamDict[RunNo][No][2][1]),' ', \
                          str(FitDict[No][1][0]), ' ', \
                          str(FitDict[No][1][1]), '\n'])
    f.writelines([' 3) ', str(ParamDict[RunNo][No][3]),  ' ', \
                          str(FitDict[No][2]),    '\n'])
    f.writelines([' 4) ', str(ParamDict[RunNo][No][4]),  ' ', \
                          str(FitDict[No][3]),    '\n'])
    f.writelines([' 8) ', str(ParamDict[RunNo][No][5]),  ' ', \
                          str(FitDict[No][4]),    '\n'])
    f.writelines([' 9) ', str(ParamDict[RunNo][No][6]),  ' ', \
                          str(FitDict[No][5]),    '\n'])
    if c.bdbox or c.dbox:
        f.writelines(['10) 0.0 1   \n']) 
    else:
        f.writelines(['10) 0.0 0   \n'])
    f.writelines([' Z) 0           \n\n\n'])
    f.close()
def BarFunc(conffile, ParamDict, FitDict, No, RunNo):
    f=open(conffile, 'ab')
    f.write('# Sersic function\n\n')
    f.writelines([' 0) sersic \n'])
    f.writelines([' 1) ', str(ParamDict[RunNo][No][2][0]), ' ', \
                          str(ParamDict[RunNo][No][2][1]), ' ', \
                          str(FitDict[No][1][0]),   ' ', \
                          str(FitDict[No][1][1]),   '\n'])
    f.writelines([' 3) ', str(ParamDict[RunNo][No][3]), ' ', \
                          str(FitDict[No][2]),  '\n'])
    f.writelines([' 4) ', str(ParamDict[RunNo][No][4]), ' ', \
                          str(FitDict[No][3]),  '\n'])
    f.writelines([' 5) ', str(ParamDict[RunNo][No][5]), ' ',\
                          str(FitDict[No][4]),  '\n'])
    f.writelines([' 8) ', str(ParamDict[RunNo][No][6]), ' ', \
                          str(FitDict[No][5]),  '\n'])
    f.writelines([' 9) ', str(ParamDict[RunNo][No][7]), ' ', \
                          str(FitDict[No][6]),  '\n'])
    if c.bdbox or c.bbox:
        f.writelines(['10) 0.0 1		\n'])
    else:
        f.writelines(['10) 0.0 0            \n'])
    f.writelines([' Z) 0 			\n\n\n'])
    f.close()
def PsfFunc(conffile, ParamDict, FitDict, No, RunNo):
    f=open(conffile, 'ab')
    f.writelines([' 0) psf\n'])
    f.writelines([' 1) ', str(ParamDict[RunNo][No][2][0]), ' ', \
                          str(ParamDict[RunNo][No][2][1]), ' ', \
                          str(FitDict[No][1][0]),   ' ', \
                          str(FitDict[No][1][1]),   '\n'])
    f.writelines([' 3) ', str(ParamDict[RunNo][No][3]), ' ', \
                          str(FitDict[No][2]),  '\n'])
    f.writelines([' Z) 0                    \n\n\n'])
    f.close()
def SkyFunc(conffile, ParamDict, FitDict, No, RunNo):
    f=open(conffile, 'ab')
    f.writelines([' 0) sky\n'])
    f.writelines([' 1) ', str(ParamDict[RunNo][No][2]), \
                '      ', str(FitDict[No][1]), '\n'])
    f.writelines([' 2) 0.000      0       \n',\
                  ' 3) 0.000      0       \n',\
                  ' Z) 0                  \n\n\n'])
    f.writelines(['# Neighbour sersic function\n\n'])
    f.close()

    
def DecideFitting(ParamDict, RunNo, bad_fit):
    FitDict = {}
    #print ParamDict 
    if RunNo == 0: # perform a single-sersic fit
        for j in range(len(ParamDict[RunNo])):
            i = j + 1
            FitDict[i] = {} 
            if ParamDict[RunNo][i][1] == 'sersic' and ParamDict[RunNo][i][11] == 'Main':
                FitDict[i][1] = [1, 1]
                FitDict[i][2] = 1 
                FitDict[i][3] = 1
                FitDict[i][4] = 1
                FitDict[i][5] = 1       
                FitDict[i][6] = 1    

            #In the first run the disk will not be fitted.
            #This is to keep the order of ParamDict and FitDict 
            if ParamDict[RunNo][i][1] == 'expdisk' and ParamDict[RunNo][i][11] == 'Main':
                FitDict[i][1] = [1, 1]
                FitDict[i][2] = 1 
                FitDict[i][3] = 1 
                FitDict[i][4] = 1       
                FitDict[i][5] = 1
                
            if ParamDict[RunNo][i][1] == 'sky':
                FitDict[i][1] = 1
                FitDict[i][2] = 1 
                FitDict[i][3] = 0 
            if ParamDict[RunNo][i][1] == 'sersic' and ParamDict[RunNo][i][11] == 'Other':
                FitDict[i][1] = [1, 1]
                FitDict[i][2] = 1 
                FitDict[i][3] = 1 
                FitDict[i][4] = 1
                FitDict[i][5] = 1       
                FitDict[i][6] = 1    

    if RunNo > 0: # Perform a either a sersic+exp fit or a dev+exp fit
        # whichever was not selected by the user originally first
        # NOTE: we prefer to fix the values of the bulge/disk
        # centers at the value found from the single-sersic fit.
        # If we found the single sersic fit to be unacceptable
        # then we will alter the FitDict later on.
        for j in range(len(ParamDict[RunNo])):
            i = j + 1
            FitDict[i] = {}  
            if ParamDict[RunNo][i][1] == 'sersic' and ParamDict[RunNo][i][11] == 'Main':
                FitDict[i][1] = [1,1] 
                #FitDict[i][1] = [bad_fit,bad_fit] 
                FitDict[i][2] = 1 
                FitDict[i][3] = 1 
                if RunNo == 1:
                    FitDict[i][4] = int(c.devauc)
                else:
                    FitDict[i][4] = int(not c.devauc)
                FitDict[i][5] = 1       
                FitDict[i][6] = 1    
            if ParamDict[RunNo][i][1] == 'expdisk' and ParamDict[RunNo][i][11] == 'Main':
                FitDict[i][1] = [1,1]
                #FitDict[i][1] = [bad_fit, bad_fit]
                FitDict[i][2] = 1 
                FitDict[i][3] = 1 
                FitDict[i][4] = 1       
                FitDict[i][5] = 1  
            if ParamDict[RunNo][i][1] == 'sky':
                FitDict[i][1] = 1
                FitDict[i][2] = 1 
                FitDict[i][3] = 0 
            if ParamDict[RunNo][i][1] == 'sersic' and ParamDict[RunNo][i][11] == 'Other':
                #should this bee all 1s or 0s?
                FitDict[i][1] = [1, 1]
                FitDict[i][2] = 1 
                FitDict[i][3] = 1 
                FitDict[i][4] = 1
                FitDict[i][5] = 1       
                FitDict[i][6] = 1    
    
    return FitDict


def FractionalError(ParamDict, ErrDict, RunNo):
    Xberr = ErrDict[RunNo][1][1][0] / ParamDict[RunNo][1][2][0] 
    Yberr = ErrDict[RunNo][1][1][1] / ParamDict[RunNo][1][2][1] 
    Fb = 10**((c.mag_zero -  ParamDict[RunNo][1][3]) / 2.5)
    Fbe = abs(10**((c.mag_zero -  ParamDict[RunNo][1][3] + ErrDict[RunNo][1][2]) / 2.5) - 10**((c.mag_zero -  ParamDict[RunNo][1][3] - ErrDict[RunNo][1][2]) / 2.5))
    ffbe = Fbe / Fb
    reerr = ErrDict[RunNo][1][3] / ParamDict[RunNo][1][4]
    nerr = ErrDict[RunNo][1][4] / ParamDict[RunNo][1][5]
    Xderr = ErrDict[RunNo][2][1][0] / ParamDict[RunNo][2][2][0] 
    Yderr = ErrDict[RunNo][2][1][1] / ParamDict[RunNo][2][2][1] 
    Fd = 10**((c.mag_zero -  ParamDict[RunNo][2][3]) / 2.5)
    Fde = n.abs(10**((c.mag_zero -  ParamDict[RunNo][2][3] + ErrDict[RunNo][2][2]) / 2.5) - 10**((c.mag_zero -  ParamDict[RunNo][2][3] - ErrDict[RunNo][2][2]) / 2.5))
    ffde = Fde / Fd
    rderr = ErrDict[RunNo][2][3] / ParamDict[RunNo][2][4]
    #        print Xberr, Yberr, Fb, Fbe, reerr, nerr
    #        print Xderr, Yderr, Fd, Fde, rderr
    toterr = n.sqrt(ffbe**2.0 + reerr**2.0 + nerr**2.0 + ffde**2.0 + rderr**2.0)
    if n.median([ffbe, reerr, nerr, ffde, rderr]) < 0.1:
        toterr = 0.01
    else:
        toterr = n.median([ffbe, reerr, nerr, ffde, rderr])
    print n.median([ffbe, reerr, nerr, ffde, rderr])
    return toterr


def DecideHowToMove2(ParamDict, RunNo,z):
    sersic_loc = c.sersic_loc # index location of the single sersic fit in the ParamDict used for decision-making in the dev+exp and Ser+exp fits
    bad_fit = 0
    HitLimitCheck = 0
    KpCArc = cal(z, c.H0, c.WM, c.WV, c.pixelscale)[3]

    if abs(c.ParamDictBook[sersic_loc][1][3] - (c.LMag - 1.0)) < 0.05 or abs(c.ParamDictBook[sersic_loc][1][3] - c.UMag) < 0.05 or c.ParamDictBook[sersic_loc][1][4] < 0.21 or c.ParamDictBook[sersic_loc][2][4] < 0.21 or  c.ParamDictBook[sersic_loc][1][5] > 8.0 or c.ParamDictBook[sersic_loc][1][4] *KpCArc > 40.0:
        print "bad sersic fit"
        bad_fit = 1
        bt_fit = .5
        ParamDict[RunNo][1][2][0] = copy.deepcopy(c.ParamDictBook[0][1][2][0])
        ParamDict[RunNo][1][2][1] = copy.deepcopy(c.ParamDictBook[0][1][2][1])
        ParamDict[RunNo][1][3] = copy.deepcopy(c.ParamDictBook[0][1][3]) - 2.5 * n.log10(bt_fit)
        ParamDict[RunNo][1][4] = copy.deepcopy(c.ParamDictBook[0][1][4])
        ParamDict[RunNo][1][5] = 4.0
        ParamDict[RunNo][1][6] = copy.deepcopy(c.ParamDictBook[0][1][6])
        ParamDict[RunNo][1][7] = copy.deepcopy(c.ParamDictBook[0][1][7])
        ParamDict[RunNo][2][2][0] = copy.deepcopy(c.ParamDictBook[0][1][2][0])
        ParamDict[RunNo][2][2][1] = copy.deepcopy(c.ParamDictBook[0][1][2][1])
        ParamDict[RunNo][2][3] = copy.deepcopy(c.ParamDictBook[0][1][3])-2.5 * n.log10(1.0 - bt_fit)
        ParamDict[RunNo][2][4] = copy.deepcopy(c.ParamDictBook[0][1][4])
        ParamDict[RunNo][2][5] = copy.deepcopy(c.ParamDictBook[0][1][6])
        ParamDict[RunNo][2][6] = copy.deepcopy(c.ParamDictBook[0][1][7])

        try:
            ParamDict[RunNo][c.SkyNo][2] = copy.deepcopy(c.ParamDictBook[0][-1][2])
        except:
            pass
        
    elif c.ParamDictBook[sersic_loc][1][5] <= 2.0: # disk-like galaxy -> so set disk parameters to bulge 
        print 'disky'
        bt_fit = .25
        ParamDict[RunNo][1][2][0] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][2][0])
        ParamDict[RunNo][1][2][1] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][2][1])
        ParamDict[RunNo][1][3] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][3]) - 2.5 * n.log10(bt_fit)
        ParamDict[RunNo][1][4] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][4])/4.0 #shrink bulge radius
        ParamDict[RunNo][1][5] = 4.0
        ParamDict[RunNo][1][6] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][6])
        ParamDict[RunNo][1][7] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][7])
        ParamDict[RunNo][2][2][0] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][2][0])
        ParamDict[RunNo][2][2][1] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][2][1])
        ParamDict[RunNo][2][3] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][3])-2.5 * n.log10(1.0 - bt_fit)
        ParamDict[RunNo][2][4] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][4])
        ParamDict[RunNo][2][5] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][6])
        ParamDict[RunNo][2][6] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][7])

        try:
            ParamDict[RunNo][c.SkyNo][2] = copy.deepcopy(c.ParamDictBook[sersic_loc][-1][2])
        except:
            pass

    elif 3.0 <= c.ParamDictBook[sersic_loc][1][5] and c.ParamDictBook[sersic_loc][1][5] <= 6.0: # bulge-like galaxy -> so set bulge parameters to bulge 
        print 'bulge_like'
        bt_fit = .75
        ParamDict[RunNo][1][2][0] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][2][0])
        ParamDict[RunNo][1][2][1] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][2][1])
        ParamDict[RunNo][1][3] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][3]) - 2.5 * n.log10(bt_fit)
        ParamDict[RunNo][1][4] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][4]) #shrink bulge radius
        ParamDict[RunNo][1][5] = 4.0
        ParamDict[RunNo][1][6] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][6])
        ParamDict[RunNo][1][7] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][7])
        ParamDict[RunNo][2][2][0] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][2][0])
        ParamDict[RunNo][2][2][1] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][2][1])
        ParamDict[RunNo][2][3] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][3])-2.5 * n.log10(1.0 - bt_fit)
        ParamDict[RunNo][2][4] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][4])*2.0
        ParamDict[RunNo][2][5] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][6])
        ParamDict[RunNo][2][6] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][7])

        try:
            ParamDict[RunNo][c.SkyNo][2] = copy.deepcopy(c.ParamDictBook[sersic_loc][-1][2])
        except:
            pass

    else: # some intermediate combination of bulge and disk
        print 'mix'
        bt_fit = .5
        ParamDict[RunNo][1][2][0] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][2][0])
        ParamDict[RunNo][1][2][1] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][2][1])
        ParamDict[RunNo][1][3] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][3]) - 2.5 * n.log10(bt_fit)
        ParamDict[RunNo][1][4] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][4])*.5
        ParamDict[RunNo][1][5] = 4.0
        ParamDict[RunNo][1][6] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][6])
        ParamDict[RunNo][1][7] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][7])
        ParamDict[RunNo][2][2][0] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][2][0])
        ParamDict[RunNo][2][2][1] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][2][1])
        ParamDict[RunNo][2][3] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][3])-2.5 * n.log10(1.0 - bt_fit)
        ParamDict[RunNo][2][4] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][4])*2
        ParamDict[RunNo][2][5] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][6])
        ParamDict[RunNo][2][6] = copy.deepcopy(c.ParamDictBook[sersic_loc][1][7])

        try:
            ParamDict[RunNo][c.SkyNo][2] = copy.deepcopy(c.ParamDictBook[sersic_loc][-1][2])
        except:
            pass

    return bad_fit
