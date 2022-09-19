import numpy as np
import xarray as xr
from tqdm.notebook import tqdm
from scipy.interpolate import interp1d

Aerosol_Model=([11,12,13,14,15,16,17,18,19,20])
RH=np.array([0.3,0.50,0.70,0.75,0.80,0.85,0.90,0.95]) # Relative Humidity values shown the table above
fmf = ['00', '01', '02', '05', '10', '20', '30', '50', '80', '95']
sigma = np.array([0, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4])
isig = 0

sd = np.array([25, 24, 23, 22, 21, 20, 19, 18, 17, 16], dtype=np.int16)

print('starting loops')
for imdl, mdl in tqdm(enumerate(Aerosol_Model)):
    for irh, rh in enumerate(RH):
        fpath = ''
        data = xr.open_dataset(fpath+'rhot_iaerosol%d'%Aerosol_Model[imdl] +'rh%0f'%RH[irh] + '.nc')
        itau = 0 # that's for aot=0 which means Rayleigh only atmosphere
        # here we remove the TOA glint from rhot
        rhot = np.pi*data.Lt[:,:,itau,:,:,:]/data.diff_irrad[:,:,itau,:]
        Trhog = np.pi*data.TLg[:,:,itau,:,:,:]/data.diff_irrad[:,:,itau,:]
        rhor = rhot - Trhog

        rhot_all = np.pi*data.Lt[:,:,1:,:,:,:]/data.diff_irrad[:,:,1:,:]
        Trhog_all = np.pi*data.TLg[:,:,1:,:,:,:]/data.diff_irrad[:,:,1:,:]

        rhoa = rhot_all - rhor - Trhog_all
        rhoa = rhoa[isig,:,:,:,:]
        wave = data.wavelength.values
        coeffs = np.empty((5,45,20,41,17))
        for i in range(len(wave)):
            τ = np.log(data.aot[1:,i].values)
            if wave[i] <=800:
                A_poly = np.concatenate(([τ**0], [τ**1], [τ**2], [τ**3], [τ**4]))
            else:
                A_poly = np.concatenate(([τ**0], [τ**1], [τ**2], [0*τ**3], [0*τ**4]))
            B = np.reshape(np.moveaxis(rhoa.values, 1, 0)[:,:,:,:,i], (8, 45*20*41))
            B = np.log(B)
            C = np.linalg.pinv(A_poly).T@B
            coeffs[:,:,:,:,i] = C.reshape((5,45,20,41))

        ams_all = np.moveaxis(coeffs[0, :, :, :], 3, 0)
        bms_all = np.moveaxis(coeffs[1, :, :, :], 3, 0)
        cms_all = np.moveaxis(coeffs[2, :, :, :], 3, 0)
        dms_all = np.moveaxis(coeffs[3, :, :, :], 3, 0)
        ems_all = np.moveaxis(coeffs[4, :, :, :], 3, 0)

        td = data.LT_TOA/data.LT_BOA
        td = td[isig,:,10,:,:]  # arbitrary choice of phi index - no phi dependece in td
        B = np.empty((17,41))
        A = np.empty((17,41))
        for i in range(17):
        #     A_diff = 1/data2.aot[:,i].values
            τ = data.aot[:,i]
            A_diff = np.concatenate(([τ**0], [τ**1]))
            X = np.log(td[:,:,i].values)
            tmp = (np.linalg.pinv(A_diff).T@X)
            A[i,:] = np.exp(tmp[0,:])
            B[i,:] = -tmp[1,:]

        #remove 551
        wave = data.wavelength.values
        wave = np.concatenate((wave[:6], wave[7:]))
        ams_all = interp1d(data.wavelength, ams_all, axis=0)(wave)
        bms_all = interp1d(data.wavelength, bms_all, axis=0)(wave)
        cms_all = interp1d(data.wavelength, cms_all, axis=0)(wave)
        dms_all = interp1d(data.wavelength, dms_all, axis=0)(wave)
        ems_all = interp1d(data.wavelength, ems_all, axis=0)(wave)
        A = interp1d(data.wavelength, A, axis=0)(wave)
        B = interp1d(data.wavelength, B, axis=0)(wave)
        extc = (data.aot[1,:]/data.aot[1,13]).values
        extc = interp1d(data.wavelength, extc)(wave)
        ds = xr.Dataset({"ams_all": (('nwave','nsolz','nphi','nsenz'), ams_all.astype(np.float32)),
                         "bms_all": (('nwave','nsolz','nphi','nsenz'), bms_all.astype(np.float32)),
                         "cms_all": (('nwave','nsolz','nphi','nsenz'), cms_all.astype(np.float32)),
                         "dms_all": (('nwave','nsolz','nphi','nsenz'), dms_all.astype(np.float32)),
                         "ems_all": (('nwave','nsolz','nphi','nsenz'), ems_all.astype(np.float32)),
                         "dtran_a": (('dtran_nwave','dtran_ntheta'), A.astype(np.float32)),
                         "dtran_b": (('dtran_nwave','dtran_ntheta'), B.astype(np.float32)),
                         "extc": (('dtran_nwave'), extc.astype(np.float32))},
                    coords={
                    #'AerosolModel': [mdl],
                    #'AerosolFMF': [fmf[imdl]],
                    #'RelativeHumidity' : [rh],
                    #"nscatt": np.arange(0,180),
                    "solz": data.solz.values.astype(np.float32),
                    'phi': data.relaz.values.astype(np.float32),
                    'senz': data.senz.values.astype(np.float32),
                    'wave': wave.astype(np.float32),
                    'dtran_wave' : wave.astype(np.float32),
                    'dtran_theta' : data.senz.values.astype(np.float32)
                    }, attrs = {'AerosolModel': str(mdl), 'AerosolFMF': int(fmf[imdl]),
                        'RelativeHumidity' : rh, 'Size Distribution': sd[imdl],  'sigma': sigma[isig]})
        ds.to_netcdf('aerosol_modisa_r%d'%(rh*100)+'f%s'%fmf[imdl]+'v01.nc')
        print('saved... ' + 'aerosol_modisa_r%d'%(rh*100)+'f%s'%fmf[imdl]+'v01.nc')


