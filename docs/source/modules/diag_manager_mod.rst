Diagnostics Manager Module
==============

Summary
-------

This module handles the writing of diagnostic output (from scalar to 3D arrays) to netCDF files.


Namelist options
----------------

The ``diag_manager_mod`` namelist can be found at ``src/shared/diag_manager/diag_manager.F90`` 

.. or ``src/shared/diag_manager/diag_data.F90`` ???

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
|``conserve_water`               | True     | Undocumented namelist to control flushing of output files                               |
+--------------------------------+----------+-----------------------------------------------------------------------------------------+
.. not sure whether conserve water should be included, it is in diag_data.f90, but not in the original namelist of diag_manager.f90! 

Diagnostics
-----------
.. What diagnostics are available for this part of the code.


Relevant modules and subroutines
--------------------------------

The diagnostics manager module is located at ``src/shared/diag_manager/diag_manager.F90``. 


References
----------
..
   Add relevant references. This is done in 2 steps:
   1. Add the reference itself to docs/source/references.rst
   2. Insert the citation key here, e.g. [Vallis2017]_
   
   See the Contributing guide for more info.
