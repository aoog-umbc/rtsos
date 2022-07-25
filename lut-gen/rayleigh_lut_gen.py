#python imports
import numpy as np
import xarray as xr
from scipy.optimize import least_squares
from tqdm import tqdm

data = xr.open_dataset('rhot_iaerosol11rh0.300000.nc')

itau = 0 # that's for aot=0 which means Rayleigh only atmosphere

# convert radiance from PWZ outputs to reflectance
rhot = np.pi*data.Lt[:,:,itau,:,:,:]/data.diff_irrad[:,:,itau,:]
Trhog = np.pi*data.TLg[:,:,itau,:,:,:]/data.diff_irrad[:,:,itau,:]

rhoQ = np.pi*data.LQ[:,:,itau,:,:,:]/data.diff_irrad[:,:,itau,:]
TQg = np.pi*data.TQg[:,:,itau,:,:,:]/data.diff_irrad[:,:,itau,:]

rhoU = np.pi*data.LU[:,:,itau,:,:,:]/data.diff_irrad[:,:,itau,:]
TUg = np.pi*data.TUg[:,:,itau,:,:,:]/data.diff_irrad[:,:,itau,:]

# remove direct sun glint at TOA
rhor = rhot - Trhog
rhoQr = rhoQ - TQg
rhoUr = rhoU - TUg

# convert rhor to radiance for F0=1: rhor = pi*Lr/cos(solz)
# the rayleigh luts need radiance as an input for F0=1
Lr = rhor*np.cos(np.deg2rad(rhor.solz))/np.pi
Lqr = rhoQr*np.cos(np.deg2rad(rhoQ.solz))/np.pi
Lur = rhoUr*np.cos(np.deg2rad(rhoU.solz))/np.pi

ϕ = Lr.relaz.values
ϕrad = np.deg2rad(ϕ)

A_cos = np.concatenate(([np.cos(0*ϕrad)], [np.cos(ϕrad)], [np.cos(2*ϕrad)]))
A_sin = np.concatenate(([np.sin(0*ϕrad)], [np.sin(ϕrad)], [np.sin(2*ϕrad)]))

B_r = np.moveaxis(Lr.values, 2, 4).reshape((8*45*41*17,20))
B_q = np.moveaxis(Lqr.values, 2, 4).reshape((8*45*41*17,20))
B_u = np.moveaxis(Lur.values, 2, 4).reshape((8*45*41*17,20))

X_r = np.linalg.pinv(A_cos).T@B_r.T
X_r = X_r.reshape((3,8,45,41,17))
i_ray = np.moveaxis(X_r, 0, 2)

X_q = np.linalg.pinv(A_cos).T@B_q.T
X_q = X_q.reshape((3,8,45,41,17))
q_ray = np.moveaxis(X_q, 0, 2)

X_u = np.linalg.pinv(A_sin).T@B_u.T
X_u = X_u.reshape((3,8,45,41,17))
u_ray = np.moveaxis(X_u, 0, 2)

# cosine cost function for I and Q
#def cos_func(mcoeff, relaz, Lr):
#    phi = relaz*np.pi/180.0
#    return Lr - (mcoeff[0]*np.cos(0*phi)+ mcoeff[1]*np.cos(1*phi) + mcoeff[2]*np.cos(2*phi))

# sine cost function for U
#def sin_func(mcoeff, relaz, Lqu):
#    phi = relaz*np.pi/180.0
#    return Lqu - (mcoeff[0]*np.sin(1*phi) + mcoeff[1]*np.cos(2*phi))

# Allocate arrays in memory
#i_ray = np.empty((len(Lr.sigma), len(Lr.solz), 3, len(Lr.senz), len(Lr.wavelength)))
#q_ray = np.empty((len(Lr.sigma), len(Lr.solz), 3, len(Lr.senz), len(Lr.wavelength)))
#u_ray = np.empty((len(Lr.sigma), len(Lr.solz), 3, len(Lr.senz), len(Lr.wavelength)))
#mcoeff = np.array([0,0,0])

# loop over table dimensions to optimize for the fitting coeff mcoeff
#for i in tqdm(range(len(Lr.sigma))):
#    for j in tqdm(range(len(Lr.solz))):
#        for k in tqdm(range(len(Lr.senz))):
#            for l in range(len(Lr.wavelength)):
#                try:
#                    o = least_squares(cos_func, mcoeff, args=(Lr.relaz.values, Lr[i,j,:,k,l]))
#                    oq = least_squares(cos_func, mcoeff, args=(Lr.relaz.values, Lqr[i,j,:,k,l]))
#                    ou = least_squares(sin_func, mcoeff, args=(Lr.relaz.values, Lur[i,j,:,k,l]))
#                    i_ray[i,j,:,k,l] = o.x
#                    q_ray[i,j,:,k,l] = oq.x
#                    u_ray[i,j,:,k,l] = np.concatenate(([0.0], ou.x))
#                except ValueError:
#                    i_ray[i,j,:,k,l] = np.nan
#                    q_ray[i,j,:,k,l] = np.nan
#                    u_ray[i,j,:,k,l] = np.nan
#np.save('i_ray',i_ray)
#np.save('q_ray',q_ray)
#np.save('u_ray',u_ray)

# write rayleigh radiance coeffcients into netcdf files
wave = data.wavelength.values
for i in range(len(wave)):
    ds = xr.Dataset({
                     "taur" : (('nlambda'), [data.rot[itau,i].values.astype(np.float32)],\
                             {'long_name':'Optical Thickness', 'units':'dimensionless'}),
                     "depol": (('nlambda'), [data.depol[itau,i].values.astype(np.float32)],\
                             {'long_name':'Depolarization Factor', 'units':'dimensionless'}),
                     "senz" : (('nrad_ray'), rhor.senz.values.astype(np.float32),\
                             {'long_name':'Sensor Zenith Angles', 'units':'degrees'}),
                     "solz" : (('nsun_ray'), rhor.solz.values.astype(np.float32),\
                             {'long_name':'Solar Zenith Angles', 'units':'degrees'}),
                     "sigma": (('nwind_ray'), rhor.sigma.values.astype(np.float32),\
                             {'long_name':'Sigma of Wind Speed', 'units':'sqrt(m/s)'}),
                     "i_ray": (('nwind_ray', 'nsun_ray', 'norder_ray', 'nrad_ray'), i_ray[:,:,:,:,i].astype(np.float32),\
                             {'long_name':'Rayleigh radiance coefficients for I-component', 'units':'unitless'}),
                     "q_ray": (('nwind_ray', 'nsun_ray', 'norder_ray', 'nrad_ray'), q_ray[:,:,:,:,i].astype(np.float32),\
                             {'long_name':'Rayleigh radiance coefficients for Q-component', 'units':'unitless'}),
                     "u_ray": (('nwind_ray', 'nsun_ray', 'norder_ray', 'nrad_ray'), u_ray[:,:,:,:,i].astype(np.float32),\
                             {'long_name':'Rayleigh radiance coefficients for U-component', 'units':'unitless'})})
    ds.to_netcdf('rayleigh_modisa_%d_iqu.nc'%wave[i])
