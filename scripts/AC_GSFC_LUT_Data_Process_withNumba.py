# python script to post processing aerosol LUT for MODIS and SeaWifs
# 03/31/2021 by Pengwang Zhai
from numba import jit
import os
import sys
import fnmatch
import math
import numpy as np
import h5py
import itertools
#import matplotlib.pyplot as plt

### To use the script, run the following command from the terminal:
### python MODIS_Data_Process_withNumba.py
### enter instrument_label from command line:
### instrument_label=1, 2, 3, 4  #1: OCI 2: MODIS A 3: SeaWifs 4: MISR

########## postprocessing functions section starts here ##########
def LUTDataPostProcessing(iaerosol,irh):
	writeflag=1

	### read in Mie scattering file
	with open(MIE_SCAT_Dir, 'r') as file:
		Mie_Filedir = file.read().replace('\n', '')

	aerosol_singe_scattering_albedo=np.empty(wavelengths.shape,np.float32)
	MIE_SCAT_Filename=Mie_Filedir+'/'+MIE_str_base + \
		'_MODFINE%4.2f' %RATIO_FINE_MODE_ZIA[Aerosol_Model[iaerosol]-11] + \
		'RH%4.2f'%RH[irh] + '.h5'
	if(os.path.isfile(MIE_SCAT_Filename)) :
		h5_MieScat=h5py.File(MIE_SCAT_Filename)
		arslnd1=np.array(h5_MieScat['AerosolNumberConcentration_f'],np.float32)
		arslnd2=np.array(h5_MieScat['AerosolNumberConcentration_c'],np.float32)
		CSCAT1=np.array(h5_MieScat['CSCATf'],np.float32)
		CSCAT2=np.array(h5_MieScat['CSCATc'],np.float32)
		CEXT1=np.array(h5_MieScat['CEXTf'],np.float32)
		CEXT2=np.array(h5_MieScat['CEXTc'],np.float32)
		NUMMIEANG=np.array(h5_MieScat['NUMMIEANG'],np.int)
		scattering_angle=np.array(h5_MieScat['SCAT_ANG'],np.float32)

		PHMX1=np.array(h5_MieScat['PHMXf'],np.float32)
		PHMX2=np.array(h5_MieScat['PHMXc'],np.float32)
		PHMX=np.empty((wavelengths.size,6,scattering_angle.size),np.float32)

		finemodeweight=arslnd1*CSCAT1/(arslnd1*CSCAT1+arslnd2*CSCAT2)

		for iWavelength in range(wavelengths.size) :
			aerosol_singe_scattering_albedo[iWavelength]=(arslnd1*CSCAT1[iWavelength]+arslnd2*CSCAT2[iWavelength]) \
						/(arslnd1*CEXT1[iWavelength]+arslnd2*CEXT2[iWavelength])
			for iscat in range(len(scattering_angle)) :
				for ielem in range(6) :
					PHMX[iWavelength][ielem][iscat]= \
						PHMX1[ielem][iscat][iWavelength]*finemodeweight[iWavelength] + \
						PHMX2[ielem][iscat][iWavelength]*(1.0-finemodeweight[iWavelength])
	else :
		print(MIE_SCAT_Filename +' does not exist')
		writeflag=0

	### initialize the reflectand and transmittance fields
	Rad_DiffT_Boa2Toa=np.empty((wavelengths.size,sigma.size,tau865.size,nthetav),np.float32)
	Rad_DiffT_Too2Toa=np.empty((wavelengths.size,sigma.size,tau865.size,nthetav),np.float32)

	Irrad_TranM_Toa2Boa=np.empty((wavelengths.size,sigma.size,tau865.size,theta0.size),np.float32)
	Irrad_TranM_Toa2Too=np.empty((wavelengths.size,sigma.size,tau865.size,theta0.size),np.float32)
	Rho_t=np.empty((wavelengths.size,sigma.size,tau865.size,theta0.size,PhiV.size,nthetav),np.float32)
	Q_t=np.empty((wavelengths.size,sigma.size,tau865.size,theta0.size,PhiV.size,nthetav),np.float32)
	U_t=np.empty((wavelengths.size,sigma.size,tau865.size,theta0.size,PhiV.size,nthetav),np.float32)

	Rho_g=np.empty((wavelengths.size,sigma.size,tau865.size,theta0.size,PhiV.size,nthetav),np.float32)
	Q_g=np.empty((wavelengths.size,sigma.size,tau865.size,theta0.size,PhiV.size,nthetav),np.float32)
	U_g=np.empty((wavelengths.size,sigma.size,tau865.size,theta0.size,PhiV.size,nthetav),np.float32)

	for isigma, iopt in itertools.product(range(len(sigma)), range(len(tau865))):
		itheta=1
		filestrbase='DiffuseT_iaerosol%d' % Aerosol_Model[iaerosol] + 'rh_%f' % RH[irh] + 'sigma_%05.2f' % sigma[isigma]                                   + 'tau865_%05.2f' % tau865[iopt]
		diffuseTranfileoutput='output_'+instrument_strbase+filestrbase+'.h5'
		if(not os.path.isfile(diffuseTranfileoutput)) :
			print(diffuseTranfileoutput+' does not exist')
			writeflag=0
			break

		h5_diffuseT=h5py.File(diffuseTranfileoutput)
			
# read in and calculate radiance diffuse transmittance
		thetav_simu=np.array(h5_diffuseT['ThetaV'],np.float32)
		Wavelength_Simu=np.array(h5_diffuseT['WaveLength'],np.float32)
		Atmos_Layer_Alt=np.array(h5_diffuseT['Altitude'],np.float32)
		Radiance_TOA=np.array(h5_diffuseT['Radiance_TOA'],np.float32)
		Radiance_BOA=np.array(h5_diffuseT['Radiance_BOA'],np.float32)
		Radiance_TOO=np.array(h5_diffuseT['Radiance_TOO'],np.float32)
		Surface_Pressure_in_mb=np.array(h5_diffuseT['Surface_Pressure_in_mb'],np.float32)

		Tau_Aerosol_Extinction=np.array(h5_diffuseT['Tau_Aerosol_Extinction'],np.float32)
		Tau_Rayleigh_Extinction=np.array(h5_diffuseT['Tau_Rayleigh_Extinction'],np.float32)
		sigmatemp=np.array(h5_diffuseT['SIGMA'],np.float32)
		if abs(sigma[isigma]-sigmatemp[0])>1.0e-6 :
			sys.exit("Check sigma values")

#		finemode_fraction=np.array(h5_diffuseT['AerosolFineModeFraction'],np.float32)
		finemode_fraction=np.array(RATIO_FINE_MODE_ZIA[Aerosol_Model[iaerosol]-11],np.float32)

		test_flag1=max(abs(thetav_simu-ThetaV))
		test_flag2=max(abs(Wavelength_Simu-wavelengths))
			
		if test_flag1 > 1.0e-5 :
			sys.exit("Check thetav values")
		if test_flag2 > 1.0e-5 :
			sys.exit("Check wavelength values")

		assign_diffuse_transmittance(wavelengths,nthetav,isigma,iopt, \
		                        Rad_DiffT_Boa2Toa,Rad_DiffT_Too2Toa,\
    		                    Radiance_TOA,Radiance_BOA,Radiance_TOO)

#		for iWavelength in range(len(wavelengths)):
#			for iThetaV in range(nthetav):
#				Rad_DiffT_Boa2Toa[iWavelength][isigma][iopt][iThetaV] =  \
#					Radiance_TOA[0,iThetaV,iWavelength]/Radiance_BOA[0,iThetaV,iWavelength]
#				Rad_DiffT_Too2Toa[iWavelength][isigma][iopt][iThetaV] =  \
#					Radiance_TOA[0,iThetaV,iWavelength]/Radiance_TOO[0,iThetaV,iWavelength]
			
		for itheta in range(len(theta0)):
			filestrbase='LUT_iaerosol%d' % Aerosol_Model[iaerosol] + 'rh_%f' % RH[irh] + 'sigma_%05.2f' % sigma[isigma]                                   +'theta0_%05.2f' %theta0[itheta]                             + 'tau865_%05.2f' % tau865[iopt]
			fileoutput='output_'+instrument_strbase+filestrbase+'.h5'
			if(not os.path.isfile(fileoutput)) :
				writeflag=0
				break
				
			h5_reflectance=h5py.File(fileoutput)
			MU_SOLAR=np.array(h5_reflectance['MU_SOLAR'],np.float32)
			PhiV_simu=np.array(h5_reflectance['PhiV'],np.float32)
			ThetaV_simu=np.array(h5_reflectance['ThetaV'],np.float32)
				
			test_flag3=max(abs(PhiV_simu-PhiV))
			test_flag4=max(abs(ThetaV_simu-ThetaV))
			test_flag5=abs(MU_SOLAR[0]+math.cos(theta0[itheta]/180.0*np.pi))
			if test_flag3 > 1.0e-5 :
				sys.exit("Check phiv values")
			if test_flag4 > 1.0e-5 :
				sys.exit("Check ThetaV values")
			if test_flag5 > 1.0e-5 :
				sys.exit("Check cos(theta0) values")
					
			Irradiance_TOA_Downwelling = np.array(h5_reflectance['Irrad_Down_TOA'],np.float32)
			Radiance_TOA=np.array(h5_reflectance['Radiance_TOA'],np.float32)
			Q_TOA=np.array(h5_reflectance['Q_TOA'],np.float32)
			U_TOA=np.array(h5_reflectance['U_TOA'],np.float32)

			Radiance_TOA_Glint=np.array(h5_reflectance['Radiance_TOA_Glint'],np.float32)
			Q_TOA_Glint=np.array(h5_reflectance['Q_TOA_Glint'],np.float32)
			U_TOA_Glint=np.array(h5_reflectance['U_TOA_Glint'],np.float32)

			Irradiance_BOA_Downwelling = np.array(h5_reflectance['Irrad_Down_BOA'],np.float32)
			Irradiance_TOO_Downwelling = np.array(h5_reflectance['Irrad_Down_TOO'],np.float32)

			assign_reflectance(wavelengths,PhiV,nthetav,isigma,iopt,itheta, \
				Irrad_TranM_Toa2Boa,Irrad_TranM_Toa2Too,Rho_t,Q_t,U_t,\
				Irradiance_BOA_Downwelling,Irradiance_TOA_Downwelling,\
				Irradiance_TOO_Downwelling,Radiance_TOA,Q_TOA,U_TOA,\
				Rho_g,Q_g,U_g,Radiance_TOA_Glint,Q_TOA_Glint,U_TOA_Glint)

#			for iWavelength in range(len(wavelengths)):
#				Irrad_TranM_Toa2Boa[iWavelength][isigma][iopt][itheta] =                             Irradiance_BOA_Downwelling[iWavelength]/Irradiance_TOA_Downwelling[iWavelength]
#				Irrad_TranM_Toa2Too[iWavelength][isigma][iopt][itheta] =                             Irradiance_TOO_Downwelling[iWavelength]/Irradiance_TOA_Downwelling[iWavelength]
#				for iPhi in range(len(PhiV)):
#					for iThetaV in range(nthetav):
#						Rho_t[iWavelength][isigma][iopt][itheta][iPhi][iThetaV]=                                     np.pi*Radiance_TOA[iPhi][iThetaV][iWavelength]/Irradiance_TOA_Downwelling[iWavelength]
#						Q_t[iWavelength][isigma][iopt][itheta][iPhi][iThetaV]=                                     np.pi*Q_TOA[iPhi][iThetaV][iWavelength]/Irradiance_TOA_Downwelling[iWavelength]
#						U_t[iWavelength][isigma][iopt][itheta][iPhi][iThetaV]=                                     np.pi*U_TOA[iPhi][iThetaV][iWavelength]/Irradiance_TOA_Downwelling[iWavelength]
		if(writeflag==0):
			break
	if writeflag==1 :
		data_process_output_filename='rt_sos_aerosol'+instrument_strbase+ 'r_%f' % RH[irh] \
							   +'f%f' % RATIO_FINE_MODE_ZIA[Aerosol_Model[iaerosol]-11] +'.h5'
		if(os.path.isfile(data_process_output_filename)) :
			print(data_process_output_filename + ' exist')
		else :
			h5_rho = h5py.File(data_process_output_filename, 'w')
			h5_rho.create_dataset('rho_t', data=Rho_t)
			h5_rho.create_dataset('q_t', data=Q_t)
			h5_rho.create_dataset('u_t', data=U_t)
			h5_rho.create_dataset('rho_g', data=Rho_g)
			h5_rho.create_dataset('q_g', data=Q_g)
			h5_rho.create_dataset('u_g', data=U_g)

			h5_rho.create_dataset('Rad_DiffT_Boa2Toa', data=Rad_DiffT_Boa2Toa)
			h5_rho.create_dataset('Rad_DiffT_Too2Toa', data=Rad_DiffT_Too2Toa)
			h5_rho.create_dataset('Irrad_Transmittance_Toa2Boa', data=Irrad_TranM_Toa2Boa)
			h5_rho.create_dataset('Irrad_Transmittance_Toa2Too', data=Irrad_TranM_Toa2Too)
			h5_rho.create_dataset('solz', data=theta0)
			h5_rho.create_dataset('senz', data=ThetaV[0:nthetav])
			h5_rho.create_dataset('phi', data=PhiV)
			h5_rho.create_dataset('wavelength', data=Wavelength_Simu)
			h5_rho.create_dataset('aerosol_optical_depth_865nm', data=tau865)
			h5_rho.create_dataset('sigma', data=sigma)
			h5_rho.create_dataset('rh', data=RH[irh])
			h5_rho.create_dataset('finemodefraction', data=finemode_fraction)
			h5_rho.create_dataset('Atmosphere_Layer_Altitudes', data=Atmos_Layer_Alt)
			h5_rho.create_dataset('Surface_Pressure_in_mb', data=Surface_Pressure_in_mb)
			h5_rho.create_dataset('scattering_angle', data=scattering_angle)
			h5_rho.create_dataset('scattering_matrix', data=PHMX)
			h5_rho.create_dataset('aerosol_ssa', data=aerosol_singe_scattering_albedo)
			h5_rho.close()
			print(dirname+ ' is processed')


@jit(nopython=True) # Set "nopython" mode for best performance, equivalent to @njit
def assign_diffuse_transmittance(wavelengths,nthetav,isigma,iopt, \
		Rad_DiffT_Boa2Toa,Rad_DiffT_Too2Toa,Radiance_TOA,Radiance_BOA,Radiance_TOO):
	for iWavelength in range(len(wavelengths)):
		for iThetaV in range(nthetav):
			Rad_DiffT_Boa2Toa[iWavelength][isigma][iopt][iThetaV] =  \
			    Radiance_TOA[0,iThetaV,iWavelength]/Radiance_BOA[0,iThetaV,iWavelength]
			Rad_DiffT_Too2Toa[iWavelength][isigma][iopt][iThetaV] =  \
			    Radiance_TOA[0,iThetaV,iWavelength]/Radiance_TOO[0,iThetaV,iWavelength]

@jit(nopython=True) # Set "nopython" mode for best performance, equivalent to @njit
def assign_reflectance(wavelengths,PhiV,nthetav,isigma,iopt,itheta, \
              Irrad_TranM_Toa2Boa,Irrad_TranM_Toa2Too,Rho_t,Q_t,U_t,\
			  Irradiance_BOA_Downwelling,Irradiance_TOA_Downwelling,\
			  Irradiance_TOO_Downwelling,Radiance_TOA,Q_TOA,U_TOA,\
			  Rho_g,Q_g,U_g,Radiance_TOA_Glint,Q_TOA_Glint,U_TOA_Glint):

	for iWavelength in range(len(wavelengths)):
		Irrad_TranM_Toa2Boa[iWavelength][isigma][iopt][itheta] = \
			  Irradiance_BOA_Downwelling[iWavelength]/         \
			  Irradiance_TOA_Downwelling[iWavelength]
		Irrad_TranM_Toa2Too[iWavelength][isigma][iopt][itheta] = \
				Irradiance_TOO_Downwelling[iWavelength]/       \
				Irradiance_TOA_Downwelling[iWavelength]
		for iPhi in range(len(PhiV)):
			for iThetaV in range(nthetav):
				Rho_t[iWavelength][isigma][iopt][itheta][iPhi][iThetaV]=\
				   np.pi*Radiance_TOA[iPhi][iThetaV][iWavelength]/ \
						 Irradiance_TOA_Downwelling[iWavelength]
				Q_t[iWavelength][isigma][iopt][itheta][iPhi][iThetaV]=\
				   np.pi*Q_TOA[iPhi][iThetaV][iWavelength]/         \
				   Irradiance_TOA_Downwelling[iWavelength]
				U_t[iWavelength][isigma][iopt][itheta][iPhi][iThetaV]=\
				   np.pi*U_TOA[iPhi][iThetaV][iWavelength]/         \
				   Irradiance_TOA_Downwelling[iWavelength]
				Rho_g[iWavelength][isigma][iopt][itheta][iPhi][iThetaV]=\
				   np.pi*Radiance_TOA_Glint[iPhi][iThetaV][iWavelength]/ \
						 Irradiance_TOA_Downwelling[iWavelength]
				Q_g[iWavelength][isigma][iopt][itheta][iPhi][iThetaV]=\
				   np.pi*Q_TOA_Glint[iPhi][iThetaV][iWavelength]/         \
				   Irradiance_TOA_Downwelling[iWavelength]
				U_g[iWavelength][isigma][iopt][itheta][iPhi][iThetaV]=\
				   np.pi*U_TOA_Glint[iPhi][iThetaV][iWavelength]/         \
				   Irradiance_TOA_Downwelling[iWavelength]

########## postprocessing functions section ends here ##########


# Specify instrument_label first before postprocessing

instrument_label = input("instrument_label=?, enter 1 for OCI, 2 for MODIS, 3 for SeaWifs, 4 for MISR: ")
print ("You entered " + instrument_label)

instrument_label=int(instrument_label)  # 1: OCI table 2: MODIS A 3: SeaWifs

if instrument_label < 1 or instrument_label > 4 :
	sys.exit("Your instrument_label value is invalid")

Misr_Mie_Dir='MISR_MIE_DIR.txt'
SeaWifs_Mie_Dir='SEAWIFS_MIE_DIR.txt'
MODIS_Mie_Dir='MODIS_MIE_DIR.txt'
OCI_Mie_Dir='OCI_MIE_DIR.txt'
AUX_Dir='auxiliary_directory'

### read in auxillary directory
with open(AUX_Dir, 'r') as file:
	Instrument_Settingdir = file.read().replace('\n', '')
	
if instrument_label == 1 :
	Instrument_Setting_Filename=Instrument_Settingdir+'/'+'afrt_input_oci.txt'
	nwv=239
	instrument_strbase='OCI'
	MIE_SCAT_Dir=OCI_Mie_Dir
	MIE_str_base='OCI'

elif instrument_label == 2 :
	Instrument_Setting_Filename=Instrument_Settingdir+'/'+'afrt_input_modisa.txt'
	nwv=17
#	wavelengths=np.array([4.12000e-01, 4.43000e-01, 4.69000e-01,4.88000e-01, \
#                          5.31000e-01, 5.47000e-01, 5.51000e-01, 5.55000e-01,\
#						  6.45000e-01, 6.67000e-01, 6.78000e-01, 7.48000e-01,\
#						  8.59000e-01, 8.69000e-01, 1.24000e-00, 1.64000e-00,\
#						  2.13000e-00 ],np.float32)
	instrument_strbase='MODISa'
	MIE_SCAT_Dir=MODIS_Mie_Dir
	MIE_str_base='MODIS'
elif instrument_label == 3 :
	Instrument_Setting_Filename=Instrument_Settingdir+'/'+'afrt_input_seawifs.txt'
	nwv=8
#	wavelengths=np.array([4.12000e-01,4.43000e-01,4.90000e-01,5.10000e-01,\
#                          5.55000e-01,6.70000e-01, 7.65000e-01,8.65000e-01],np.float32)
	instrument_strbase='SeaWifs'
	MIE_SCAT_Dir=SeaWifs_Mie_Dir
	MIE_str_base='SEAWIFS'
elif instrument_label == 4 :
	Instrument_Setting_Filename=Instrument_Settingdir+'/'+'rtsos_input_misr.txt'
	nwv=4
#	wavelengths=np.array([4.43000e-01,5.57000e-01,6.71000e-01,8.65000e-01],np.float32)
	instrument_strbase='Misr'
	MIE_SCAT_Dir=Misr_Mie_Dir
	MIE_str_base='MISR'

wavelengths=np.zeros(nwv)
with open(Instrument_Setting_Filename, 'r') as instrument_file:
    instrument_file.readline()
    for irec in range(len(wavelengths)):
        instrument_rec=instrument_file.readline()
        instrument_field=instrument_rec.split()
        wavelengths[irec]=float(instrument_field[1])

dirnamebase='Inputfile_Dir_'+instrument_strbase

#IAEROSOL=1,21. 1-10 is Shettle and Fenn, 11-20 is Ahmad model, 21 dust aerosol model
Aerosol_Model=([11,12,13,14,15,16,17,18,19,20])
RH=np.array([0.3,0.50,0.70,0.75,0.80,0.85,0.90,0.95],np.float32) # Relative Humidity values shown the table above
#Aerosol_Model=([11])
#RH=np.array([0.3],np.float32) # Relative Humidity values shown the table above

RATIO_FINE_MODE_ZIA=np.array([0.0, 0.01, 0.02, 0.05, 0.1, 0.2,0.3, 0.5, 0.8, 0.95],np.float32)
tau865=np.array([0.00,0.05,0.10,0.15,0.20,0.25,0.30,0.40,0.50],np.float32)
theta0=np.array([ 0., 2., 4., 6., 8., 10., 12., 14., 16., 18., 20., 22., 24.,\
                 26., 28., 30., 32., 34., 36., 38., 40., 42., 44., 46., 48., \
                 50., 52., 54., 56., 58., 60., 62., 64., 66., 68., 70., \
                 72., 74., 76., 78., 80., 82., 84., 86., 88.],np.float32)
ThetaV=np.array([0., 2.282, 5.2363, 8.2037, 11.1683, 14.125, 17.0705,\
             20.0018, 22.9162, 25.8107, 28.6824, 31.5285, 34.3456, 37.1307,\
			 39.8804, 42.5912, 45.2595, 47.8813, 50.4528, 52.9697, 55.4276,\
			 57.8219, 60.1479, 62.4006, 64.5749, 66.6652, 68.6663, 70.5724,\
			  72.3778, 74.0767, 75.6633, 77.1319, 78.4769, 79.6929, 80.7746,\
			81.7174, 82.5169, 83.1692, 83.6712, 84.0205, 84.2152, 95.7848,\
			95.9795, 96.3288, 96.8308, 97.4831, 98.2826, 99.2254, 100.3071,\
			101.5231, 102.8681, 104.3367, 105.9233, 107.6222, 109.4276, \
			111.3337, 113.3348, 115.4251, 117.5994, 119.8521, 122.1781, \
			124.5724, 127.0303, 129.5472, 132.1187, 134.7405, 137.4088, \
			140.1196, 142.8693, 145.6544, 148.4715, 151.3176, 154.1893, \
			157.0838, 159.9982, 162.9295, 165.875, 168.8317, 171.7963,  \
			174.7637, 177.718,180.],np.float32)
PhiV=np.array([0.0, 5., 15.,  25.,  35.,  45.,  55.,  65.,  75.,  85.,  95., \
            105.,  115.,  125.,  135.,  145.,  155.,  165.,  175.,  180.],np.float32)

nthetav=int(ThetaV.size/2)

sigma = np.array([0, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4])
wndspd=np.empty(sigma.shape)
I_SURFACE_ROUGHNESS_PARA=2
if I_SURFACE_ROUGHNESS_PARA==1 :
#inverse wind speed from SIGMA^2=0.003D0+0.00512D0*WNDSPD Cox&Munk 1954
	wndspd=(np.square(sigma)-0.003)/0.00512
elif I_SURFACE_ROUGHNESS_PARA==2 :
# Gordon & Wang 1992
	wndspd=(np.square(sigma))/0.00534


for iaerosol, irh in itertools.product(range(len(Aerosol_Model)), range(len(RH))):
	dirname=dirnamebase+'AerosolModel%d' % Aerosol_Model[iaerosol] + 'rh_%f' % RH[irh]
	isdir = os.path.isdir(dirname)
	if not isdir :
		print('Warning, '+dirname+" does not exist")
		continue
	else :
		os.chdir(dirname)
		cwd = os.getcwd()
		print("Current working directory: {0}".format(cwd))
		if(not os.path.isfile(MIE_SCAT_Dir)) :
			print('Warning, '+MIE_SCAT_Dir+" does not exist")
			os.chdir('../')
			continue
			
		LUTDataPostProcessing(iaerosol,irh)
		os.chdir('../')


