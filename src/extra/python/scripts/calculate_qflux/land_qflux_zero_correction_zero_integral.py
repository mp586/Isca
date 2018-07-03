import numpy as np
import xarray as xr
from xarray import ufuncs as xruf
import time
from scipy import stats
from mpl_toolkits.basemap import shiftgrid
import matplotlib.pyplot as plt
import os

from netCDF4 import Dataset
import sys
sys.path.insert(0, '/scratch/mp586/Code/PYCODES')
# import plotting_routines
from plotting_routines_kav7 import area_weighted_avg
from plotting_routines_kav7 import area_integral

GFDL_BASE = os.environ['GFDL_BASE']
sys.path.insert(0, os.path.join(GFDL_BASE,'src/extra/python/scripts')) 
import cell_area as ca


landfile=Dataset(os.path.join(GFDL_BASE,'input/two_continents/land.nc'),mode='r')
# landfile=Dataset(os.path.join(GFDL_BASE,'input/squareland/land.nc'),mode='r')
# landfile=Dataset(os.path.join(GFDL_BASE,'input/sqland_plus_antarctica/land.nc'),mode='r')
# landfile=Dataset(os.path.join(GFDL_BASE,'input/aquaplanet/land.nc'),mode='r')
# landfile=Dataset(os.path.join(GFDL_BASE,'input/square_South_America/land.nc'))
# landfile=Dataset(os.path.join(GFDL_BASE,'input/square_Africa/land.nc'))
# landfile=Dataset(os.path.join(GFDL_BASE,'input/all_continents/land.nc'))

landmask=landfile.variables['land_mask'][:]

area_array = ca.cell_area(t_res=42,base_dir='/scratch/mp586/Isca/')
area_array = xr.DataArray(area_array)

#input file
dsin = Dataset(os.path.join(GFDL_BASE,'input/aquaplanet/isca_qflux/ocean_qflux.nc'))

#output file
dsout = Dataset(os.path.join(GFDL_BASE,'input/two_continents/isca_qflux/zero_integral/ocean_qflux.nc'), "w", format="NETCDF3_CLASSIC")

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

        qflux_in = varin[:]
        qflux_out = qflux_in[:]

        lats = dsin.variables['lat'][:]
        lons = dsin.variables['lon'][:]
        time = dsin.variables['time'][:]
	area_array = xr.DataArray(area_array, coords=[lats,lons], dims = ['lat','lon'])
        num_oceancells = (np.size(landmask) - np.count_nonzero(landmask))

        for i in range(0,12):
            qflux_i_init = qflux_in[i,:,:]
            qflux_i_init[landmask == 1.] = 0. # 2.0
            qflux_i_init = xr.DataArray(qflux_i_init, coords = [lats,lons], dims = ['lat','lon'])
            qflux_out[i,:,:] = qflux_i_init


        qflux_out = xr.DataArray(qflux_out,coords=[time,lats,lons],dims=['time','lat','lon'])
        meanq = qflux_out.mean('time')
        
        meanq_int = area_integral(meanq,area_array,landmask,'all_sfcs')# doesn't matter whether I put option all sfcs or ocean, because qflux is zero over ocean anyway

        q_int_invweight_landzero = (meanq_int * 1./(area_array.where(landmask==0.)))/num_oceancells
        q_int_invweight_landzero = xr.DataArray(q_int_invweight_landzero, coords = [lats,lons], dims = ['lat','lon'])

        correction_matrix = np.expand_dims(q_int_invweight_landzero,axis=0)
        correction_matrix = np.repeat(correction_matrix,12,axis=0) 
        correction_matrix = xr.DataArray(correction_matrix,coords=[time,lats,lons],dims=['time','lat','lon'])
        # the correction matrix is the same in every month, since the annual mean of a 12xlatxlon matrix of ones is a latxlon matrix of ones, so similarly if the ones are replaces by q_int_invweight_landzero

        print(area_integral(qflux_out.mean('time'),area_array,landmask,'all_sfcs') - area_integral(correction_matrix.mean('time'),area_array,landmask,'all_sfcs'))

        qflux_out = qflux_out - correction_matrix

        print(area_integral(qflux_out.mean('time'),area_array,landmask,'all_sfcs'))

        outVar[:] = np.asarray(qflux_out)

# NB: the two print statements above should show the same result in theory, but I think due to machine precision, they don't.... 


# make qflux_int zero in each month instead
# include this in the loop for i in range(0,12)
            # q_int = area_integral(qflux_i_init,area_array,landmask,'all_sfcs') # doesn't matter whether I put option all sfcs or ocean, because
            # # qflux is zero over ocean anyway
            # q_int_invweight_landzero = (q_int * 1./(area_array.where(landmask==0.)))/num_oceancells
            # q_int_invweight_landzero = xr.DataArray(q_int_invweight_landzero, coords = [lats,lons], dims = ['lat','lon'])
            # qflux_i = qflux_i_init - q_int_invweight_landzero
            # qflux_out[i,:,:] = qflux_i
            # print(i)
            # print(area_integral(qflux_i, area_array, landmask, 'all_sfcs')) # to check that global integral of corrected qflux is actually (close to) zero
            # print(area_weighted_avg(qflux_i, area_array, landmask, 'ocean')) 
            # if (i == 1) or (i == 2):
            #     (qflux_i_init - qflux_i).plot()
            #     plt.show()


    else:
        
        outVar = dsout.createVariable(v_name, varin.datatype, varin.dimensions)
        print varin.datatype
    
        # Copy variable attributes
        outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})
        outVar[:] = varin[:]

# close the output file
dsout.close()
