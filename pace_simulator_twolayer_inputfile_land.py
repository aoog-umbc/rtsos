# ===============================================================
#  RTSOS – Radiative Transfer model based on Successive Orders of Scattering
#  Copyright (C) 2025  Pengwang Zhai, University of Maryland Baltimore County
#
#  Licensed under the Creative Commons Attribution–NonCommercial 4.0
#  International License (CC BY-NC 4.0).
#  You may use, modify, and share this code for research and
#  educational purposes with proper attribution.
#  Commercial use requires written permission from the author.
#
#  Full license: https://creativecommons.org/licenses/by-nc/4.0/
#  Contact: Pengwang Zhai  |  [pwzhai@umbc.edu]
# ===============================================================

import numpy as np
import random
import sys

def RossLi_input_writer(filestrbase,ipss,iocean):
    fileinput='input_ps_'+filestrbase
    f = open(fileinput, 'w')
    f.write("%f" % wndspd + '        #wind speed \n')
    f.write("%f" % theta0+ '       #THETA0 in degrees \n')
    f.write("%f" % wv_pace_ref + '        #WV_PACE_REF \n')
    f.write("%f" % tau_ref_hi + '        #top layer aerosol TAU_REF \n')
    f.write("%f" % Height_Particle_hi + '    # top layer scatteror height \n')
    f.write("%f" % Height_Variance_Particle_hi + '    # top layer scatteror height variance \n')
    f.write("%f" % tau_ref_low + '        #lower layer aerosol TAU_REF \n')
    f.write("%f" % Height_Particle_low + '    # lower layer scatteror height \n')
    f.write("%f" % Height_Variance_Particle_low + '  # lower layer scatteror height variance \n')
    f.write("%d" % Aerosol_Model[iaerosol]+ '  #IAEROSOL=-99,-98,-1,1,20. -99 read aerosol pmhx in from file; -98 read water cloud phmx from file; -1 Ahmad model with flexbile RH and FMF; 1-10 is Shettle and Fenn, 11-20 is Ahmad model \n')
    f.write("%f" % AeroFMF + '        #Aerosol fine mode fraction, only used when Aerosol_Model[iaerosol]==-1 \n')
    f.write("%f" % RH[irh]+ '        #Relative Humidity IRH=1,8, RH=[0.30,0.50,0.70,0.75,0.80,0.85,0.90,0.95] \n')
    f.write("%d" % bottom_case_select[iocean] + '   #bottom_case_select, case -200-203 Land; 0(atmosphere only), case 1 [Chla] parameterization, case 2 [Chla]+Sediment, case 3: seven parameter model\n')
    f.write("%d" % ncolinput + '        #NCOLINPUT \n')
    f.write("%d" % nquadainput + '        #NQUADAINPUT \n')
    f.write("%d" % nquadoinput + '        #NQUADOINPUT \n')
    f.write("%d" % MAXMORDINPUT + '        #MAXMORDINPUT \n')
    f.write("%d" % NTHETAV + '        #NTHETAV \n')
    f.write("%d" % NPHIV + '        #NPHIV \n')
    f.write("%d" % monochromatic_flag + '     #monochromatic_flag 1=.true. 0=.false. \n')
    f.write("%d" % hyspectral_flag + '        #HYSPECTRAL_FLAG, 1=.true. 0=.false. \n')
    f.write("%d" % atmos_zero + '        #atmos_zero, 1=.true. 0=.false. \n')
    f.write("%d" % gas_abs_flag + '        #GAS_ABS_FLAG, 1=.true. 0=.false. \n')
    f.write("%f" % OZONE_COLUMN + '       #ozone column amount in Dobson Unit \n')
    f.write("%f" % H2O_COLUMN + '       #water vapor column amount in cm \n')
    f.write("%f" % NO2_COLUMN + '       #no2 column amount in Dobson Unit \n')
    f.write("%f" % pressure_surface + '       # surface pressure in mb \n')
    f.write("%d" % wv_seg_flag + '        #wv_seg_flag, 0: all; 1: seg1+3only; 2: seg2only; 3 seg1+2+3; 4: seg4only \n')
    f.write("%f" % AirSensor_Height + '       # AirSensor_Height unit km \n')
    f.write("%d" % pss_flag[ipss] + '       # pseudospherical flag, 0 turn off; 1: turn on \n')
    f.write("%s" % aux_dir +'    #aux_dir \n')
    f.write("%s" % gas_absorption_coeff_dir +'    #gas_absorption_coeff_dir \n')
    f.write("%s" % atmos_profile_filename +'\n')
    f.write("%s" % aerosol_phasematrix_file_hi +'\n')
    f.write("%s" % aerosol_phasematrix_file_low +'\n')
    f.write("%s" % land_ref_spectra_filename +'\n')
    f.write("%s" % 'output_ps_' + filestrbase+'\n')
    f.close
    
def RossLi_surf_spec_writer(land_ref_spectra_filename):
    spectra_data=[]
    for iwave in range(len(wavelength_land_ref)) :
        spectra_data.append('{} {} {} {} {}\n'.format(wavelength_land_ref[iwave], fiso[iwave], fvol[iwave], fgeo[iwave], Bpol[iwave]))
    f = open(land_ref_spectra_filename, 'w')
    f.write("%d" % nwv_land_ref + '        #number of wavelength \n')
    f.writelines(spectra_data)
    f.close

RH=np.array([0.30,0.50,0.70,0.75,0.80,0.85,0.90,0.95])

irh=5
wndspd=5.0 #only used for file consistency
theta0=40.0
wv_pace_ref=876.0

tau_ref_hi=0.05
tau_ref_low=0.1

Height_Particle_hi=12.0
Height_Particle_low=4.0

Height_Variance_Particle_hi=2.0
Height_Variance_Particle_low=2.0

Aerosol_Model=([-99,-98, -97, -1,11,12,13,14,15,16,17,18,19,20])
#Aerosol_Model=([-1]) # flexible FMF and RH options for Ahmad's aerosol model.

iaerosol=2

#IAEROSOL=11-20 corresponds to fine mode fraction of
#RATIO_FINE_MODE_ZIA=(/0.0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5, 0.8, 0.95/) ! from personal communication with Zia

#IAEROSOL=-1: Zia aerosol models with flexible FMF and relative humidity.
#IAEROSOL=-98: Water clouds
#IAEROSOL=-99: flexible aerosol models output from seperate package
#IAEROSOL=-97: two layer aerosols, high and lower layer specified by two aerosol files

#AeroFMF=random.random()
AeroFMF=0.3

#bottom_case_select=np.array([-203 -202, -201, -200, 0, 1, 2, 3])
#                              !==-203 Ross Li Land Reflectance
#                              !==-202 Snow Reflectance
#                              !==-201 mRPV land Reflectance
#                              !==-200 Land Lambertian Reflectance
#                              !==0 no ocean water body
#                              !==1 CASE 1 WATER IOPS
#                              !==2 CASE 2 WATER IOPS
#							  !==3 Bio-2 model in polarimeter fitting
# negative values mean land surface
# 0: atmosphere bounded by ocean surface only

bottom_case_select=np.array([0,1,-202,-203])

ncolinput=40
nquadainput=40
nquadoinput=60
MAXMORDINPUT=40
NTHETAV=36
NPHIV=19

monochromatic_flag=0
hyspectral_flag=0

# if true, only use one phase matrix for ocean waters
atmos_zero=0

gas_abs_flag=1

wv_seg_flag=0
AirSensor_Height=2.2
pss_flag=np.array([0, 1])

# these two values are the reference values caculated from US standard atmosphere 1976.
OZONE_COLUMN=345.66 # OZONE IN THE WHOLE COLUMN IN DOBSON UNIT
H2O_COLUMN=1.4387   # WATER VAPOR IN THE WHOLE COLUMN IN CENTIMETERS.
NO2_COLUMN=0.2075   # NO2 IN THE WHOLE COLUMN IN DOBSON UNIT

pressure_surface=1013.0 #surface pressure in mb

aux_dir='/Users/pwzhai/Research/RT/SOS/SOS_Callable/Data/'
gas_absorption_coeff_dir='/Users/pwzhai/Research/RT/Gas_Absorption_Coefficients/'

atmos_profile_base='afglus'
atmos_profile_filename=atmos_profile_base+'.dat'
aerosol_phasematrix_file_hi='output_flexible_aerosol_fullwave.h5'
aerosol_phasematrix_file_low='output_flexible_aerosol_fullwave.h5'

#possible atmosphere profiles are:
#afglus.dat
#afglsw.dat
#afglss.dat
#afglmw.dat

###########
ipss=1
iocean=3

if bottom_case_select[iocean] == -202 :
	nwv_land_ref=6
	wavelength_land_ref=np.array([300.,440.,550.,664.,867.,2260.])
	fiso=np.array([0.99,0.9878,0.9822,0.9615,0.90,0.19])
	fvol=0.0*fiso
	fgeo=0.0*fiso
	Bpol=0.0*fiso
else :
	nwv_land_ref=6
	wavelength_land_ref=np.array([300.,440.,550.,664.,867.,2260.])
	fiso=np.array([0.05,0.05,0.05,0.05,0.05,0.05])
	fvol=0.1*fiso
	fgeo=0.5*fiso
	Bpol=np.ones([nwv_land_ref])

if bottom_case_select[iocean] >= 0 :
	print("this script is for land surface only. Use another script for ocean surfaces!")
	sys.exit(1)
else :
	land_ref_spectra_filename='land_ref_spectra'
	RossLi_surf_spec_writer(land_ref_spectra_filename)
	filestrbase='LandCase%d' % bottom_case_select[iocean] \
		+ 'tau_ref_hi_%05.2f' % tau_ref_hi  \
		+ 'scatteror_hi_%05.2f' % Height_Particle_hi  \
		+ 'tau_ref_low_%05.2f' % tau_ref_low  \
		+ 'scatteror_low_%05.2f' % Height_Particle_low  \
		+'theta0_%05.2f' %theta0
	RossLi_input_writer(filestrbase,ipss,iocean)
