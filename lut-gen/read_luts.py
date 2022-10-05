# imports
import numpy as np
import xarray as xr
from tqdm.notebook import tqdm


instrument_label = input("instrument_label=?, enter 1 for OCI, 2 for MODIS, 3 for SeaWifs, 4 for MISR: ")

instrument_label=int(instrument_label)  # 1: OCI table 2: MODIS A 3: SeaWifs

if instrument_label < 1 or instrument_label >4 :
        sys.exit("Your instrument_label value is invalid")

if instrument_label == 1 :
        instrument_strbase='OCI'
elif instrument_label == 2 :
        instrument_strbase='MODISa'
elif instrument_label == 3 :
        instrument_strbase='SeaWifs'
elif instrument_label == 4 :
        instrument_strbase='Misr'

fpath = './'+instrument_strbase+'/rt_outputs/'

# arrays of the input parameters used in the runs
# coming from rt_GSFC_LUT_pre.py
Aerosol_Model=([11,12,13,14,15,16,17,18,19,20]) # aerosol model numbers named for Ahmad models according to pwz
RH=np.array([0.3,0.50,0.70,0.75,0.80,0.85,0.90,0.95]) # Relative Humidity values shown the table above
#Aerosol_Model=([19,20])
 
#Outputfile_Dir_MODISaAerosolModel11rh_0.300000

tau865=np.array([0.00,0.05,0.10,0.15,0.20,0.25,0.30,0.40,0.50]) # optical depth array from rt_GSFC_LUT_pre.py
theta0=np.array([ 0., 2., 4., 6., 8., 10., 12., 14., 16., 18., 20., 22., 24., \
                                  26., 28., 30., 32., 34., 36., 38., 40., 42., 44., 46., 48., \
                                  50., 52., 54., 56., 58., 60., 62., 64., 66., 68., 70., \
                                  72., 74., 76., 78., 80., 82., 84., 86., 88.]) # solz array from rt_GSFC_LUT_pre.py

sigma = np.array([0, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]) # wave slope array from rt_GSFC_LUT_pre.py
thetav = np.array([  0.    ,   2.282 ,   5.2363,   8.2037,  11.1683,  14.125 ,  17.0705,
        20.0018,  22.9162,  25.8107,  28.6824,  31.5285,  34.3456,  37.1307,
        39.8804,  42.5912,  45.2595,  47.8813,  50.4528,  52.9697,  55.4276,
        57.8219,  60.1479,  62.4006,  64.5749,  66.6652,  68.6663,  70.5724,
        72.3778,  74.0767,  75.6633,  77.1319,  78.4769,  79.6929,  80.7746,
        81.7174,  82.5169,  83.1692,  83.6712,  84.0205,  84.2152]) # senz array from rt_GSFC_LUT_pre.py

phi = np.array([  0.,   5.,  15.,  25.,  35.,  45.,  55.,  65.,  75.,  85.,  95., 105.,
       115., 125., 135., 145., 155., 165., 175., 180.])  # relaz array from rt_GSFC_LUT_pre.py

#wave = 1000*np.array([0.412, 0.443, 0.469, 0.488, 0.531, 0.547, 0.551, 0.555, 0.645, 0.667,
#       0.678, 0.748, 0.859, 0.869, 1.24 , 1.64 , 2.13 ])

wave = xr.open_dataset(fpath+'output_' + instrument_strbase + 'LUT_iaerosol16rh_0.300000sigma_00.40theta0_68.00tau865_00.00.h5', engine='netcdf4').WaveLength.values
#Aerosol_Model=[11]
#RH = [0.3]
len_phi = 20
len_thetav = 41
len_wave = 239 #17
print('Allocating memory...')
try:
    Lt = np.nan+np.empty((len(Aerosol_Model), len(RH), len(sigma), len(theta0), len(tau865), len_phi, len_thetav, len_wave),dtype='float32')
    LQ = np.nan+np.empty((len(Aerosol_Model), len(RH), len(sigma), len(theta0), len(tau865), len_phi, len_thetav, len_wave),dtype='float32')
    LU = np.nan+np.empty((len(Aerosol_Model), len(RH), len(sigma), len(theta0), len(tau865), len_phi, len_thetav, len_wave),dtype='float32')
    TLg = np.nan+np.empty((len(Aerosol_Model), len(RH), len(sigma), len(theta0), len(tau865), len_phi, len_thetav, len_wave),dtype='float32')
    TQg = np.nan+np.empty((len(Aerosol_Model), len(RH), len(sigma), len(theta0), len(tau865), len_phi, len_thetav, len_wave),dtype='float32')
    TUg = np.nan+np.empty((len(Aerosol_Model), len(RH), len(sigma), len(theta0), len(tau865), len_phi, len_thetav, len_wave),dtype='float32')
    diff_irrad = np.nan+np.empty((len(Aerosol_Model), len(RH), len(sigma), len(theta0), len(tau865), len(wave)),dtype='float32')
    aot = np.nan+np.empty((len(Aerosol_Model), len(RH), len(tau865), len(wave)),dtype='float32')
    rot = np.nan+np.empty((len(Aerosol_Model), len(RH), len(tau865), len(wave)),dtype='float32')
    depol = np.nan+np.empty((len(Aerosol_Model), len(RH), len(tau865), len(wave)),dtype='float32')
    LT_TOA = np.nan+np.empty((len(Aerosol_Model), len(RH), len(sigma), len(tau865), len_phi, len_thetav, len(wave)),dtype='float32')
    LT_BOA = np.nan+np.empty((len(Aerosol_Model), len(RH), len(sigma), len(tau865), len_phi, len_thetav, len(wave)),dtype='float32')
except:
    Lt = np.memmap('Lt_tmp', mode='w+', shape= (len(Aerosol_Model), len(RH), len(sigma), len(theta0), len(tau865), len_phi, len_thetav, len_wave),dtype='float32')
    LQ = np.memmap('LQ_tmp', mode='w+', shape= (len(Aerosol_Model), len(RH), len(sigma), len(theta0), len(tau865), len_phi, len_thetav, len_wave),dtype='float32')
    LU = np.memmap('LU_tmp', mode='w+', shape= (len(Aerosol_Model), len(RH), len(sigma), len(theta0), len(tau865), len_phi, len_thetav, len_wave),dtype='float32')
    TLg = np.memmap('TLg_tmp', mode='w+', shape= (len(Aerosol_Model), len(RH), len(sigma), len(theta0), len(tau865), len_phi, len_thetav, len_wave),dtype='float32')
    TQg = np.memmap('TQg_tmp', mode='w+', shape= (len(Aerosol_Model), len(RH), len(sigma), len(theta0), len(tau865), len_phi, len_thetav, len_wave),dtype='float32')
    TUg = np.memmap('TUg_tmp', mode='w+', shape= (len(Aerosol_Model), len(RH), len(sigma), len(theta0), len(tau865), len_phi, len_thetav, len_wave),dtype='float32')
    diff_irrad = np.memmap('diff_irrad_tmp', mode='w+', shape= (len(Aerosol_Model), len(RH), len(sigma), len(theta0), len(tau865), len(wave)),dtype='float32')
    aot = np.memmap('aot_tmp', mode='w+', shape= (len(Aerosol_Model), len(RH), len(tau865), len(wave)),dtype='float32')
    rot = np.memmap('rot_tmp', mode='w+', shape= (len(Aerosol_Model), len(RH), len(tau865), len(wave)),dtype='float32')
    depol = np.memmap('depol_tmp', mode='w+', shape= (len(Aerosol_Model), len(RH), len(tau865), len(wave)),dtype='float32')
    LT_TOA = np.memmap('LT_TOA_tmp', mode='w+', shape= (len(Aerosol_Model), len(RH), len(sigma), len(tau865), len_phi, len_thetav, len(wave)),dtype='float32')
    LT_BOA = np.memmap('Lt_BOA_tmp', mode='w+', shape= (len(Aerosol_Model), len(RH), len(sigma), len(tau865), len_phi, len_thetav, len(wave)),dtype='float32')
    
print('starting loops')
for imdl, mdl in tqdm(enumerate(Aerosol_Model)):
    for irh, rh in enumerate(RH):
        #fpath = 'Outputfile_Dir_MODISaAerosolModel%d'%Aerosol_Model[imdl]+'rh_%0f_2/'%RH[irh]
        #print('Rading path %s' %fpath) 
        #fpath = './'+instrument_strbase+'/rt_outputs/'
        for isig, sig in enumerate(sigma):
            for itheta, theta in enumerate(theta0):
                for iopt, opt in enumerate(tau865):
                    #print(imdl, irh, isig, itheta, iopt)
                    fname = 'output_'+instrument_strbase+'LUT_iaerosol%d'%Aerosol_Model[imdl]+'rh_%0f'%RH[irh]+\
                     'sigma_%05.2f'%sigma[isig]+'theta0_%05.2f' %theta0[itheta] + 'tau865_%05.2f' % tau865[iopt] + '.h5'
                    fnameDiff = 'output_'+instrument_strbase+'DiffuseT_iaerosol%d'%Aerosol_Model[imdl]+'rh_%0f'%RH[irh]+\
                     'sigma_%05.2f'%sigma[isig]+ 'tau865_%05.2f' % tau865[iopt] + '.h5'
                    try:
                        data = xr.open_dataset(fpath+fname, engine='netcdf4')
                        Lt[imdl,irh,isig,itheta,iopt, :, :, :] = data['Radiance_TOA'].values[:,:41,:]
                        LQ[imdl,irh,isig,itheta,iopt, :, :, :] = data['Q_TOA'].values[:,:41,:]
                        LU[imdl,irh,isig,itheta,iopt, :, :, :] = data['U_TOA'].values[:,:41,:]
                        TLg[imdl,irh,isig,itheta,iopt, :, :, :] = data['Radiance_TOA_Glint'].values[:,:41,:]
                        TQg[imdl,irh,isig,itheta,iopt, :, :, :] = data['Q_TOA_Glint'].values[:,:41,:]
                        TUg[imdl,irh,isig,itheta,iopt, :, :, :] = data['U_TOA_Glint'].values[:,:41,:]
                        aot[imdl,irh,iopt,:] = np.sum(data.Tau_Aerosol_Extinction,axis=0).values
                        rot[imdl,irh,iopt,:] = np.sum(data.Tau_Rayleigh_Extinction,axis=0).values
                        depol[imdl,irh,iopt,:] = np.mean(data.Rayleigh_Depolarization_Ratio,axis=0).values
                        diff_irrad[imdl,irh,isig,itheta,iopt, :] = data['Irrad_Down_TOA'].values
                    except FileNotFoundError:
                        print('File does not exist: %s' %fname)
                        Lt[imdl,irh,isig,itheta,iopt, :, :, :] = np.nan
                    try:
                        dataD = xr.open_dataset(fpath+fnameDiff, engine='netcdf4')
                        LT_TOA[imdl,irh,isig,iopt,:,:,:] = dataD['Radiance_TOA'].values[:,:41,:]
                        LT_BOA[imdl,irh,isig,iopt,:,:,:] = dataD['Radiance_BOA'].values[:,:41,:]
                    except FileNotFoundError:
                        #pass
                        print('File does not exist: %s' %fnameDiff)
        ds = xr.Dataset({"Lt": (('sigma', 'solz', 'tau865', 'relaz', 'senz', 'wavelength'), Lt[imdl,irh,:,:,:,:,:,:]),
            "TLg": (('sigma', 'solz', 'tau865', 'relaz', 'senz', 'wavelength'), TLg[imdl,irh,:,:,:,:,:,:]),
            "LQ": (('sigma', 'solz', 'tau865', 'relaz', 'senz', 'wavelength'), LQ[imdl,irh,:,:,:,:,:,:]),
            "LU": (('sigma', 'solz', 'tau865', 'relaz', 'senz', 'wavelength'), LU[imdl,irh,:,:,:,:,:,:]),
            "TQg": (('sigma', 'solz', 'tau865', 'relaz', 'senz', 'wavelength'), TQg[imdl,irh,:,:,:,:,:,:]),
            "TUg": (('sigma', 'solz', 'tau865', 'relaz', 'senz', 'wavelength'), TUg[imdl,irh,:,:,:,:,:,:]),
            "diff_irrad": (('sigma', 'solz', 'tau865',  'wavelength'), diff_irrad[imdl,irh,:,:,:,:]),
            'aot': (('tau856','wavelength'), aot[imdl,irh,:,:]),
            'rot': (('tau856','wavelength'), rot[imdl,irh,:,:]),
            'depol': (('tau856','wavelength'), depol[imdl,irh,:,:]),
            'LT_TOA': (('sigma', 'tau865', 'relaz', 'senz', 'wavelength'), LT_TOA[imdl,irh,:,:,:,:,:]),
            'LT_BOA': (('sigma', 'tau865', 'relaz', 'senz', 'wavelength'), LT_BOA[imdl,irh,:,:,:,:,:])}, 
            coords={
                    'AerosolModel': [mdl],
                    'RelativeHumidity' : [rh],
                    "sigma": sigma,
                    "solz": theta0,
                    "tau865": tau865,
                    'relaz': phi,
                    'senz': thetav,
                    'wavelength': wave
                    },)
            #{'aot': (('tau856','wavelength'), aot[imdl,irh,:,:])},coords={'tau865':tau865,'wavelength':wave},)
        print('saved... ' + instrument_strbase + '_rhot_iaerosol%d'%Aerosol_Model[imdl]+'rh%0f'%RH[irh]+'.nc')    
        ds.to_netcdf(instrument_strbase + '_rhot_iaerosol%d'%Aerosol_Model[imdl]+'rh%0f'%RH[irh]+'.nc')


#print(data)
