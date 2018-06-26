#! /bin/bash
# shell script for submitting to PBS
#
#SBATCH -p ember
####### -M detar@physics.utah.edu
####### -m abe
####### -t (command line in spawnmultijob.py)
####### -N (command line in spawnmultijob.py)
####### -J (command line in spawnmultijob.py)
#SBATCH -A detar
#SBATCH -V

# Submission command must define LATS, SOURCES, JOBIDS, NCASES
# sbatch -N ${NODES} -t ${walltime} -J ${jobname} LATS=${cfgnos},NCASES=${ncases} ${slurm_script}

# LATS    list of cfg numbers, separated by /
# NCASES  number of cfg cases to run

umask 0022

export LD_LIBRARY_PATH=/usr/local/ofed/lib64:/usr/local/fftw-3.3.7/mvapich2/lib:${LD_LIBRARY_PATH}:/usr/local/python2/lib:/usr/local/cuda/lib64

echo "Running on nodes"
echo $SLURM_JOB_NODELIST

cd $HOME/allHISQ/l2464f211b600m0102m0509m635/

# Take predefined parameters from qsub command line:
if [ -n "${SLURM_SUBMIT_DIR}" ]
then
  cd ${SLURM_SUBMIT_DIR}
  # Get job-dependent variables
  # Unpack lists
  cfgs_milc=( `echo ${LATS} | sed 's|/| |g'` )
  ncases=${NCASES}
  pbsjobid=${SLURM_JOBID}
  if [ -z "${pbsjobid}" ]
  then
    pbsjobid=none
  fi
  testing=0
  prompt=0
else
  echo "Not a SLURM job.  Running in test mode."
  cfgs_milc=(x.99)
  t0s=(0)
  jobids=("grp")
  ncases=1
  njobs=0
  pbsjobid=test
  testing=1
  prompt=2
fi

argList="${cfgs_milc} ${ncases} 1"
scriptList="../scripts/params-allHISQ.yaml ../scripts/params-launch.yaml params-ens.yaml params-machine.yaml"

/usr/bin/python2.7  ../scripts/make-allHISQ-prompts.py ${argList} ${scriptList}

if [ $? -ne 0 ]
then
    echo "Exiting because of errors in job"
    exit 1
else
    exit 0
fi

