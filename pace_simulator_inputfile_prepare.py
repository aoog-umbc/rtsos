import numpy as np

def input_writer(filestrbase,iocs,ichla,imono,iatmos,isg,igas,iwv):
    fileinput='input_ps_'+filestrbase
    f = open(fileinput, 'w')
    f.write("%f" % wndspd + '        #wind speed \n')
    f.write("%f" % theta0+ '       #THETA0 in degrees \n')
    f.write("%f" % tau550 + '        #TAU550 \n')
    f.write("%d" % irh+ '        #Relative Humidity IRH=1,5, RH=[0.50,0.70,0.80,0.90,0.95] \n')
    f.write("%d" % iaerosol+ '        #IAEROSOL=1,20. 1-10 is Shettle and Fenn, 11-20 is Ahmad model \n')
    f.write("%d" % ocean_case_select[iocs] + '   #OCEAN_CASE_SELECT, case 0(atmosphere only), case 1 [Chla] parameterization, case 2 [Chla]+Sediment, case 3: seven parameter model\n')
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
    f.write("%d" % chla_homogeneity + '        #CHLA_HOMOGENEITY, 1=.true. 0=.false. \n')
    f.write("%d" % ocean_raman_flag + '        #OCEAN_RAMAN_FLAG, 1=.true. 0=.false. \n')
    f.write("%d" % ocean_fchla_flag + '        #OCEAN_FCHLA_FLAG, 1=.true. 0=.false. \n')
    f.write("%d" % ocean_fcdom_flag + '        #OCEAN_FCDOM_FLAG, 1=.true. 0=.false. \n')
    f.write("%d" % ap_select + '              #AP_SELECT, 1 Bricaud LUT, 2 Mixure of pico and micron cells in Ciott et al. 2002 \n')
    f.write("%d" % monochromatic_flag[imono] + '     #monochromatic_flag 1=.true. 0=.false. \n')
    f.write("%d" % hyspectral_flag + '        #HYSPECTRAL_FLAG, 1=.true. 0=.false. \n')
    f.write("%d" % npq_flag + '        #NPQ_FLAG, 1=.true. 0=.false. \n')
    f.write("%d" % ocean_phmx_one + '        #OCEAN_PHMX_ONE, 1=.true. 0=.false. \n')
    f.write("%d" % atmos_zero[iatmos] + '        #atmos_zero, 1=.true. 0=.false. \n')
    f.write("%d" % SUNGLINT_INPUT[isg] + '        #SUNGLINT_INPUT, 0 include sun glint 1 no sun glint \n')
    f.write("%d" % gas_abs_flag[igas] + '        #GAS_ABS_FLAG, 1=.true. 0=.false. \n')
    f.write("%f" % OZONE_COLUMN + '       #ozone column amount in Dobson Unit \n')
    f.write("%f" % H2O_COLUMN + '       #water vapor column amount in cm \n')
    f.write("%f" % pressure_surface + '       # surface pressure in mb \n')
    f.write("%d" % wv_seg_flag[iwv] + '        #wv_seg_flag, 0: all; 1: seg1+3only; 2: seg2only; 3 seg1+2+3; 4: seg4only \n')
    f.write("%f" % AirSensor_Height + '       # AirSensor_Height unit km \n')
    f.write("%d" % pss_flag + '       # pseudospherical flag, 0 turn off; 1: turn on \n')
    f.write("%s" % atmos_profile_filename +'\n')
    f.write("%s" % 'output_ps_' + filestrbase+'\n')
    f.close

wndspd=5.0
theta0=30.0
tau550=0.1
irh=3
iaerosol=16

ocean_case_select=np.array([0, 1, 2, 3])
# the following parameters are used in ocean_case_select==2
# chla, phytoplankton_index_refraction,phytoplankton_spectral_slope,
#sediment_index_refraction,sediment_spectral_slope,sediment_concentration
chla=np.array([0.01, 0.1, 1.0])
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

chla_homogeneity=1
ocean_raman_flag=1
ocean_fchla_flag=1
ocean_fcdom_flag=1

ap_select = 1
monochromatic_flag=np.array([0, 1])
hyspectral_flag=0
npq_flag=0

ocean_phmx_one=1
# if true, only use one phase matrix for ocean waters
atmos_zero=np.array([0, 1])
SUNGLINT_INPUT=np.array([0, 1])

gas_abs_flag=np.array([0, 1])
wv_seg_flag=np.array([0, 1, 2, 3, 4])
AirSensor_Height=2.2
pss_flag=1

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

###########

for iocs in range(len(ocean_case_select)):
    for ichla in range(len(chla)):
        for imono in range(len(monochromatic_flag)):
            for iatmos in range(len(atmos_zero)):
                for isg in range(len(SUNGLINT_INPUT)):
                    for igas in range(len(gas_abs_flag)):
                        for iwv in range(len(wv_seg_flag)):
                            filestrbase='OceanCase%d' % ocean_case_select[iocs] \
				       +'chla%05.2f' % chla[ichla] \
				       +'mono%d' % monochromatic_flag[imono] \
				       +'atmoszero%d' % atmos_zero[iatmos] \
				       +'sg%d' % SUNGLINT_INPUT[isg]   \
				       +'gasflag%d' % gas_abs_flag[igas]   \
				       +'wv_seg_flag%d' % wv_seg_flag[iwv]
                            input_writer(filestrbase,iocs,ichla,imono,iatmos,isg,igas,iwv)






