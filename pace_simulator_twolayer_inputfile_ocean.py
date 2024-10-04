import numpy as np
import random
import sys

def ocean_input_writer(filestrbase,ipss,iocean):
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
    f.write("%f" % albedo_ground + '   #albedo_ground \n')
    f.write("%f" % water_depth_max + '   #water_depth_max \n')
    f.write("%f" % chla[ichla] + '        #CHLa \n')
    f.write("%f" % phytoplankton_index_refraction + '        #PHYTOPLANKTON_INDEX_REFRACTION \n')
    f.write("%f" % phytoplankton_spectral_slope + '        #PHYTOPLANKTON_SPECTRAL_SLOPE\n')
    f.write("%f" % sediment_index_refraction + '        #SEDIMENT_INDEX_REFRACTION \n')
    f.write("%f" % sediment_spectral_slope + '        #SEDIMENT_SPECTRAL_SLOPE \n')
    f.write("%f" % sediment_concentration + '        #SEDIMENT_CONCENTRATION \n')
    f.write("%f" % adg440 + '        #adg440 (1/m), range: 0.0:2.5 \n')
    f.write("%f" % bbp660_BackscatterCoeff + '        #bbp660 (1/m), range 0:0.1\n')
    f.write("%f" % Bp660_BackscatterFraction + '      #Bp660_BackscatterFraction, range 0"0.05 \n')
    f.write("%f" % Sdg + '        #Sdg exponential spectral slope of dg absorption (1/nm) range: 0.01:0.02 \n')
    f.write("%f" % Sbp + '        #Sbp power spectral slope of backscattering coefficient (1/nm) range: 0:0.5\n')
    f.write("%f" % S_Bp + '       #S_Bp power spectral slope of backscattering fraction (1/nm) range: -0.2:0.2 \n')
    f.write("%d" % ncolinput + '        #NCOLINPUT \n')
    f.write("%d" % nquadainput + '        #NQUADAINPUT \n')
    f.write("%d" % nquadoinput + '        #NQUADOINPUT \n')
    f.write("%d" % MAXMORDINPUT + '        #MAXMORDINPUT \n')
    f.write("%d" % NTHETAV + '        #NTHETAV \n')
    f.write("%d" % NPHIV + '        #NPHIV \n')
    f.write("%d" % chla_homogeneity + '        #CHLA_HOMOGENEITY, 1=.true. 0=.false. \n')
    f.write("%d" % ocean_raman_flag + '        #OCEAN_RAMAN_FLAG, 1=.true. 0=.false. \n')
    f.write("%d" % ocean_fchla_flag + '        #OCEAN_FCHLA_FLAG, 1=.true. 0=.false. \n')
    f.write("%d" % ocean_fcdom_flag + '        #OCEAN_FCDOM_FLAG, 1=.true. 0=.false. \n')
    f.write("%d" % ap_select + '              #AP_SELECT, 1 Bricaud LUT, 2 Mixure of pico and micron cells in Ciott et al. 2002 \n')
    f.write("%d" % monochromatic_flag + '     #monochromatic_flag 1=.true. 0=.false. \n')
    f.write("%d" % hyspectral_flag + '        #HYSPECTRAL_FLAG, 1=.true. 0=.false. \n')
    f.write("%d" % npq_flag + '        #NPQ_FLAG, 1=.true. 0=.false. \n')
    f.write("%d" % ocean_phmx_one + '        #OCEAN_PHMX_ONE, 1=.true. 0=.false. \n')
    f.write("%d" % atmos_zero + '        #atmos_zero, 1=.true. 0=.false. \n')
    f.write("%d" % SUNGLINT_INPUT     + '        #SUNGLINT_INPUT, 0 include sun glint 1 no sun glint \n')
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
    f.write("%s" % 'output_ps_' + filestrbase+'\n')
    f.close


RH=np.array([0.30,0.50,0.70,0.75,0.80,0.85,0.90,0.95])

irh=5
wndspd=5.0
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
# negative values mean land surface, please use another script
# 0: atmosphere bounded by ocean surface only
bottom_case_select=np.array([0,1,-203])
albedo_ground=0.3
water_depth_max=200.0

# the following parameters are used in bottom_case_select==2
# chla, phytoplankton_index_refraction,phytoplankton_spectral_slope,
#sediment_index_refraction,sediment_spectral_slope,sediment_concentration
chla=np.array([0.03, 0.3, 3, 10, 30])
ichla=1

phytoplankton_index_refraction=1.02
phytoplankton_spectral_slope=3.0
sediment_index_refraction=1.2
sediment_spectral_slope=4.0
sediment_concentration=0.0

# the following parameters are used in bottom_case_select ==3, the seven parameter model
# chla, adg440, bbp660_BackscatterCoeff,Bp660_BackscatterFraction,Sdg,Sbp,S_Bp
adg440=1.0                         #adg440 (1/m), range: 0.0:2.5
bbp660_BackscatterCoeff=0.05       #bbp660 (1/m), range 0:0.1
Bp660_BackscatterFraction=0.01     #Bp660_BackscatterFraction, range 0"0.05
Sdg=0.015                          #Sdg exponential spectral slope of dg absorption (1/nm) range: 0.01:0.02
Sbp=0.3                            #Sbp power spectral slope of backscattering coefficient (1/nm) range: 0:0.5
S_Bp=0.01                          #S_Bp power spectral slope of backscattering fraction (1/nm) range: -0.2:0.2

ncolinput=40
nquadainput=40
nquadoinput=60
MAXMORDINPUT=40
NTHETAV=36
NPHIV=19

chla_homogeneity=1
ocean_raman_flag=1
ocean_fchla_flag=1
ocean_fcdom_flag=1

ap_select = 1
monochromatic_flag=0
hyspectral_flag=0
npq_flag=0

ocean_phmx_one=1
# if true, only use one phase matrix for ocean waters
atmos_zero=0
SUNGLINT_INPUT=0

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
iocean=1

if(bottom_case_select[iocean]<0) :
	print("this script is for ocean only. Use another script for land surfaces!")
	sys.exit(1)

filestrbase='OceanCase%d' % bottom_case_select[iocean] \
	+ 'tau_ref_hi_%05.2f' % tau_ref_hi  \
	+ 'scatteror_hi_%05.2f' % Height_Particle_hi  \
	+ 'tau_ref_low_%05.2f' % tau_ref_low  \
	+ 'scatteror_low_%05.2f' % Height_Particle_low  \
	+'chla%05.2f' % chla[ichla] \
	+'theta0_%05.2f' %theta0
ocean_input_writer(filestrbase,ipss,iocean)
