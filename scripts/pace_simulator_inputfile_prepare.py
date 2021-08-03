import numpy as np

def input_writer(filestrbase,ichla,itheta,ipss):
    fileinput='input_ps_'+filestrbase
    f = open(fileinput, 'w')
    f.write("%f" % wndspd + '        #wind speed \n')
    f.write("%f" % theta0[itheta]+ '       #THETA0 in degrees \n')
    f.write("%f" % wv_pace_ref + '        #WV_PACE_REF \n')
    f.write("%f" % tau_ref + '        #TAU_REF \n')
    f.write("%f" % RH[irh]+ '        #Relative Humidity IRH=1,8, RH=[0.30,0.50,0.70,0.75,0.80,0.85,0.90,0.95] \n')
    f.write("%d" % iaerosol+ '        #IAEROSOL=-99,1,20. -99 read in from file; 1-10 is Shettle and Fenn, 11-20 is Ahmad model \n')
    f.write("%d" % ocean_case_select + '   #OCEAN_CASE_SELECT, case 0(atmosphere only), case 1 [Chla] parameterization, case 2 [Chla]+Sediment, case 3: seven parameter model\n')
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
    f.write("%s" % atmos_profile_filename +'\n')
    f.write("%s" % aerosol_phasematrix_file +'\n')
    f.write("%s" % 'output_ps_' + filestrbase+'\n')
    f.close

RH=np.array([0.30,0.50,0.70,0.75,0.80,0.85,0.90,0.95])

irh=4
wndspd=5.0
theta0=np.array([30.0, 85.0])
wv_pace_ref=873.0
tau_ref=0.1


iaerosol=16

#ocean_case_select=np.array([0, 1, 2, 3])
ocean_case_select=1
water_depth_max=200.0

# the following parameters are used in ocean_case_select==2
# chla, phytoplankton_index_refraction,phytoplankton_spectral_slope,
#sediment_index_refraction,sediment_spectral_slope,sediment_concentration
chla=np.array([0.01, 0.03, 0.1, 0.3, 1.0, 3, 10])
phytoplankton_index_refraction=1.02
phytoplankton_spectral_slope=3.0
sediment_index_refraction=1.2
sediment_spectral_slope=4.0
sediment_concentration=0.0

# the following parameters are used in ocean_case_select ==3, the seven parameter model
# chla, adg440, bbp660_BackscatterCoeff,Bp660_BackscatterFraction,Sdg,Sbp,S_Bp
adg440=1.0                         #adg440 (1/m), range: 0.0:2.5
bbp660_BackscatterCoeff=0.05       #bbp660 (1/m), range 0:0.1
Bp660_BackscatterFraction=0.01     #Bp660_BackscatterFraction, range 0"0.05
Sdg=0.015                          #Sdg exponential spectral slope of dg absorption (1/nm) range: 0.01:0.02
Sbp=0.3                            #Sbp power spectral slope of backscattering coefficient (1/nm) range: 0:0.5
S_Bp=0.01                          #S_Bp power spectral slope of backscattering fraction (1/nm) range: -0.2:0.2

ncolinput=20
nquadainput=40
nquadoinput=60
MAXMORDINPUT=20
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


atmos_profile_base='afglus'
atmos_profile_filename=atmos_profile_base+'.dat'
aerosol_phasematrix_file='output_flexible_nmode3_fmixing_2_fmfrac_0.500_dmfrac_0.200_cmfrac_0.300_dmsfrac_0.600_fwatersol_0.600_fBrc_0.100_fsoot_0.300.h5'
#possible atmosphere profiles are:
#afglus.dat
#afglsw.dat
#afglss.dat
#afglmw.dat

###########

for ichla in range(len(chla)):
	for itheta in range(len(theta0)):
		for ipss in range(len(pss_flag)):
			filestrbase='OceanCase%d' % ocean_case_select \
						+ 'tau_ref_%05.2f' % tau_ref       \
						+'chla%05.2f' % chla[ichla] \
						+'theta0_%05.2f' %theta0[itheta] \
						+'pss%d'%pss_flag[ipss]
			input_writer(filestrbase,ichla,itheta,ipss)






