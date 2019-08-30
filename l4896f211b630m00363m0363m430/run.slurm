#! /bin/bash

#SBATCH --gres=gpu:4
#SBATCH -N 4
#SBATCH -p long
####### -C pascal
#SBATCH -A semibdff-19-20
#SBATCH -e stderrJob%jnode%n
#SBATCH -o stdoutJob%jnode%n
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

cd $HOME/allHISQ/l4896f211b630m00363m0363m430

# Take predefined parameters from qsub command line:
if [ -n "${SLURM_SUBMIT_DIR}" ]
then
  cd ${SLURM_SUBMIT_DIR}
  # Get job-dependent variables
  # Unpack lists
  # cfgs_milc=( `echo ${LATS} | sed 's|/| |g'` )
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
  LATS="x.99"
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
export OMP_NUM_THREADS=8
#export OMPI_MCA_btl=self,vader,tcp
export OMPI_MCA_btl_openib_connect_udcm_max_retry=1000

argList="${LATS} ${ncases} 1"
scriptList="../scripts/params-allHISQ-plus3.yaml ../scripts/params-launch.yaml params-ens.yaml params-machine.yaml"

echo "Removing any leftover correlators"
./purge_corrs.sh ${LATS} ${NCASES}

python ../scripts/make-allHISQ-prompts-NoHiddenSSD.py ${argList} ${scriptList}

if [ $? -ne 0 ]
then
    echo "Exiting because of errors in job"
    exit 1
else
    echo "Finished with status 0."
    exit 0
fi

