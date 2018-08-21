import numpy as np
import xarray
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
from plotting_routines_kav7 import * # isca and gfdl have 0:04 and 0:03 

sys.path.insert(0, os.path.join(GFDL_BASE,'src/extra/python/scripts'))
import cell_area as ca
area_array = ca.cell_area(t_res=42,base_dir='/scratch/mp586/GFDL_BASE/GFDL_FORK/GFDLmoistModel/')
area_array = xr.DataArray(area_array)
GFDL_BASE = os.environ['GFDL_BASE']
GFDL_DATA = os.environ['GFDL_DATA']


ctl_model = input('Enter model name as string ')
if (ctl_model == 'Isca') or (ctl_model == 'isca'): 
    control_model = 'Isca_DATA'
elif (ctl_model == 'gfdl') or (ctl_model == 'GFDL'):
    control_model = 'GFDL_DATA'
control_dir= control_model + '/' + input('Enter control directory name as string ')
print control_dir
ctl_runmin=input('Enter runmin number ')  # Should be a January month for seasonal variables to be correct
ctl_runmax=input('Enter runmax number for comparison ')
ctl_timeseries_max = input('Enter end of ctl timeseries month ')

model = input('Enter model ')
if (model == 'Isca') or (model == 'isca'): 
    model_data = 'Isca_DATA'
elif (model == 'gfdl') or (model == 'GFDL'):
    model_data = 'GFDL_DATA'
testdir = input('Enter data directory name as string ')
runmin=input('Enter runmin number ')  # Should be a January month for seasonal variables to be correct
runmax=input('Enter runmax number ')
testdir = model_data + '/' + testdir

landmask_name = input('Which landmask? ')
landfile=Dataset(os.path.join(GFDL_BASE,'input/'+landmask_name+'/land.nc'),mode='r')
landmask=landfile.variables['land_mask'][:]
landlats=landfile.variables['lat'][:]
landlons=landfile.variables['lon'][:]

# for specified lats

landmaskxr=xr.DataArray(landmask,coords=[landlats,landlons],dims=['lat','lon']) # need this in order to use .sel(... slice) on it

# get sst climatology from chosen experiment

[tsurf,tsurf_avg,tsurf_seasonal_avg,tsurf_month_avg,time]=seasonal_surface_variable(testdir,model,runmin,runmax,'t_surf','K')
[tsurf_ctl,tsurf_avg_ctl,tsurf_seasonal_avg_ctl,tsurf_month_avg_ctl,time]=seasonal_surface_variable(control_dir,ctl_model,ctl_runmin,ctl_runmax,'t_surf','K')

i = 1
if model=='isca':
    runnr="{0:04}".format(i)
elif model=='gfdl':
	runnr="{0:03}".format(i)
filename = '/scratch/mp586/'+testdir+'/run'+runnr+'/atmos_monthly.nc'
nc = Dataset(filename,mode='r')




#input file
dsin = Dataset(os.path.join(GFDL_BASE,'input/sst_clim_amip.nc'))

#output file
# dsout = Dataset(os.path.join(GFDL_BASE,'input/'+landmask_name+'/prescribed_ssts_control.nc'), "w", format="NETCDF3_CLASSIC")
# for control, the input data directory was Isca/two_continents_newbucket_finalIscaAPqflux_landqfluxzero_zerointegral_with6hrly run 121-481
# for perturbed, the input data directory was Isca/two_continents_newbucket_finalIscaAPqflux_landqfluxzero_zerointegral_with6hrly_2xCO2_spinup_361 run 120-480

#dsout = Dataset(os.path.join(GFDL_BASE,'input/'+landmask_name+'/prescribed_ssts_perturbed.nc'), "w", format="NETCDF3_CLASSIC")

dsout = Dataset(os.path.join(GFDL_BASE,'input/'+landmask_name+'/prescribed_ssts_uniform.nc'), "w", format="NETCDF3_CLASSIC")



#Copy dimensions
for dname, the_dim in dsin.dimensions.iteritems():
    if (dname == 'lat') or (dname == 'lon') or (dname == 'latb') or (dname == 'lonb'):
        print dname
        dsout.createDimension(dname, len(nc.variables[dname][:]))
    else:
        print dname, len(the_dim)
        dsout.createDimension(dname, len(the_dim) if not the_dim.isunlimited() else None)


# Copy variables
for v_name, varin in dsin.variables.iteritems():
    
    if v_name == 'sst_clim_amip':
#        outVar = dsout.createVariable('prescribed_ssts_control', varin.datatype, varin.dimensions)
#        outVar = dsout.createVariable('prescribed_ssts_perturbed', varin.datatype, varin.dimensions)
        outVar = dsout.createVariable('prescribed_ssts_uniform', varin.datatype, varin.dimensions)

        print v_name, varin.datatype
    
        # Copy variable attributes
        outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})

        tsurf_in = varin[:]
        tsurf_out = tsurf_in[:]

        uniform_warming = area_weighted_avg(tsurf_avg - tsurf_avg_ctl, area_array, landmaskxr, 'ocean', minlat = -30., maxlat = 30.)

#        tsurf_out = tsurf_month_avg[:]

        tsurf_out = tsurf_month_avg_ctl[:] + uniform_warming
        print('Applying uniform warming of + '+str(uniform_warming)+' K to each month')
        
        outVar[:] = np.asarray(tsurf_out)

    elif v_name in ['lat','lon','latb','lonb']:

        outVar = dsout.createVariable(v_name, varin.datatype, varin.dimensions)
        print v_name, varin.datatype
    
        # Copy variable attributes
        outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})
        
        outVar[:] = np.asarray(nc.variables[v_name][:])        

    else:
        outVar = dsout.createVariable(v_name, varin.datatype, varin.dimensions)
        print v_name, varin.datatype
    
        # Copy variable attributes
        outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})
        outVar[:] = varin[:]

# close the output file
dsout.close()
