#! /bin/bash

#SBATCH --gres=gpu:2
#SBATCH -N 4
#SBATCH -p long
#SBATCH --qos=scavenger
#SBATCH -C pascal
#SBATCH -A semibdff-20-21
#SBATCH -e stderrJob%jnode%n
#SBATCH -o stdoutJob%jnode%n
####### -t (command line in spawnjob.py)
####### -J (command line in spawnjob.py)
#SBATCH -S 4
#SBATCH -V

# Submission command must define environment the variable RUNCMDFILE
# sbatch -N ${NODES} -t ${walltime} -J ${jobname} ${slurm_script}

umask 0022

echo "Running on nodes"
echo $SLURM_JOB_NODELIST

echo "Running with RUNCMDFILE ${RUNCMDFILE}"

if [ ! -n "${SLURM_SUBMIT_DIR}" ]
then
  echo "FATAL: Not a SLURM job."
  exit 1
fi
jobid=${SLURM_JOBID}

runcmdfile=${SLURM_SUBMIT_DIR}/${RUNCMDFILE}

echo "`date` Running on nodes"
echo $SLURM_JOB_NODELIST

# BNL does not have DataWarp, so we fake it
DW_JOB_STRIPED=/hpcgpfs01/work/lqcd/semibdff-18-19/allHISQ

if [ -z "${DW_JOB_STRIPED}" ]
then
  echo "FATAL: no DW_JOB_STRIPED in environment"
  exit 1
fi

if [ ! -f "${runcmdfile}" ]
then
  echo "FATAL: run command file ${runcmdfile} not found"
  exit 1
fi

# Edit the job command file
# replacing "JOBID" with the job number
# and "DW_JOB_STRIPED" with the datawarp path.

echo "Replacing 'JOBID' with ${SLURM_JOBID} and 'DW_JOB_STRIPED' with ${DW_JOB_STRIPED}"

for f in `awk '{for(i=1;i<=NF;i++)if(index($i,"inJob")>0)print $i}' ${runcmdfile}`
do
  for g in ${f}*
  do
    echo "sed 's/JOBID/'${SLURM_JOBID}'/' < $g | sed 's|DW_JOB_STRIPED|'${DW_JOB_STRIPED}'/'"
    sed 's|JOBID|'${SLURM_JOBID}'|' < $g | sed 's|DW_JOB_STRIPED|'${DW_JOB_STRIPED}'|' > foo.${SLURM_JOBID}
    cp foo.${SLURM_JOBID} $g
    rm foo.${SLURM_JOBID}
  done
done

# The set up script creates a file tree under "DW_JOB_STRIPED" that we
# copy to datawarp, now that we know where it is.
# for d in DW_JOB_STRIPED/prop/*
# do
#   c=`basename $d`
#   mkdir -p ${DW_JOB_STRIPED}/prop/${c}
# #  rmdir $d
# done
# 
# for d in DW_JOB_STRIPED/rand/*
# do
#   c=`basename $d`
#   mkdir -p $DW_JOB_STRIPED/rand/${c}
# #  rmdir $d
# done

# Run production jobs out of $CSCRATCH
# SCRATCH_HOME=$CSCRATCH
# SCRATCH=${SCRATCH_HOME}/allHISQ/scratch/l64192f211b700m00316m0158m188
# mkdir -p $SCRATCH
# ./setup_rsync.sh  ${SCRATCH_HOME}
# cd $SCRATCH
export PYTHONPATH="../scripts/:${PYTHONPATH}"

export OMP_NUM_THREADS=4
#export OMPI_MCA_btl=self,vader,tcp
export OMPI_MCA_btl_openib_connect_udcm_max_retry=1000
export PMI_MMAP_SYNC_WAIT_TIME=600

# echo "`date` Broadcasting the executable"
# sbcast ../bin/ks_spectrum_hisq /tmp/ks_spectrum_hisq
# ls -l /tmp/ks_spectrum_hisq
# 
echo "`date` Running the job launch commands:"
source ${runcmdfile}

if [ $? -ne 0 ]
then
  echo "`date` Exiting because of errors in job"
  exit 1
else
  exit 0
fi

