#!/bin/csh -fe


#$ -l h_cpu=08:00:00
#$ -N FMS_idealize_spectral_grey_B
#$ -pe ic.alloc 32
#$ -o /home/df/sukyoung/exp_control
#$ -r n
#####

  set machine          = `hostname`

  set in               = $1 #this is the input from runjob and corresponds to the restart month

  set npes             = 8  #number of processes WARNING: can only use the restart files from 8 cpu's if restart was made from a run using 8 cps

  #begin personalisations for running at exeter:
  set exp_name          = seasonal_gray
  set workdir           = {{ workdir }}
  set base_arc          = {{ datadir }}
  set dir_base          = $GFDL_BASE
  set source_dir        = $dir_base/src
  set exp_dir           = $dir_base/exp/$exp_name
  set spin_up_restarts  = $dir_base/spin_up_restart/$exp_name/np$npes
  set core_namelist     = $exp_dir/core.nml       #dynamis namelist
  set phys_namelist     = $exp_dir/phys.nml       #physic namelist
  set diag_table        = $exp_dir/diag_table       #vars to output
  set field_table       = $exp_dir/field_table
  set compile_dir       = $dir_base/compilation_parallel  #compiled code location
  set executable        = $compile_dir/fms_moist.x      #compiled executable
  set path_names        = $exp_dir/path_names
  set make_flags        =                                                # set to -d for DEBUG messages
  set details_file      = $exp_dir/details.txt

  #run in serial or parallel?
  set run_gdb_parallel  = false     #default should be false
  set run_idb_serial  = false       #default should be false
  set run_mpi   = true              #default should be true
  set run_serial  = false           #default should be false
  set write_over_data   = true      #default should be false

  #MiMA options
  set ozone_nc_file     = ozone_1990.nc #default for test case should be ozone_1990.nc

set out = $in       #assign the input to output and add 1.
@ out ++
echo $out



#use restart files from spin_up
if ($out > 12) then
  #if true use experiment restarts else use the spin_up data
  set use_spin_up = false #s Means use_AS_spin_up, as in if $in > 12 then don't use the data as spin up, but if $in < 13 then DO use the data as spin up.
else
  #spin up scenario
    set use_spin_up = true
endif

if ($use_spin_up == true) then
  set arc = $spin_up_restarts
else
  set arc = $base_arc
endif


if ( ! -d $spin_up_restarts ) mkdir -p $spin_up_restarts
endif
if ( ! -d $base_arc ) mkdir -p $base_arc
endif
if ( ! -d $workdir ) mkdir -p $workdir
endif

# ************************************************************
#remove old files from within the working directory ->scratch
  echo blah >> $workdir/blah
  rm -rf $workdir/* >& /dev/null
# ************************************************************


#check if data already exists. Override data only when flag is true
if ( -d $arc'/run'$out ) then
  if ( $write_over_data == false) then
     echo 'file already exists for run'$out
     exit
  endif
endif

setenv MALLOC_CHECK_ 0

#if the compile folder does not exist make it
if ( ! -d $compile_dir ) mkdir -p $compile_dir
endif


if($do_compile == true) then

#mkmf flag info-
  #> make the Makefile from distributed source:
    # -a is the abspath (absolute path)
    # -p is the file to be made
    # -t is template location mkmf.no_opt.template.ia64 template (ifort compiler)
    # -c are cppDefs are "-Duse_libMPI -Duse_netCDF"
    #note that '\' is the escape character and is used in this context to continue reading next line as though there is no carrage return

  #final part of mkmf call (args): are a list of directories and files to be searched for targets and dependencies
  #path_name contains all the .f90 references (and their location within source_dir) needed to create the executable FMS.exe (flexible modelling system)
  #mpp for parallel computing, constant are standard earth constants, /usr/local/include is empty, $source_dir/include file for fms these are new files and are not
  #included in path_names and thus have been specified seperately.
  #see http://www.gfdl.noaa.gov/~vb/mkmf.html

  # JP [20/11/15]
  # Taken from https://github.com/tapios/fms-idealized runscripts
  # Prepend fortran files in srcmods directory to pathnames.
  # Use 'find' to make list of srcmod/*.f90 files. mkmf uses only the first instance of any file name.
  cd $source_dir
  find $exp_dir/srcmods/ -maxdepth 1 -iname "*.f90" -o -iname "*.inc" -o -iname "*.c" -o -iname "*.h" > $workdir/tmp_pathnames
  echo "Using the following sourcecode modifications:"
  cat $workdir/tmp_pathnames
  cat $path_names >> $workdir/tmp_pathnames


  if ($run_mpi == true) then
    echo "Run in parallel mode"
    $dir_base/bin/mkmf $make_flags -a $source_dir  -p fms_moist.x -t   $exp_dir/mkmf.template.ia64 \
    -c "-Duse_libMPI -Duse_netCDF -Duse_LARGEFILE -DINTERNAL_FILE_NML -DOVERLOAD_C8" $workdir/tmp_pathnames $source_dir/shared/mpp/include $source_dir/shared/constants $source_dir/include
    cp Makefile $compile_dir    #copy the mf
    cd $compile_dir
    make
  endif
  if ($run_idb_serial == true || $run_serial == true)   then #|| means logical or
    #only run in serial when debugging using idb
    echo "Run in serial mode"
    $dir_base/bin/mkmf $make_flags -a $source_dir  -p fms_moist.x -t   $exp_dir/mkmf.template.debug\
    -c "-Duse_netCDF" $workdir/tmp_pathnames $source_dir/shared/mpp/include $source_dir/shared/constants $source_dir/include
    cp Makefile $compile_dir
    cd $compile_dir
    make
 endif
endif
echo "Compilation done"


  cd $workdir
  mkdir INPUT RESTART

#EOF is a 'tag' where the shell will read in multiple lines until EOF occurs
#set the parameters for the namelist within the file input.nml
#convection is given 7200 is resolve i.e. 2 hours

cat > input.nml <<EOF
 &main_nml
     days   = 30,
     hours  = 0,
     minutes = 0,
     seconds = 0,
     dt_atmos = 900,
     current_date = 0001,1,1,0,0,0
     calendar = 'thirty_day'
EOF

# No restarts when $in=0 and it means start model from initial state
# Do not use the first year of runs (allow it to stabilise before looking at results)

# Create symbolic link from input ozone file to work directory, which is where the code expects to find such files.
ln -s $exp_dir/input/$ozone_nc_file $GFDL_WORK/$exp_name/np$npes/INPUT/$ozone_nc_file

if ($in > 0) then
  cd INPUT
  if ($in == 12) then
    cp $spin_up_restarts/restarts/res_$in.cpio res
  else
    cp $arc/restarts/res_$in.cpio res
  endif
  cpio -iv < res
endif


#if ($in > 13) then
# cp $arc/restarts/res_$in.cpio res
# cpio -iv < res
#endif

# JP [12/12/15] Add git commit details to file details.txt in the output directory
# get the HEAD git commit and add it to the details of the run
  cd $exp_dir
  set git_branch = `git symbolic-ref HEAD`
  echo Version Control: > $workdir/details.txt
  echo branch: $git_branch >> $workdir/details.txt
  git log -1 >> $workdir/details.txt
  echo >> $workdir/details.txt
  cat $details_file >> $workdir/details.txt


#join namelists into input.nml
  cd  $workdir
  cat $core_namelist >> input.nml
  cat $phys_namelist >> input.nml
  cp  $diag_table diag_table
  cp  $field_table field_table
  cp  $executable $executable:t
  cp  $path_names path_names.txt


#run and determine what type of machine the script is run on. npes->number of processes and $executable:t program name and arguments
if ($run_gdb_parallel == true) then
  ps ax | grep fms_moist.x
  mpirun -np $npes  xterm -e gdb $executable:t
#   mpirun -dgb=idb -np $npes  $executable:t
endif

if ($run_idb_serial == true) then
  idb -gdb $executable
#see manual  http://caligari.dartmouth.edu/doc/linux/idb_debugger_manual.htm#intro
endif

if ($run_serial == true) then
  $executable
endif

if ($run_mpi == true) then
  mpirun  -np $npes $executable:t
endif

#if using multiple processors then join the output files created into the file runX
  if ($npes > 1) then
     foreach ncfile (`/bin/ls *.nc.0000`) #ncfile = i, for each i(`/bin/ls *.nc.0000`)
        $dir_base/postprocessing/mppnccombine.x $ncfile:r
        if ($status == 0) rm -f $ncfile:r.????  #r.???? eg nc.0003
     end
  endif

if ( ! -d $arc/run$out ) mkdir $arc/run$out
endif
if ( ! -d $arc/restarts) mkdir $arc/restarts
endif

cp ./*.nc $arc/run$out/   #move the model output to archive

#  /bin/ls *.nc | cpio -ovK > nc_$out.cpio
#  cp nc_$out.cpio $arc/nc_$out.cpio

# #creates the new restart files res_X.cpio #s It would appear this is unecessary in 2013 FMS as new mppncombine.x does the restart part and the other nc file work in one move.
 cd RESTART
# if ($npes > 1) then
#     foreach ncfile (`/bin/ls *.nc.0000`)
#         $dir_base/postprocessing/mppnccombine.x $ncfile:r
#         if ($status == 0) rm -f $ncfile:r.????
#     end
# endif
 /bin/ls *.res *.res.nc | cpio -ov > res_$out.cpio  #compress the restart then copy from run location to data stroage location
cp res_$out.cpio $arc/restarts/

cd  $workdir
cp input.nml $arc #save the namelist record of the run
cp *.txt     $arc # move any text files to archive too

unset timestamp
#unset echo timestamp
