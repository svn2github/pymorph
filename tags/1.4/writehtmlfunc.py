from os.path import exists
import csv
import fileinput
from cosmocal import *
import config as c

class WriteHtmlFunc:
    """The class which will write html and csv output"""
    def __init__(self, cutimage, distance, alpha1, alpha2, alpha3, delta1, delta2, delta3, z, C, C_err, A, A_err, S, S_err, G, M):
        self.cutimage     = cutimage
        self.distance     = distance
        self.alpha1       = alpha1
        self.alpha2       = alpha2
        self.alpha3       = alpha3
        self.delta1       = delta1
        self.delta2       = delta2
        self.delta3       = delta3
        self.z            = z
        self.C            = C
        self.C_err        = C_err
        self.A            = A
        self.A_err        = A_err
        self.S            = S
        self.S_err        = S_err
        self.G            = G
        self.M            = M
        self.write_params = write_params(cutimage, distance, alpha1, alpha2, alpha3, delta1, delta2, delta3, z, C, C_err, A, A_err, S, S_err, G, M)

def write_params(cutimage, distance, alpha1, alpha2, alpha3, delta1, delta2, delta3, z, C, C_err, A, A_err, S, S_err, G, M):

    outfile = open('R_' + str(cutimage)[:-4] + 'html','w')
    outfile.writelines(['<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 \
                         Transitional//EN">\n'])
    outfile.writelines(['<HTML> \n <HEAD> \n <meta http-equiv\
                         ="Content-Type" content="text/html; charset=utf-8">\
                         <title>Pipeline Result</title> \n </HEAD><BODY> \n'])
    outfile.writelines(['<TABLE BORDER="0" align="center" cellspacing=1',\
                        ' width="100%"> \n'])
    alpha_j = (alpha1 + (alpha2 + alpha3 / 60.0) / 60.0) * 15.0
    delta_j = delta1 - (delta2 + delta3 / 60.0) / 60.0
    if(c.repeat == False):
        for line_i in fileinput.input("index.html",inplace =1):
            line_i = line_i.strip()
            if not '</BODY></HTML>' in line_i:
                print line_i    
        indexfile = open('index.html', 'a+')
        indexfile.writelines(['<a href="R_',\
                              str(cutimage)[:-5],'.html',\
                                  '"> ', str(cutimage)[:-5],\
                                  ' </a> <br>\n'])
        indexfile.writelines(['</BODY></HTML>\n'])
        indexfile.close()
    object = 1
    object_err = 1
    if exists('fit.log'):
        for line in open('fit.log','r'): 
            values = line.split() 
            try: 
                if(str(values[0]) == 'Input'):
                    outfile.writelines(['<TR align="center" bgcolor="#CCFFFF">\
                                        <TH> Image </TH> <TD align="left">\
                                        &nbsp;&nbsp;&nbsp;', str(cutimage), \
                                        '&nbsp;&nbsp;&nbsp&nbsp;&nbsp;&nbsp;', \
                                        '<A HREF="http://nedwww.ipac.caltech.edu/cgi-bin/nph-objsearch?search_type=Near+Position+Search&amp;in_csys=Equatorial&amp;in_equinox=J2000.0&amp;lon=', str(alpha_j)[:6], 'd&amp;lat=', str(delta_j)[:6], 'd&amp;radius=5.0&amp;out_csys=Equatorial&amp;out_equinox=J2000.0&amp;obj_sort=Distance+to+search+center&amp;of=pre_text&amp;zv_breaker=30000.0&amp;list_limit=5&amp;img_stamp=YES&amp;z_constraint=Unconstrained&amp;ot_include=ANY&amp;nmp_op=ANY">NED</A>', \
                                        '</TD> <TH> RA </TH> <TD>', \
                                        str(alpha1), ' ', str(alpha2),\
                                        ' ',str(alpha3), '</TD> </TR> \n' ])

                if(str(values[0]) == 'Init.'):
                    outfile.writelines(['<TR align="center" bgcolor="#99CCFF">\
                                        <TH> Init. par. file </TH> \
                                        <TD align="left">&nbsp;&nbsp;&nbsp;', \
                                        str(values[4]), '</TD> <TH> Dec </TH> \
                                        <TD>', str(delta1), ' ', str(delta2),\
                                        ' ',str(delta3), '</TD> </TR> \n' ])		
                if(str(values[0]) == 'Restart'):
                    outfile.writelines(['<TR align="center" bgcolor="#CCFFFF">\
                                        <TH> Restart file </TH> \
                                        <TD align="left">&nbsp;&nbsp;&nbsp;', \
                                        str(values[3]), '</TD> <TH> z </TH>\
                                        <TD>', str(z), '</TD></TR>\n' ])
                if(str(values[0]) == 'Chi^2/nu'):
                    chi2nu = float(values[2])
                    outfile.writelines(['<TR align="center" bgcolor=',\
                                        '"#99CCFF"> <TH> &chi; <sup> 2',\
                                        ' </sup> / &nu; </TH> \
                                        <TD align="left">&nbsp;&nbsp;&nbsp;', \
                                        str(values[2]),'</TD> <TH> Separation\
                                        between <br> psf and image </TH>\
                                        <TD>', str(round(distance, 3))[:5],\
                                        ' arc sec</TD></TR>\n' ])
                if(str(values[0]) == 'sersic' and object == 1):
                    mag_b = float(values[4])
                    re = float(values[5])
                    n = float(values[6])
                    object += 1
                if(str(values[0]) == 'expdisk'):
                    mag_d = float(values[4])
                    rd = float(values[5])
                if(str(values[0])[:1] == '('):
                    if(str(a) == 'sersic' and object_err == 1):
                        mag_b_err = float(values[2])
                        re_err  = float(values[3])
                        n_err = float(values[4])
                        object_err += 1
                    if(str(a) == 'expdisk'):
                        mag_d_err = float(values[2])
                        rd_err = float(values[3])
                a=values[0]				
            except:
                pass
        if(z == 9999):
            re_kpc = 9999
            re_err_kpc = 9999
            rd_kpc = 9999
            rd_err_kpc = 9999
        else:
            phy_parms = cal(z, c.H0, c.WM, c.WV, c.pixelscale)
            re_kpc = phy_parms[3] * re
            re_err_kpc = phy_parms[3] * re_err
            rd_kpc = phy_parms[3] * rd
            rd_err_kpc = phy_parms[3] * rd_err
        run = 1
        if exists('result.csv'):
            for line_res in csv.reader(open('result.csv').readlines()[1:]):    
                if(str(line_res[0]) == cutimage[:-5]):
                    run += 1
        f_res = open("result.csv", "ab")
        writer = csv.writer(f_res)
        galid = str(cutimage)[:-5]
        BD = 10**(-0.4 * ( mag_b - mag_d))
        BT = 1.0 / (1.0 + 1.0 / BD)
        writer.writerow([galid, alpha_j, delta_j, z, mag_b, mag_b_err, re, re_err, re_kpc, re_err_kpc, n, n_err, mag_d, mag_d_err, rd, rd_err, rd_kpc, rd_err_kpc, BD, BT, chi2nu, run, C, C_err, A, A_err, S, S_err, G, M, distance])
        f_res.close()
    outfile.writelines(['</TABLE> \n'])
    #outfile.writelines(['<CENTER><IMG SRC="plot_', str(files)[6:-4], 'png"></CENTER>'])
    outfile.writelines(['<TABLE BORDER="0" align="center" cellspacing=1',\
                        ' width="100%"> \n \
                        <TR align="center"> <TD ROWSPAN=2><IMG SRC="P_', \
                        str(cutimage)[:-4], 'png" alt="plot"></TD> <TD  \
                        bgcolor="#CCFFFF"> \
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\
                        &nbsp;&nbsp;</TD> </TR> \n',\
                        ' <TR align="center" bgcolor="#99CCFF"> <TD> \
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\
                        &nbsp;&nbsp;</TD> </TR> \n </TABLE> \n'])
    outfile.writelines(['<TABLE BORDER="0" align="center" cellspacing=1',\
                        ' width="100%"> \n'])	
    outfile.writelines(['<TR align="center" bgcolor="#CCFFFF"> <TH> Component \
                         <TH> xc <TH> yc <TH> mag <TH> radius <br> (pixels)\
                         <TH> radius <br> (kpc) <TH> n <TH> ellipticity\
                         <TH> pa <TH> box/disk </TH> </TR> \n'])
    object = 1
    object_err = 1
    if exists('fit.log'):
        for line in open('fit.log','r'): 
            values = line.split() 
            try: 
                if(str(values[0]) == 'sersic'):
                    if object > 1:
                        outfile.writelines(['<TR align="center" bgcolor=',\
                                            '"#99CCFF"> <TD>', str(values[0]), \
                                            ' </TD> <TD> ', \
                                            str(values[2])[1:-1],' </TD> <TD> '\
                                            , str(values[3])[:-1],' </TD> <TD> \
                                            ', str(values[4]), ' </TD> <TD> ',\
                                            str(values[5]), ' </TD> <TD> ', \
                                            ' ', ' </TD> <TD> ',\
                                            str(values[6]), ' </TD> <TD> ', \
                                            str(values[7]), ' </TD> <TD> ', \
                                            str(values[8]), ' </TD> <TD> ', \
                                            str(values[9]), ' </TD> </TR> \n'])
                    if object == 1:
                        outfile.writelines(['<TR align="center" bgcolor=',\
                                            '"#99CCFF"> <TD>', str(values[0]), \
                                            ' </TD> <TD> ', \
                                            str(values[2])[1:-1],' </TD> <TD> '\
                                            , str(values[3])[:-1],' </TD> <TD> \
                                            ', str(values[4]), ' </TD> <TD> ',\
                                            str(values[5]), ' </TD> <TD> ', \
                                            str(round(re_kpc, 3))[:5], '</TD> <TD> ',\
                                            str(values[6]), ' </TD> <TD> ', \
                                            str(values[7]), ' </TD> <TD> ', \
                                            str(values[8]), ' </TD> <TD> ', \
                                            str(values[9]), ' </TD> </TR> \n'])
                        object += 1

                if(str(values[0]) == 'expdisk'):
                    outfile.writelines(['<TR align="center" bgcolor="#99CCFF">\
                                         <TD>', str(values[0]), \
                                        ' </TD> <TD> ', str(values[2])[1:-1],\
                                        ' </TD> <TD> ', str(values[3])[:-1], \
                                        ' </TD> <TD> ', str(values[4]), \
                                        ' </TD> <TD> ', str(values[5]), \
                                        ' </TD> <TD> ', str(round(rd_kpc, 3))[:5],  \
                                        ' </TD> <TD> ', ' ',  \
                                        ' </TD> <TD> ', str(values[6]), \
                                        ' </TD> <TD> ', str(values[7]), \
                                        ' </TD> <TD> ', str(values[8]), \
                                        ' </TD>  </TR> \n'])
                if(str(values[0])[:1] == '('):
                    if(str(a) == 'sersic' and object_err > 1):
                        outfile.writelines(['<TR align="center" \
                                            bgcolor="#CCFFFF"> <TD>', ' ' , \
                                            ' </TD> <TD> ',\
                                            str(values[0])[1:-1], \
                                            ' </TD> <TD> ', \
                                            str(values[1])[:-1], \
                                            ' </TD> <TD> ', str(values[2]), \
                                            ' </TD> <TD> ', str(values[3]), \
                                            ' </TD> <TD> ', ' ', \
                                            ' </TD> <TD> ', str(values[4]), \
                                            ' </TD> <TD> ', str(values[5]), \
                                            ' </TD> <TD> ', str(values[6]), \
                                            ' </TD> <TD> ', str(values[7]), \
                                            ' </TD> </TR> \n' ])
                    if(str(a) == 'sersic' and object_err == 1):
                        outfile.writelines(['<TR align="center" \
                                            bgcolor="#CCFFFF"> <TD>', ' ' , \
                                            ' </TD> <TD> ',\
                                            str(values[0])[1:-1], \
                                            ' </TD> <TD> ', \
                                            str(values[1])[:-1], \
                                            ' </TD> <TD> ', str(values[2]), \
                                            ' </TD> <TD> ', str(values[3]), \
                                            ' </TD> <TD> ', str(round(re_err_kpc, 3))[:5], \
                                            ' </TD> <TD> ', str(values[4]), \
                                            ' </TD> <TD> ', str(values[5]), \
                                            ' </TD> <TD> ', str(values[6]), \
                                            ' </TD> <TD> ', str(values[7]), \
                                            ' </TD> </TR> \n' ])
                        object_err += 1
                    if(str(a) == 'expdisk'):
                        outfile.writelines(['<TR align="center" \
                                            bgcolor="#CCFFFF"> <TD>', ' ' , \
                                            ' </TD> <TD> ',\
                                            str(values[0])[1:-1], \
                                            ' </TD> <TD> ',\
                                            str(values[1])[:-1], \
                                            ' </TD> <TD> ', str(values[2]), \
                                            ' </TD> <TD> ', str(values[3]), \
                                            ' </TD> <TD> ', str(round(rd_err_kpc, 3))[:5], \
                                            ' </TD> <TD> ', ' ' , \
                                            ' </TD> <TD> ', str(values[4]), \
                                            ' </TD> <TD> ', str(values[5]), \
                                            ' </TD> <TD> ', str(values[6]), \
                                            ' </TD> </TR> \n' ])
                a=values[0]				
            except:
                pass
    outfile.writelines(['<TR align="center" bgcolor="#99CCFF"> <TH> \
                         Concentration <TH> Asymmetry <TH> Clumpness <TH>\
                         Gini Coefficient <TH> M20 \
                         <TH> B/D <TH> B/T </TH> </TR> \n'])
    outfile.writelines(['<TR align="center" bgcolor="#CCFFFF"> <TD>',\
                         str(C)[:5], ' </TD> <TD> ', str(A)[:5], \
                        ' </TD> <TD> ', str(S)[:5], ' </TD> <TD> ', str(G)[:5],\
                        ' </TD> <TD> ', str(M)[:5], ' </TD> <TD> ', str(BD)[:5]\
                        , ' </TD> <TD> ', str(BT)[:5], ' </TD> </TR> \n' ])

    outfile.write('</TABLE> \n')		
    outfile.write('</BODY></HTML> \n')
    outfile.close()
    outfile1 = open('galfit.html', 'w')
    outfile1.write('<HTML><HEAD> \n')
    outfile1.writelines(['<META HTTP-EQUIV="Refresh" CONTENT="10; \
                    URL=file:///Vstr/vstr/vvinuv/june-july07/',\
                    'pipeline/galfit.html"> \n'])
    outfile1.write('</HEAD> \n')
    outfile = 'R_' + str(cutimage)[:-4] + 'html'
    try:
        for line in open(outfile, 'r'):
            if(str(line) != '<html>'):
                outfile1.writelines([str(line)])
    except:
        pass
    outfile1.close()

