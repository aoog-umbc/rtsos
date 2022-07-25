import os
import sys
from shutil import copy, move
import numpy as np

def input_writer(fileinput,fileoutput,iaerosol,irh,isigma,itheta,iopt):
    f = open(fileinput, 'w')
    f.write("%d" % instrument_label+ '        #instrument_label, 1: OCI 2: MODIS 3: SeaWifs 4: MISR \n')
    f.write("%d" % Aerosol_Model[iaerosol]+ '        #IAEROSOL=1,21. 1-10 is Shettle and Fenn, 11-20 is Ahmad model, 21 dust aerosol model \n')
    f.write("%f" % AeroFMF + '        #Aerosol fine mode fraction, only used when Aerosol_Model[iaerosol]==-1 \n')
    f.write("%f" % RH[irh] + '        #Relative Humidity RH=[0.3, 0.50,0.70,0.75, 0.80,0.85,0.90,0.95] \n')
    f.write("%f" % wndspd[isigma] + '        #wind speed \n')
    f.write("%f" % theta0[itheta]+ '       #THETA0 in degrees \n')
    f.write("%f" % tau865[iopt] + '        #TAU865 \n')
    f.write("%f" % pressure_surface + '       # surface pressure in mb \n')
    f.write("%f" % H2O_COLUMN + '       #water vapor column amount in cm \n')
    f.write("%f" % OZONE_COLUMN + '       #ozone column amount in Dobson Unit \n')
    f.write("%d" % iwhitecap + '          #iwhitecap flag; 0 off, 1 on \n')
    f.write("%d" % I_SURFACE_ROUGHNESS_PARA + '  #I_SURFACE_ROUGHNESS_PARA==1; COX&MUNK 1954; 2: GORDON&WANG 1992 \n')
    f.write("%d" % idf+ '        #diffuse transmittance flag; 0 off, 1 on \n')
    f.write("%d" % I_SPHERICAL_SHELL_CORRECTION+ '   #SPHERICAL SHELL CORRECTION flag; 0 off, 1 on \n')
    f.write("%s" % atmos_profile_filename +'\n')
    f.write("%s" % fileoutput +'\n')
    f.close

instrument_label = input("instrument_label=?, enter 1 for OCI, 2 for MODIS, 3 for SeaWifs, 4 for MISR: ")

instrument_label=int(instrument_label)  # 1: OCI table 2: MODIS A 3: SeaWifs

if instrument_label < 1 or instrument_label >4 :
	sys.exit("Your instrument_label value is invalid")

I_SURFACE_ROUGHNESS_PARA=2

I_SPHERICAL_SHELL_CORRECTION=0 # 0/1: turn off/on spherical shell correction

#IAEROSOL=1,21. 1-10 is Shettle and Fenn, 11-20 is Ahmad model, 21 dust aerosol model
Aerosol_Model=([11,12,13,14,15,16,17,18,19,20])
AeroFMF=-1.0E12  # intentionly set it to be bizarre as we don't need it in this work.
tau865=np.array([0.00,0.05,0.10,0.15,0.20,0.25,0.30,0.40,0.50])
RH=np.array([0.3,0.50,0.70,0.75,0.80,0.85,0.90,0.95]) # Relative Humidity values shown the table above
theta0=np.array([ 0., 2., 4., 6., 8., 10., 12., 14., 16., 18., 20., 22., 24., \
				  26., 28., 30., 32., 34., 36., 38., 40., 42., 44., 46., 48., \
				  50., 52., 54., 56., 58., 60., 62., 64., 66., 68., 70., \
				  72., 74., 76., 78., 80., 82., 84., 86., 88.])

sigma = np.array([0, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4])
wndspd=np.empty(sigma.shape)
if I_SURFACE_ROUGHNESS_PARA==1 :
#inverse wind speed from SIGMA^2=0.003D0+0.00512D0*WNDSPD Cox&Munk 1954
	wndspd=(np.square(sigma)-0.003)/0.00512
elif I_SURFACE_ROUGHNESS_PARA==2 :
# Gordon & Wang 1992
	wndspd=(np.square(sigma))/0.00534

wndspd[wndspd<0.0]=0.0
	
if instrument_label == 1 :
	instrument_strbase='OCI'
	Miefile_Dir='OCI_MIE_DIR.txt'
elif instrument_label == 2 :
	instrument_strbase='MODISa'
	Miefile_Dir='MODIS_MIE_DIR.txt'
elif instrument_label == 3 :
	instrument_strbase='SeaWifs'
	Miefile_Dir='SEAWIFS_MIE_DIR.txt'
elif instrument_label == 4 :
	instrument_strbase='Misr'
	Miefile_Dir='MISR_MIE_DIR.txt'

iwhitecap=0
     #if iwhitecap==0 turn off white cap calculation
     #if iwhitecap==1 turn on white cap calculation 
df_flag = ([0,1])  # if idf ==0, regular reflectance calculation
         # if idf ==1, diffuse transmittance calculation

# these two values are the reference values caculated from US standard atmosphere 1976.
OZONE_COLUMN=345.66 # OZONE IN THE WHOLE COLUMN IN DOBSON UNIT
H2O_COLUMN=1.4387   # WATER VAPOR IN THE WHOLE COLUMN IN CENTIMETERS.

pressure_surface=1013.0 #surface pressure in mb


atmos_profile_base='afglus'
atmos_profile_filename=atmos_profile_base+'.dat'

#possible atmosphere profiles are:
#afglus.dat
#afglsw.dat
#afglss.dat
#afglmw.dat
if os.path.isdir(instrument_strbase):
    pass
else:
    os.mkdir(instrument_strbase)
dirnamebase= instrument_strbase + '/Inputfile_Dir_'+instrument_strbase



###########
for idf in df_flag :
	if idf == 0 :
		for iaerosol in range(len(Aerosol_Model)):
			for irh in range(len(RH)):
				dirname=dirnamebase+'AerosolModel%d' % Aerosol_Model[iaerosol] \
									+ 'rh_%f' % RH[irh]
				# Check whether the specified path is an existing directory or not
				isdir = os.path.isdir(dirname)
				if not isdir :
					try:
						os.makedirs(dirname)
					except OSError:
						print ("Creation of the directory %s failed" % dirname)
					else:
						print ("Successfully created the directory %s " % dirname)

				copy('gas_absorption_coeff_dir', dirname)
				copy('auxiliary_directory', dirname)
				copy(Miefile_Dir, dirname)

				for isigma in range(len(sigma)):
					for itheta in range(len(theta0)):
						for iopt in range(len(tau865)):
							filestrbase='LUT_iaerosol%d' % Aerosol_Model[iaerosol] \
								+ 'rh_%f' % RH[irh]       \
								+ 'sigma_%05.2f' % sigma[isigma]       \
								+'theta0_%05.2f' %theta0[itheta] \
								+ 'tau865_%05.2f' % tau865[iopt]
							fileinput='input_'+instrument_strbase+filestrbase
							fileoutput='output_'+instrument_strbase+filestrbase
							input_writer(fileinput,fileoutput,iaerosol,irh,isigma,itheta,iopt)
							move(fileinput,dirname)
	else:
		itheta=1
		for iaerosol in range(len(Aerosol_Model)):
			for irh in range(len(RH)):
				dirname=dirnamebase+'AerosolModel%d' % Aerosol_Model[iaerosol] \
									+ 'rh_%f' % RH[irh]
				# Check whether the specified path is an existing directory or not
				isdir = os.path.isdir(dirname)
				if not isdir :
					try:
						os.makedirs(dirname)
					except OSError:
						print ("Creation of the directory %s failed" % dirname)
					else:
						print ("Successfully created the directory %s " % dirname)

				for isigma in range(len(sigma)):
					for iopt in range(len(tau865)):
						filestrbase='DiffuseT_iaerosol%d' % Aerosol_Model[iaerosol] \
								+ 'rh_%f' % RH[irh]       \
								+ 'sigma_%05.2f' % sigma[isigma]       \
								+ 'tau865_%05.2f' % tau865[iopt]
						fileinput='input_'+instrument_strbase+filestrbase
						fileoutput='output_'+instrument_strbase+filestrbase
						input_writer(fileinput,fileoutput,iaerosol,irh,isigma,itheta,iopt)
						if not os.path.isfile(dirname+'/'+fileinput) :
							move(fileinput,dirname)
						else :
							print (fileinput + 'exist in ' + dirname)





