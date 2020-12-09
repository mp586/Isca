Diagnostics Manager Module
==============

Summary
-------

This module handles the writing of diagnostic output (anything from scalar to 3D arrays) to netCDF files. The user can specify which fields should be output and at which temporal resolution (e.g. monthly means, daily means ... ). The source code is located at ``src/shared/diag_manager/diag_manager.F90`` . 


Namelist options
----------------

.. .. or ``src/shared/diag_manager/diag_data.F90`` ???

+--------------------------------+----------+-----------------------------------------------------------------------------------------+
| Name                           | Default  | Description                                                                             |
+================================+==========+=========================================================================================+
|``append_pelist_name``          | False    |                                                                                         |
|                                |          |                                                                                         |
+--------------------------------+----------+-----------------------------------------------------------------------------------------+
|``mix_snapshot_average_fields`` | False    |                                                                                         |
+--------------------------------+----------+-----------------------------------------------------------------------------------------+
|``max_files``                   | 31       | Sets the maximum number of output files allowed                                         |
+--------------------------------+----------+-----------------------------------------------------------------------------------------+
|``max_output_fields``           | 300      | Sets the maximum number of output fields allowed                                        |
+--------------------------------+----------+-----------------------------------------------------------------------------------------+
|``max_input_fields``            | 300      | Sets the maximum number of input fields allowed                                         |
+--------------------------------+----------+-----------------------------------------------------------------------------------------+
|``max_axes``                    | 60       | Sets the maximum number of independent axes                                             |
+--------------------------------+----------+-----------------------------------------------------------------------------------------+
|``do_diag_field_log``           | False    |                                                                                         |
+--------------------------------+----------+-----------------------------------------------------------------------------------------+
|``write_bytes_in_files``        | False    |                                                                                         |
+--------------------------------+----------+-----------------------------------------------------------------------------------------+
|``debug_diag_manager``          | False    |                                                                                         |
+--------------------------------+----------+-----------------------------------------------------------------------------------------+
|``max_num_axis_sets``           | 25       |                                                                                         |
+--------------------------------+----------+-----------------------------------------------------------------------------------------+
|``use_cmor``                    | False    |                                                                                         |
+--------------------------------+----------+-----------------------------------------------------------------------------------------+
|``issue_oor_warnings``          | True     | If ``True`` check for values outside the valid range. This range is passed to the       |
|                                |          | ``diag_manager_mod`` via the OPTIONAL variable range in the                             |
|                                |          | ``register_diag_field`` function                                                        |
+--------------------------------+----------+-----------------------------------------------------------------------------------------+
|``oor_warnings_fatal``          | True     | If ``True`` issue a fatal error if any values for the output field are outside the      |
|                                |          | given range                                                                             |
+--------------------------------+----------+-----------------------------------------------------------------------------------------+


Diagnostics
-----------
.. What diagnostics are available for this part of the code.

This part of the code does not have its own diagnostics, but rather handles the saving of all variables. See also ``/src/extra/python/isca/diagtable.py``

Output files 
^^^^^^^^^^^^

In order to save output in Isca, an output file is created first. Commonly used output timesteps include monthly, daily or hourly.

Create the output file `atmos_monthly' : 
``diag.add_file('atmos_monthly', 30, 'days', time_units='days')``

Alternatively (or in addition), output daily data with 
``diag.add_file('atmos_daily', 1, 'days', time_units='days')``

And/or e.g. 6-hourly data with
``diag.add_file('atmos_6_hourly', 6, 'hours', time_units='hours')``

Output fields
^^^^^^^^^^^^^

An output field is created via ``diag.add_field(module, name, time_avg, files)``

The default for ``time_avg`` = False, the default for ``files`` = None. 

``time_avg`` is usually set to True for most variables when an output field is defined.

If ``files`` = None, then the diagnostics will be saved to all of the given output files (in our example monthly, daily and 6h). 

An output file can be specified via e.g. ``files=['atmos_6_hourly']`` in 

``diag.add_field('dynamics', 'ucomp', time_avg=True, files=['atmos_6_hourly'])`` 

if 6h zonal winds shall be saved, but not monthly/daily or

``diag.add_field('atmosphere', 'precipitation', time_avg=True, files=['atmos_monthly'])`` 

if only monthly-mean precipitation shall be saved, but not 6h/daily



Below is a list of commonly saved diagnostics. See the relevant modules for an exhaustive list of available diagnostics. 

+--------------------------+----------------------+-------------------------+-----------------------------------------------------------------+
| Module                   | Name                 | Dimensions              | Description                                                     |
+==========================+======================+===========================================================================================+
| ``dynamics`` 			   | ``ps``  	 	      | (time, lat, lon) 		| surface pressure (:math:`Pa`)									  |
+--------------------------+----------------------+-------------------------+-----------------------------------------------------------------+
| ``dynamics`` 			   | ``bk`` 	          | (phalf) 				| vertical coordinate sigma values           					  |
+--------------------------+----------------------+-------------------------+-----------------------------------------------------------------+
| ``dynamics`` 			   | ``pk`` 	          | (phalf) 				| vertical coordinate pressure values (:math:`Pa`)				  |
+--------------------------+----------------------+-------------------------+-----------------------------------------------------------------+
| ``dynamics`` 			   | ``slp`` 	          | (time, lat, lon) 		| sea level pressure (:math:`Pa`)								  |
+--------------------------+----------------------+-------------------------+-----------------------------------------------------------------+
| ``dynamics`` 			   | ``height`` 	      | (time, pfull, lat, lon) | geopotential height at full model levels (:math:`m`)			  |
+--------------------------+----------------------+-------------------------+-----------------------------------------------------------------+
| ``dynamics`` 			   | ``zsurf`` 	          | (lat, lon) 				| geopotential height at the surface (:math:`m`)				  |
+--------------------------+----------------------+-------------------------+-----------------------------------------------------------------+
| ``dynamics`` 			   | ``u_comp`` 	      | (time, pfull, lat, lon) | zonal component of the horizontal winds (:math:`m/s`)			  |
+--------------------------+----------------------+-------------------------+-----------------------------------------------------------------+
| ``dynamics`` 			   | ``v_comp`` 	      | (time, pfull, lat, lon) | meridional component of the horizontal winds (:math:`m/s`)      |
+--------------------------+----------------------+-------------------------+-----------------------------------------------------------------+
| ``dynamics`` 			   | ``omega`` 	          | (time, pfull, lat, lon) | vertical velocity (:math:`Pa/s`)								  |
+--------------------------+----------------------+-------------------------+-----------------------------------------------------------------+
| ``dynamics`` 			   | ``sphum`` 	          | (time, pfull, lat, lon) | specific humidity (:math:`kg/kg`)								  |
+--------------------------+----------------------+-------------------------+-----------------------------------------------------------------+
| ``dynamics`` 			   | ``temp``	          | (time, pfull, lat, lon) | temperature (:math:`K`)										  |
+--------------------------+----------------------+-------------------------+-----------------------------------------------------------------+
| ``dynamics`` 			   | ``vor`` 	          | (time, pfull, lat, lon) | vorticity (:math:`1/s`)										  |
+--------------------------+----------------------+-------------------------+-----------------------------------------------------------------+
| ``dynamics`` 			   | ``div``	          | (time, pfull, lat, lon) | divergence (:math:`1/s`)										  |
+--------------------------+----------------------+-------------------------+-----------------------------------------------------------------+
| ``dynamics`` 			   | ``sphum_u`` 	      | (time, pfull, lat, lon) | specific humidity * u (:math:`kg/kg * m/s`)				  	  |
+--------------------------+----------------------+-------------------------+-----------------------------------------------------------------+
| ``dynamics`` 			   | ``sphum_v`` 	      | (time, pfull, lat, lon) | specific humidity * v (:math:`kg/kg * m/s`)				  	  |+--------------------------+----------------------+-------------------------+-----------------------------------------------------------------+
| ``dynamics`` 			   | ``sphum_w`` 	      | (time, pfull, lat, lon) | specific humidity * w (:math:`kg/kg * m/s`)				  	  |+--------------------------+----------------------+-------------------------+-----------------------------------------------------------------+


.. diag.add_field('atmosphere', 'precipitation', time_avg=True)
.. diag.add_field('atmosphere', 'bucket_depth', time_avg=True)
.. diag.add_field('atmosphere', 'bucket_depth_cond', time_avg=True)
.. diag.add_field('atmosphere', 'bucket_depth_conv', time_avg=True)
.. diag.add_field('atmosphere', 'bucket_depth_lh', time_avg=True)
.. diag.add_field('mixed_layer', 't_surf', time_avg=True)
.. diag.add_field('atmosphere', 'rh', time_avg=True) 
.. diag.add_field('rrtm_radiation', 'toa_sw',time_avg=True)
.. diag.add_field('rrtm_radiation', 'olr',time_avg=True)
.. diag.add_field('atmosphere', 'potential_evap', time_avg=True) 
.. diag.add_field('atmosphere', 'cape', time_avg=True) 
.. diag.add_field('rrtm_radiation', 'flux_sw', time_avg=True)
.. diag.add_field('rrtm_radiation', 'flux_lw', time_avg=True) 
.. diag.add_field('mixed_layer', 'flux_lhe', time_avg=True) 
.. diag.add_field('mixed_layer', 'flux_t', time_avg=True) 


Relevant modules and subroutines
--------------------------------

The ``diag_manager_mod`` uses several modules and subroutines, including 

``diag_axis``

``diag_grid``

``diag_output``

``diag_util``

``diag_data``

``diag_table``


.. References
.. ----------
.. ..
..    Add relevant references. This is done in 2 steps:
..    1. Add the reference itself to docs/source/references.rst
..    2. Insert the citation key here, e.g. [Vallis2017]_
   
..    See the Contributing guide for more info.

.. None

Authors
-------

This documentation was written by Marianne Pietschnig, peer reviewed by Stephen Thomson and quality controlled by Ross Castle. 
