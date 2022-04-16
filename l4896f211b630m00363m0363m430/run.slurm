#! /bin/bash

#SBATCH --gres=gpu:2
#SBATCH -N 4
#SBATCH -p long
####### -q scavenger
#SBATCH -C pascal
#SBATCH -A semibdff-20-21
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
source $HOME/bin/pythonpath.sh

# Show environment
env

# Show executable dependencies
ldd $HOME/allHISQ/bin/ks_spectrum_hisq
ldd $HOME/allHISQ/bin/ks_spectrum_hisq_sm37-sp-openmpi2

# Job parameters
if [ -n "${SLURM_SUBMIT_DIR}" ]
then
  cd ${SLURM_SUBMIT_DIR}
  testing=0
  prompt=0
else
  echo "Not a SLURM job.  Running in test mode."
  NCASES=1
  LATS="x.99"
  NJOBS=1
  testing=1
  prompt=2
fi

ncases=${NCASES}
cfgs_milc=${LATS}
njobs=${NJOBS}

# location of QUDA tunecache file
export QUDA_RESOURCE_PATH=${SLURM_SUBMIT_DIR}
export OMP_NUM_THREADS=8
#export OMPI_MCA_btl=self,vader,tcp
export OMPI_MCA_btl_openib_connect_udcm_max_retry=1000

argList="${LATS} ${ncases} 1"
scriptList="../scripts/params-allHISQ-plus4.yaml ../scripts/params-launch.yaml params-ens.yaml params-machine.yaml"

echo "Removing any leftover correlators"
./purge_corrs.sh ${LATS} ${NCASES} run3c

echo "Running the job script:"
echo "python ../scripts/make-allHISQ-prompts-NoHiddenSSD.py ${argList} ${scriptList}"

# Use Intel's python3 until it is installed in /usr/local
/hpcgpfs01/software/Intel/psxe2019/intelpython3/bin/python ../scripts/make-allHISQ-prompts-NoHiddenSSD.py ${argList} ${scriptList}

if [ $? -ne 0 ]
then
    echo "Exiting because of errors in job"
    exit 1
else
    echo "Finished with status 0."
    exit 0
fi

