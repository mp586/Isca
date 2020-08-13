# adapted from https://gist.github.com/guziy/8543562 
# for copying variable attributes from invar to outvar

# This script calculates a symmetric ocean heat transport from the 
# ocean q flux resulting from the script '/GFDL_BASE/stephen/calculate_qflux_aquaplanet.py
# The symmetry is such that Jan is the same as July but flipped about the Equator, 
# Feb is the same as August and so on. Not calculating a zonal mean here, because it is
# not zonally homogeneous. Instead, each grid point is matched with its partner from the 
# flipped array and the mean calculated (see the for loop)


from netCDF4 import Dataset
import numpy as np
import xarray as xr
from matplotlib import pyplot as plt
from scipy import interpolate
import os 
GFDL_BASE        = os.environ['GFDL_BASE']

#input file
dsin = Dataset(GFDL_BASE+'/exp/mp586/aquaplanet/input/ocean_qflux_finalAPqflux_isca_almostsymm.nc')

#output file
dsout = Dataset(GFDL_BASE+'/exp/mp586/aquaplanet/input/ocean_qflux_finalAPqflux_isca_symm.nc', "w", format="NETCDF3_CLASSIC")

#Copy dimensions
for dname, the_dim in dsin.dimensions.iteritems():
    print dname, len(the_dim)
    dsout.createDimension(dname, len(the_dim) if not the_dim.isunlimited() else None)


# Copy variables
for v_name, varin in dsin.variables.iteritems():
    
    if v_name == 'ocean_qflux':
        outVar = dsout.createVariable('ocean_qflux', varin.datatype, varin.dimensions)
        print varin.datatype
    
        # Copy variable attributes
        outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})



	xrarray=xr.DataArray(varin[:])
#        numlats=xrarray.shape[1]
        NHSHavg=np.empty_like(xrarray[0:6,:,:])

        for j in range (0,6):             
            NHSHavg[j,:,:] = (xrarray[j,:,:] + xrarray[j+6,::-1,:])/2.

        NHSHavg = xr.DataArray(NHSHavg)
        NHSHavg.mean('dim_0').plot()
        plt.show()

        twelve_months =  xr.concat((NHSHavg,NHSHavg[:,::-1,:]),'dim_0','all', 'different',
                                   'equals', None, None, None, None)

        outVar[:] = np.asarray(twelve_months)
        xr.DataArray(twelve_months).mean('dim_0').plot()

        xrarray.mean('dim_0').plot()
        plt.show() 

    else:        
        outVar = dsout.createVariable(v_name, varin.datatype, varin.dimensions)
        print varin.datatype
    
        # Copy variable attributes
        outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})
        outVar[:] = varin[:]

# close the output file
dsout.close()









