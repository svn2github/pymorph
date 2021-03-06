from os.path import exists
import csv
import fileinput
from cosmocal import *
#from utilities import WriteDb
import config as c
import numpy as n

def ReadLog(ParamDict, No):
    if exists('fit.log'):
        for line in open('fit.log','r'): 
            values = line.split() 
            try: 
                if(str(values[0]) == 'Input'):
                    alpha_ned = str(alpha_j)[:6]
                    delta_ned = str(delta_j)[:6]
                if(str(values[0]) == 'Init.'):
                    initial_conf = str(values[4])
                if(str(values[0]) == 'Restart'):
                    restart_conf = str(values[3])
                if(str(values[0]) == 'Chi^2/nu'):
                    chi2nu = float(values[2])
                    Distance = str(round(distance, 3))[:5]
                if(str(values[0]) == 'sersic'):
                    ParamDict[No][2][0] = float(values[2][1:-1])
                    ParamDict[No][2][1] = float(values[3][:-1])
                    ParamDict[No][3] = float(values[4])
                    ParamDict[No][4] = float(values[5])
                    ParamDict[No][5] = float(values[6])
                    ParamDict[No][6] = float(values[7])
                    ParamDict[No][7] = float(values[8])
		    ParamDict[No][8] = float(values[9])
                    No += 1
                if(str(values[0]) == 'expdisk'):
                    ParamDict[No][2][0] = float(values[2][1:-1])
                    ParamDict[No][2][1] = float(values[3][:-1])
                    ParamDict[No][3] = float(values[4])
                    ParamDict[No][4] = float(values[5])
                    ParamDict[No][5] = float(values[6])
                    ParamDict[No][6] = float(values[7])
                    ParamDict[No][7] = float(values[8])
                    No += 1
                if(str(values[0]) == 'psf'):
                    ParamDict[No][2][0] = float(values[2][1:-1])
                    ParamDict[No][2][1] = float(values[3][:-1])
                    ParamDict[No][3] = float(values[4])
                    No += 1
                if(str(values[0]) == 'sky'):
                    for j in range(len(ParamDict)):
                        i = j + 1
                        if ParamDict[i][1] == 'sky':
                            ParamDict[i][2] = float(values[4])
            except:
                pass
#        if 'bulge' in ComP and 'disk' in ComP:
#            BD = 10**(-0.4 * ( mag_b - mag_d))
#            BT = 1.0 / (1.0 + 1.0 / BD)
#        elif 'bulge' in ComP:
#            BD = 'nan'
#            BT = 1.0
#        elif 'disk' in ComP:
#            BD = 0.0
#            BT = 0.0
#        else:
#            BD = 'nan'
#            BT = 'nan'
    return ParamDict
#a = {1: {1: 'sersic', 2: [65.688000000000002, 65.738], 3: 22.5169, 4: 10.288, 5: 4.0, 6: 0.33636057854019513, 7: -12.900000000000006, 8: 0, 9: 0, 11: 'Main'}, 2: {1: 'expdisk', 2: [65.688000000000002, 65.738], 3: 22.5169, 4: 10.288, 5: 0.33636057854019513, 6: -12.900000000000006, 7: 0, 8: 0, 11: 'Main'}, 3: {1: 'sersic', 2: [56.633000000000003, 107.64100000000001], 3: 22.5913, 4: 5.7359999999999998, 5: 4.0, 6: 0.66979236436704614, 7: -75.799999999999997, 8: 0, 9: 0, 11: 'Other'}, 4: {1: 'sky', 2: -0.001669224, 3: 0, 4: 0, 5: 0, 11: 'Other'}}

#print ReadLog(a)
