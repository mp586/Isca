# zonal mean of amip sst climatology (still has NH/SH asymmetry)
# use for zonally symmetric full continents exp. 


# adapted from https://gist.github.com/guziy/8543562

from netCDF4 import Dataset
import numpy as np
import xarray as xr
from matplotlib import pyplot as plt
from scipy import interpolate
from isca import GFDL_BASE
import os

# adapted from https://stackoverflow.com/questions/6518811/interpolate-nan-values-in-a-numpy-array
def fill_nan(A):
          '''
          interpolate to fill nan values
          '''
          inds = np.arange(A.shape[0])
          good = np.where(np.isfinite(A))
          f = interpolate.interp1d(inds[good], A[good],kind='cubic',bounds_error=False)
      
          B = np.where(np.isfinite(A),A,f(inds))
          return B




#input file
dsin = Dataset(os.path.join(GFDL_BASE,'input/sst_clim_amip.nc'))

#output file
dsout = Dataset(os.path.join(GFDL_BASE,"input/sst_amip_zonalsymm_perpeqnox.nc"), "w", format="NETCDF3_CLASSIC")
#Copy dimensions
for dname, the_dim in dsin.dimensions.iteritems():
    print dname, len(the_dim)
    dsout.createDimension(dname, len(the_dim) if not the_dim.isunlimited() else None)


# Copy variables
for v_name, varin in dsin.variables.iteritems():
    if v_name == 'sst_clim_amip':
        outVar = dsout.createVariable('sst_amip_zonalsymm_perpeqnox', varin.datatype, varin.dimensions)
        print varin.datatype
    
        # Copy variable attributes
        outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})

        xrarray = xr.DataArray(varin[:])
        zonalmean = xrarray.mean('dim_2')
        zonalmean_totalcoverage = np.expand_dims(zonalmean,axis = 2)
        zonalmean_totalcoverage = np.repeat(zonalmean_totalcoverage, 360, axis = 2)
        shoulder_seasons = np.empty((6,np.shape(varin[0,:,:])[0], np.shape(varin[0,:,:])[1]), type(zonalmean_totalcoverage))
        shoulder_seasons[0:3,:,:] = zonalmean_totalcoverage[1:4,:,:]
        shoulder_seasons[3:6,:,:] = zonalmean_totalcoverage[7:10,:,:]
        shoulder_seasons = xr.DataArray(shoulder_seasons)
        equinoxavg = shoulder_seasons.mean('dim_0')
        out_ssts = np.empty_like(zonalmean_totalcoverage)
        for i in range(12):
          out_ssts[i,:,:] = equinoxavg

        outVar[:] = np.asarray(out_ssts)

        xr.DataArray(out_ssts).mean('dim_0').plot()
        plt.show()
        plt.close()

    else:
        
        outVar = dsout.createVariable(v_name, varin.datatype, varin.dimensions)
        print varin.datatype
    
        # Copy variable attributes
        outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})
        outVar[:] = varin[:]





# close the output file
dsout.close()








