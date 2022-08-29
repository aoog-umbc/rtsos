import numpy as np
import random

def input_writer(filestrbase,wndspd,RH,AeroFMF,H2O_COLUMN,theta0,tau_ref):
    fileinput='input_ps_'+filestrbase
    f = open(fileinput, 'w')
    f.write("%f" % wndspd + '        #wind speed \n')
    f.write("%f" % theta0+ '       #THETA0 in degrees \n')
    f.write("%f" % wv_pace_ref + '        #WV_PACE_REF \n')
    f.write("%f" % tau_ref+ '        #TAU_REF \n')
    f.write("%d" % Aerosol_Model[iaerosol]+ '  #IAEROSOL=-99,-1,1,20. -99 read in from file; -1; Ahmad model with flexbile RH and FMF; 1-10 is Shettle and Fenn, 11-20 is Ahmad model \n')
    f.write("%f" % AeroFMF + '        #Aerosol fine mode fraction, only used when Aerosol_Model[iaerosol]==-1 \n')
    f.write("%f" % RH+ '    #Relative Humidity IRH=1,5, RH=[0.30,0.50,0.70,0.75,0.80,0.85,0.90,0.95] \n')
    f.write("%d" % ocean_case_select + '   #OCEAN_CASE_SELECT, case 0(atmosphere only), case 1 [Chla] parameterization, case 2 [Chla]+Sediment, case 3: seven parameter model\n')
    f.write("%f" % water_depth_max + '   #water_depth_max \n')
    f.write("%f" % chla+ '        #CHLa \n')
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
    f.write("%d" % SUNGLINT_INPUT + '        #SUNGLINT_INPUT, 0 include sun glint 1 no sun glint \n')
    f.write("%d" % gas_abs_flag + '        #GAS_ABS_FLAG, 1=.true. 0=.false. \n')
    f.write("%f" % OZONE_COLUMN + '       #ozone column amount in Dobson Unit \n')
    f.write("%f" % H2O_COLUMN + '       #water vapor column amount in cm \n')
    f.write("%f" % NO2_COLUMN + '       #no2 column amount in Dobson Unit \n')
    f.write("%f" % pressure_surface + '       # surface pressure in mb \n')
    f.write("%d" % wv_seg_flag + '        #wv_seg_flag, 0: all; 1: seg1+3only; 2: seg2only; 3 seg1+2+3; 4: seg4only \n')
    f.write("%f" % AirSensor_Height + '       # AirSensor_Height unit km \n')
    f.write("%d" % pss_flag + '       # pseudospherical flag, 0 turn off; 1: turn on \n')
    f.write("%s" % atmos_profile_filename +'\n')
    f.write("%s" % aerosol_phasematrix_file +'\n')
    f.write("%s" % 'output_ps_' + filestrbase+'\n')
    f.close

ocean_case_select=0
monochromatic_flag=0
atmos_zero=0
gas_abs_flag=1
wv_seg_flag=0
SUNGLINT_INPUT=0

water_depth_max=200.0

#RH=np.array([0.30,0.50,0.70,0.75,0.80,0.85,0.90,0.95])
#AeroFMF=random.random()
chla=0.01
# the following parameters are used in ocean_case_select==2
# chla, phytoplankton_index_refraction,phytoplankton_spectral_slope,
#sediment_index_refraction,sediment_spectral_slope,sediment_concentration
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

hyspectral_flag=0
npq_flag=0

ocean_phmx_one=1
# if true, only use one phase matrix for ocean waters

AirSensor_Height=2.2
pss_flag=0

# these two values are the reference values caculated from US standard atmosphere 1976.
OZONE_COLUMN=345.66 # OZONE IN THE WHOLE COLUMN IN DOBSON UNIT
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
# Now lets generate the 100 terms of halton sequence between 0 and 1 
dim=6
n_sample=10

def primes_from_2_to(n):
    sieve = np.ones(n // 3 + (n % 6 == 2), dtype=bool)
    for i in range(1, int(n ** 0.5) // 3 + 1):
        if sieve[i]:
            k = 3 * i + 1 | 1
            sieve[k * k // 3::2 * k] = False
            sieve[k * (k - 2 * (i & 1) + 4) // 3::2 * k] = False
    return np.r_[2, 3, ((3 * np.nonzero(sieve)[0][1:] + 1) | 1)]


def van_der_corput(n_sample, base=2):
    n_sample,base=int(n_sample),int(base)
    sequence = []
    for i in range(n_sample):
        n_th_number, denom = 0., 1.
        while i > 0:
            i, remainder = divmod(i, base)
            denom *= base
            n_th_number += remainder / denom
        sequence.append(n_th_number)

    return sequence


def halton(dim, n_sample):
    big_number = 10
    while 'Not enought primes':
        base = primes_from_2_to(big_number)[:dim]
        if len(base) == dim:
            break
        big_number += 1000

    # Generate a sample using a Van der Corput sequence per dimension.
    sample = [van_der_corput(n_sample + 1, dim) for dim in base]
    sample = np.stack(sample, axis=-1)[1:]

    return sample

hs=halton(dim,n_sample) #this gives the sequence of halton terms stacked in 
                       #n_sample dimensional array with 5 independent halton
                       # terms along each dimension
wv_pace_ref=873.0

# Now lets generate different input parameters and hence files based on halton sequnces
Aerosol_Model=np.array([-1,11,12,13,14,15,16,17,18,19,20])
iaerosol=0

for j in range(n_sample):
    r=hs[j] #gives 1d array of 5 independent halton terms
    
    wndspd=0+r[0]*(30-0) #Wind spped between 0 and 30.
    RH=0.3+r[1]*(0.99-0.3) #Relative Humidity 0.3 and 0.99.
    AeroFMF=0.0+r[2]*(1.0-0) #Fine mode fraction between 0 and 1.
    H2O_COLUMN=0.0+r[3]*(6.0-0) #1.4387  # WATER VAPOR IN THE WHOLE COLUMN IN CENTIMETERS.
    theta0=0+r[4]*(85-0)#theta0 range=[0,85]
    tau_ref=0.01+r[5]*(0.4-0.01)#tau_ref range=[0.01,0.4]
    filestrbase='W%05.2f' % wndspd \
               +'FMF%05.2f' % AeroFMF \
               +'rh%05.2f' % RH \
               +'H2O_COLUMN%05.2f' % H2O_COLUMN \
               +'theta0%05.2f' %theta0 \
               +'tau_ref%05.2f' %tau_ref
    input_writer(filestrbase,wndspd,RH,AeroFMF,H2O_COLUMN,theta0,tau_ref)
#
#




