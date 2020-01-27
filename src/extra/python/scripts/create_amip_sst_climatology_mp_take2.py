# create_amip_sst_climatology_mp.py creates a climatology based only on NH Jan-Jun and SH Jul - Dec data
# THIS script produces a climatology based on all months of data, but the result is a minimum at the equator in the annual mean, which is undesirable (see plot Code/Graphics/comp_sst_clims_blue_take2_red_older_annualmean.png and Code/Graphics/comp_sst_clims_blue_take2_red_older.png (which is for January)) --> the run /scratch/mp586/GFDL_BASE/GFDL_FORK/GFDLmoistModel/exp/ap_to_full/aquaplanet_calculate_qflux_and_qflux_runs_correct.py on gv1 uses the output from create_amip_sst_climatology_mp.py which is the red curve in those graphs. 


# what's happening in this routine? Take january entire earth and July entire earth flipped about equator, then concatinate (so append along lon axis) and calculate the zonal mean --> this gives 6 months of data. NH Jan = SH July, NH Feb = SH August ... but flipped about the equator. The resulting 6 months are then again flipped about the eqautor and concatenated, so that Jan = Jul flipped, Feb = August flipped ... 


# adapted from https://gist.github.com/guziy/8543562

from netCDF4 import Dataset
import numpy as np
import xarray as xr
from matplotlib import pyplot as plt
from scipy import interpolate


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
dsin = Dataset("/scratch/mp586/GFDL_BASE/GFDL_FORK/GFDLmoistModel/input/sst_clim_amip.nc")

#output file
dsout = Dataset("/scratch/mp586/GFDL_BASE/GFDL_FORK/GFDLmoistModel/input/sst_clim_amip_final.nc", "w", format="NETCDF3_CLASSIC") # This is to differentiate from _sqland, because that was NH SH symmetric in each month, not only in the annual mean! --> bug!

#Copy dimensions
for dname, the_dim in dsin.dimensions.iteritems():
    print dname, len(the_dim)
    dsout.createDimension(dname, len(the_dim) if not the_dim.isunlimited() else None)


# Copy variables
for v_name, varin in dsin.variables.iteritems():
    
    if v_name == 'sst_clim_amip':
        outVar = dsout.createVariable('sst_clim_amip_final', varin.datatype, varin.dimensions)
        print varin.datatype
    
        # Copy variable attributes
        outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})

	xrarray=xr.DataArray(varin[:])
        numlats=xrarray.shape[1]
        # Jan-Jun NH together with Jul - Dec SH
        whole_earth_6months = xr.concat((xrarray[0:6,:,:],xrarray[6:,::-1,:]),'dim_2','all', 'different','equals', None, None, None, None)
        zonal_mean = whole_earth_6months.mean('dim_2')
        
        twelve_months = xr.concat((zonal_mean,zonal_mean[:,::-1]),'dim_0','all', 'different','equals', None, None, None, None)
        a=np.expand_dims(twelve_months,axis=2)
        zonalmean_totalcoverage=np.repeat(a,360,axis=2)

        outVar[:] = np.asarray(zonalmean_totalcoverage)
        xr.DataArray(zonalmean_totalcoverage).mean('dim_0').plot()
        plt.show() # saved as amip_sst_NHSH_mean (_eqinterp) for the data interpolated cubically around 
        #equator, so that there is no minimum there, like in the NHSH mean file
        plt.close()

        check = xrarray.mean('dim_2')
        check=np.expand_dims(check,axis=2)
        check=np.repeat(check,360,axis=2)
        xr.DataArray(check).mean('dim_0').plot()
        plt.show() # saved as amip_sst_mean
        plt.close()
    else:
        
        outVar = dsout.createVariable(v_name, varin.datatype, varin.dimensions)
        print varin.datatype
    
        # Copy variable attributes
        outVar.setncatts({k: varin.getncattr(k) for k in varin.ncattrs()})
        outVar[:] = varin[:]





# close the output file
dsout.close()







