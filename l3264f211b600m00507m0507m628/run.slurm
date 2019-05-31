#! /bin/bash
# shell script for submitting to PBS
#
#SBATCH -p pigpu
#SBATCH --gres=gpu:4
####### -M zgelzer@illinois.edu
####### -m abe
####### -t (command line in spawnmultijob.py)
####### -N (command line in spawnmultijob.py)
####### -J (command line in spawnmultijob.py)
#SBATCH -A heavylight
#SBATCH -V

# Submission command must define environment variables LATS, NCASES
# sbatch -N ${NODES} -t ${walltime} -J ${jobname} ${slurm_script}

# LATS    list of cfg numbers, separated by /
# NCASES  number of cfg cases to run

umask 0022

module list

echo "Running on nodes"
echo $SLURM_JOB_NODELIST

cd $HOME/allHISQ/l3264f211b600m00507m0507m628/

export QUDA_RESOURCE_PATH=`pwd`
export QUDA_ENABLE_P2P=0   #Turn off P2P

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
  pbsjobid=test
  testing=1
  prompt=2
fi

argList="${cfgs_milc} ${ncases} 1"
scriptList="../scripts/params-allHISQ.yaml ../scripts/params-launch.yaml params-ens.yaml params-machine.yaml"

/usr/local/python2/bin/python2.7  ../scripts/make-allHISQ-prompts.py ${argList} ${scriptList}

if [ $? -ne 0 ]
then
    echo "Exiting because of errors in job"
    mv slurm-$SLURM_JOB_ID.out slurm-$SLURM_JOB_ID.fail
    exit 1
else
    rm slurm-$SLURM_JOB_ID.out
    exit 0
fi

