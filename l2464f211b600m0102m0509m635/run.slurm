#! /bin/bash

#SBATCH --gres=gpu:2
#SBATCH -N 2
#SBATCH -p long
#SBATCH -C pascal
#SBATCH -A semibdff-18-19
#SBATCH -V

# Submission command must define environment variables LATS, NCASES
# sbatch -N ${NODES} -t ${walltime} -J ${jobname} ${slurm_script}

# LATS    list of cfg numbers, separated by /
# NCASES  number of cfg cases to run

umask 0022

echo "Running on nodes"
echo $SLURM_JOB_NODELIST

# Job environment
source ${HOME}/bin/load_modules.sh

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

# location of QUDA tunecache file
export QUDA_RESOURCE_PATH=${SLURM_SUBMIT_DIR}

argList="${cfgs_milc} ${ncases} 1"
scriptList="../scripts/params-allHISQ-plus.yaml ../scripts/params-launch.yaml params-ens.yaml params-machine.yaml"

python ../scripts/make-allHISQ-prompts.py ${argList} ${scriptList}

if [ $? -ne 0 ]
then
    echo "Exiting because of errors in job"
    exit 1
else
    exit 0
fi

