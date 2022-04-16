#! /bin/bash

#SBATCH -p normal
####### -A G-80204
#SBATCH -e stderrJob%jnode%n
#SBATCH -o stdoutJob%jnode%n
####### --qos=vippj_p1000
#SBATCH -V

# Submission command must define environment variables LATS, NCASES
# sbatch -n ${NODES} -t ${walltime} --jobname ${jobname} --mode script ${cobalt_script}
# --env LATS=${LATS}:NCASES=${NCASES}:NJOBS=${NJOBS}:NP=${N}

# LATS    list of cfg numbers, separated by /
# NCASES  number of cfg cases to run

umask 0022

nodes=128

export TACC_IBRUN_DEBUG=1

echo "Running with LATS $LATS and NCASES $NCASES"

# Take predefined parameters from qsub command line:
if [ -n "${SLURM_SUBMIT_DIR}" ]
then
  cd ${SLURM_SUBMIT_DIR}
  echo "Running on nodes"
  echo $SLURM_JOB_NODELIST
  # Get job-dependent variables
  # Unpack lists
  #  cfgs_milc=( `echo ${LATS} | sed 's|/| |g'` )
  cfgs_milc=${LATS}
  ncases=${NCASES}
  njobs=${NJOBS}
  pbsjobid=${SLURM_JOBID}
  if [ -z "${pbsjobid}" ]
  then
    pbsjobid=none
  fi
  testing=0
  prompt=0
else
  echo "Not a SLURM job.  Running in test mode."
  #cfgs_milc=(x.99)
  cfgs_milc="x.08/x.99"
  ncases=2
  njobs=1
  pbsjobid=test
  testing=1
  prompt=2
fi

#export KMP_AFFINITY="compact,granularity=fine,verbose"
#export KMP_PLACE_THREADS=54C,1T
export OMP_NUM_THREADS=14
export OMPI_MCA_btl_openib_connect_udcm_max_retry=1000
#export CRAY_OMP_CHECK_AFFINITY=TRUE
# export OMP_PROC_BIND=spread
# export OMP_PLACES=threads
#export THREADS_PER_CORE=1

# Suggested by Todd...
# export I_MPI_ADJUST_BCAST="1:16384-0"
# export I_MPI_WAIT_MODE=1
# export I_MPI_ADJUST_ALLTOALL=3 
# export I_MPI_OFA_DYNAMIC_QPS=0

# Suggested by Si Liu
#export I_MPI_STATS=10
#export I_MPI_STATS_FILE=mpi_profile_N2n2t56

argList="${cfgs_milc} ${ncases} ${njobs}"
scriptList="../scripts/params-allHISQ-plus4.yaml ../scripts/params-launch.yaml params-ens.yaml params-machine.yaml"

echo "Removing any leftover correlators"
./purge_corrs.sh ${LATS} ${NCASES} run1b

if [ $testing -eq 0 ]
then
    echo "Creating directories on all SSDs"
    ibrun ./make_ssd_dirs.sh ${LATS} ${NCASES}
fi

python3 ../scripts/make-allHISQ-prompts-NoHiddenSSD.py ${argList} ${scriptList}

if [ $? -ne 0 ]
then
    echo "Exiting because of errors in job"
    exit 1
else
    exit 0
fi

