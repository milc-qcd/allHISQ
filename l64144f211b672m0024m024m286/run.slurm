#! /bin/bash

####### -t (command line in spawnmultijob.py)
####### -N (command line in spawnmultijob.py)
#SBATCH -q regular
####### -J (command line in spawnmultijob.py)
#SBATCH -C knl
#SBATCH -S 4
#SBATCH -A mp13
#SBATCH -V
#DW jobdw capacity=16000GB access_mode=striped type=scratch

# Submission command must define environment variables LATS, NCASES
# sbatch -N ${NODES} -t ${walltime} -J ${jobname} ${slurm_script}

# LATS    list of cfg numbers, separated by /
# NCASES  number of cfg cases to run

umask 0022

echo "`date` Running on nodes"
echo $SLURM_JOB_NODELIST

echo "Running with LATS $LATS, NCASES $NCASES, and NJOBS $NJOBS"

# Take predefined parameters from qsub command line:
if [ -n "${SLURM_SUBMIT_DIR}" ]
then
  # Run production jobs out of $CSCRATCH
  ./setup_rsync.sh    
  cd $CSCRATCH/allHISQ/scratch/l64144f211b672m0024m024m286
  export PYTHONPATH="../scripts/:${PYTHONPATH}"
  pbsjobid=${SLURM_JOBID}
  if [ -z "${pbsjobid}" ]
  then
    pbsjobid=none
  fi
  testing=0
  prompt=0
else
  echo "Not a SLURM job.  Running in test mode."
  LATS="x.8/x.10/x.12/x.14/x.16/x.18"
  NCASES=6
  NJOBS=6
  pbsjobid=test
  testing=1
  prompt=2
fi
ncases=${NCASES}
cfgs_milc=${LATS}
njobs=${NJOBS}

export OMP_NUM_THREADS=4
#export OMPI_MCA_btl=self,vader,tcp
export OMPI_MCA_btl_openib_connect_udcm_max_retry=1000
export PMI_MMAP_SYNC_WAIT_TIME=600

argList="${cfgs_milc} ${ncases} ${njobs}"
scriptList="../scripts/params-allHISQ-plus4.yaml ../scripts/params-launch.yaml params-ens.yaml params-machine.yaml"

echo "`date` Removing any leftover correlators"
#./purge_corrs2.sh ${LATS} ${NCASES} run3c

if [ $testing -ne 1 ]
then
    echo "`date` Broadcasting the executable"
    sbcast ../bin/ks_spectrum_hisq /tmp/ks_spectrum_hisq
    ls -l /tmp/ks_spectrum_hisq
fi

echo "`date` Running the job script:"
echo "python ../scripts/make-allHISQ-prompts-NoHiddenSSD.py ${argList} ${scriptList}"

python ../scripts/make-allHISQ-prompts-NoHiddenSSD.py ${argList} ${scriptList}

if [ $? -ne 0 ]
then
    echo "`date` Exiting because of errors in job"
    exit 1
else
#    echo "Cleaning up symlinks."
#    ./purge_symlinks.sh ${pbsjobid}
    exit 0
fi

