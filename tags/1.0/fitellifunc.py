import sys,os
from pyraf import iraf
import config as c

class FitElliFunc:
    """The class which will run ellipse task automatically"""
    def __init__(self, clus_id, line_s):
        self.clus_id   = clus_id
        self.line_s    = line_s
        self.fit_elli  = fit_elli(clus_id, line_s)
       

def fit_elli(clus_id, line_s):
    #try:
    size = c.size
    values = line_s.split()
    mask_file = 'ell_mask_' + str(imagefile)[:6] + '_'  + str(clus_id) + '.fits'
    image_file = 'image_' + str(imagefile)[:6] + '_'  + str(clus_id) + '.fits' 
    print image_file
    xcntr_o  = float(values[1]) #x center of the object
    ycntr_o  = float(values[2]) #y center of the object
    xcntr = (size/2.0) + 1.0 + xcntr_o - int(xcntr_o)
    ycntr = (size/2.0) + 1.0 + ycntr_o - int(ycntr_o)
    mag    = float(values[7]) #Magnitude
    radius = float(values[9]) #Half light radius
    mag_zero = 25.256 #magnitude zero point
    sky	 = float(values[10]) #sky
    if(float(values[11])>=0 and float(values[11])<=180.0): 
        pos_ang = float(values[11]) - 90.0 #position angle
    if(float(values[11])<0 and float(values[11])>=-180.0):
        pos_ang = 90.0 - abs(float(values[11]))  #position angle
    if(float(values[11])>180 and float(values[11])<=360.0):
        pos_ang = float(values[11]) - 360.0 + 90.0 #position angle
    if(float(values[11])>=-360 and float(values[11])<-180.0):
        pos_ang = float(values[11]) + 360.0 - 90.0 #position angle	
    axis_rat = 1.0 / float(values[12]) #axis ration b/a
    eg = 1 - axis_rat
    if(eg<=0.05):
        eg = 0.07
    major_axis = float(values[14])#major axis of the object
    iraf.imcopy(mask_file, 'image'+str(mask_file)[8:]+'.pl')
    run_elli(image_file, xcntr, ycntr, eg, pos_ang, major_axis)


def run_elli(input, xcntr, ycntr, eg, pa, sma):#,radd,background):
	
    iraf.stsdas(_doprint=0)
    iraf.tables(_doprint=0)
    iraf.stsdas.analysis(_doprint=0)
    iraf.stsdas.analysis.isophote(_doprint=0)
    image_exist = 1
    if(str(input)[:3] == 'ima'):
        output = 'elli_' + input[6:-4] + 'txt' 
    if(str(input)[:3] == 'out'):
        output = 'out_elli_' + str(input)[4:-7] + 'txt'
	#unlearn geompar	controlpar samplepar magpar ellipse
    iraf.geompar(x0=xcntr, y0=ycntr, ellip0=eg, pa0=pa, sma0=10, minsma=0.1, \
                 maxsma=sma*5.0, step=0.1,recente="yes")
    iraf.controlpar(conver=0.05, minit=10, maxit=50, hcenter="no", hellip="no", \
                    hpa="no", wander="", maxgerr=0.5, olthres=1,soft="no")
    iraf.samplepar(integrm="bi-linear", usclip=3,lsclip=3, nclip=0, fflag=0.5)
    iraf.magpar(mag0=0, refer=1, zerolev=0)
    iraf.ellipse("".join(input), output="test", interac="no",Stdout="ellip", \
                 Stderr="err")
    iraf.tprint("test.tab", prparam="no", prdata="yes", pwidth=80, plength=0, \
                showrow="no", orig_row="no", showhdr="no", showunits="no", \
                columns="SMA, INTENS, INT_ERR, MAG, MAG_LERR, MAG_UERR",\
                rows="-", \
                option="plain", align="yes", sp_col="", lgroup=0, Stdout=output)
    for myfile in ['ellip','err','test.tab']:
        if os.access(myfile,os.F_OK):
            os.remove(myfile)
