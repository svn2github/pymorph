import numpy as n
import os
import pyfits
from pyraf import iraf
import convolve as conv
#import scipy
#import scipy.signal
class clumpness:
	"""clumpness parameter"""
	def __init__(self,z,ini_xcntr,ini_ycntr,pa,eg,extraction_radius,sigma,background,flag_image):
		self.z			= z
		self.ini_xcntr		= ini_xcntr
		self.ini_ycntr		= ini_ycntr
		self.extraction_radius	= extraction_radius
		self.pa			= pa
		self.eg			= eg
		self.background		= background
		self.flag_image		= flag_image
		self.sigma		= sigma#the size of the boxcar
		self.image_clumpness	= CLUMPNESS(self.z, self.ini_xcntr, self.ini_ycntr, self.pa, self.eg, self.background, self.extraction_radius, self.sigma, self.flag_image)

def CLUMPNESS(z, ini_xcntr, ini_ycntr, pa, eg, background, extraction_radius, sigma, flag_image):
	zextract = z[int(ini_ycntr - extraction_radius):int(ini_ycntr + \
                   extraction_radius), int(ini_xcntr - extraction_radius): \
                   int(ini_xcntr + extraction_radius)]
	NXPTS = zextract.shape[0]
	NYPTS = zextract.shape[1]
	#print NXPTS, NYPTS,ini_xcntr,ini_ycntr
	co = n.cos(pa * n.pi / 180.0)
	si = n.sin(pa * n.pi / 180.0)	
	x = n.reshape(n.arange(NXPTS * NYPTS), (NXPTS, NYPTS)) / NYPTS
	x = x.astype(n.float32)
	y = n.reshape(n.arange(NXPTS * NYPTS), (NXPTS, NYPTS)) % NYPTS
	y = y.astype(n.float32)
	tx = (x - NXPTS / 2 - 1) * co + (y - NYPTS / 2 - 1) * si
	ty = (NXPTS / 2 - 1 - x) * si + (y - NYPTS / 2 - 1) * co
	R = n.sqrt(tx**2.0 + ty**2.0 / (1.0 - eg)**2.0)
#	hdu = pyfits.PrimaryHDU(zextract.astype(n.float32))
#	hdu.writeto('sImage.fits')
#	input = 'sImage.fits'
#	iraf.images(_doprint=0)
#	iraf.images.imfilter(_doprint=0)		
#	iraf.boxcar("".join(input), output = "SImage.fits", xwindow = sigma, ywindow = sigma, boundar = "nearest", constant = 0.0)
#	I_sigma = conv.boxcar(zextract, (int(sigma), int(sigma)),mode='nearest')#the convolve image with the boxcar
#	f=pyfits.open("SImage.fits")
#	I_sigma = f[0].data
#	f.close()
#	for myfile in ['SImage.fits','sImage.fits']:
#		if os.access(myfile,os.F_OK):
#			os.remove(myfile)
#	cov_filter = scipy.signal.boxcar((int(sigma), int(sigma)))
#	cov_filter = cov_filter / cov_filter.sum()
#	I_sigma = scipy.signal.convolve(zextract, cov_filter, mode='same')
	I_sigma=conv.boxcar(zextract, (int(sigma),int(sigma)),mode='nearest')
	res = zextract - I_sigma #the residual image

	if(flag_image):
	#the below will find the image portion which is an anulus of inner radius .3*eta(.2) and outer radius 1.5*eta(.2)
#		res[where(R<=extraction_radius*(0.25/1.5))]=0 #making the residual value equal to zero inside the extraction_radius*(.25/1.5)
		res[n.where(R <= extraction_radius * (1 / 20.0))] = 0
		res[n.where(R >= extraction_radius)] = 0
		res_inside_anulus_sum = res[n.where(res > 0)].sum() #the sum of residue inside the anulus
#                print res_inside_anulus_sum, 3.14*extraction_radius*extraction_radius
		z_inside_R_sum = zextract[n.where(R <= \
                                 extraction_radius)].sum() / (3.14 * \
                                 extraction_radius * extraction_radius * \
                                 n.sqrt(1 - eg**2.0))
		area = 3.14 * (extraction_radius * extraction_radius * \
                       n.sqrt(1 - eg**2.0)) - 3.14 * (extraction_radius * \
                       extraction_radius * (1 / 6.0) * (1 / 6.0) * \
                       n.sqrt(1 - eg**2.0))
		S = res_inside_anulus_sum / area#-(0.25*extraction_radius/1.5)*(0.25*extraction_radius/1.5)*sqrt(1-eg**2.0)))
		e1sq = zextract[n.where(res > 0)].sum() + \
                       I_sigma[n.where(res > 0)].sum() + 4 * \
                       zextract[n.where(res > 0)].size * background

	#no_res_inside_anulus=res[where(res>0)].nelements()
	else:
		res[n.where(R >= extraction_radius)] = 0
		res_inside_anulus_sum = res[n.where(res > 0)].sum()
		area = 3.14 * extraction_radius**2.0
		S = res_inside_anulus_sum / area
		z_inside_R_sum = 0#just to return the value in the end
		e1sq = zextract[n.where(res > 0)].sum() + \
                       I_sigma[n.where(res > 0)].sum() + \
                       2 * zextract[n.where(res > 0)].size * background
	e2sq = res_inside_anulus_sum**2.0
	e3sq = zextract[n.where(R <= extraction_radius)].sum() + \
               2 * zextract[n.where(R <= extraction_radius)].size * background
 	e4sq = (zextract[n.where(R <= extraction_radius)].sum())**2.0
	if(e2sq!=0):
		error = e1sq / e2sq
	else:
		print "Could not find error"
		error = 0.0
	return S, error, z_inside_R_sum, e3sq, e4sq	

#f=pyfits.open('n5585_lR.fits')
#z=f[0].data
#header = f[0].header
#if (header.has_key('sky')):
#    sky = header['sky']
#f.close()
#xcntr=192.03
#ycntr=157.42
#pa=0.0
#eg=0.0
#z=z-sky
#background=1390.377
#nxpts=z.shape[0]
#nypts=z.shape[1]
#extraction_radius=100
#sigma=20.0
#clumpness(z,xcntr,ycntr,pa,eg,extraction_radius,sigma,background,1)
