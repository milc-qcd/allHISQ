#! /bin/bash

# Copy files from the NFS area to gpfs in preparation for job submission

# Super_HISQ files

SCRATCHHOME=$CSCRATCH
NFSHOME=/global/homes/d/detar

SRC=${NFSHOME}/allHISQ
DST=${SCRATCHHOME}/allHISQ/scratch

BINFILES="\
ks_spectrum_hisq \
"

for f in ${BINFILES}
do
    rsync -auv ${SRC}/bin/$f ${DST}/bin/
done

SCRIPTFILES=" \
allHISQFiles.py \
allHISQFilesNoHiddenSSD.py \
allHISQKeys.py \
make-allHISQ-prompts-NoHiddenSSD.py \
params-allHISQ-plus4.yaml \
params-launch.yaml \
"
for f in ${SCRIPTFILES}
do
    rsync -auv ${SRC}/scripts/$f ${DST}/scripts/
done

SCRIPTFILES=" \
/global/homes/d/detar/milc_qcd/python3lib/MILCprompts/MILCprompts.py \
"
for f in ${SCRIPTFILES}
do
    rsync -auv $f ${DST}/scripts/
done

ENS="l64144f211b672m0024m024m286"

ENSFILES="
make_ssd_dirs.sh \
params-ens.yaml
params-machine.yaml
purge_corrs2.sh \
purge_props.sh \
purge_symlinks.sh \
run.slurm \
tar.fiducial \
run3a \
run3b \
run3c \
"

for f in ${ENSFILES}
do
    rsync -aluv ${SRC}/${ENS}/$f ${DST}/${ENS}/
done

# Wavefunction

rsync -auv ${SRC}/wavefunction/* ${DST}/wavefunction/

# Python lib files

SRC=${NFSHOME}/python_modules
DST=${SCRATCHHOME}/

rsync -auv ${SRC} ${DST}

# Additional Python files

#rsync -auv ${NFSHOME}/milc_qcd/python2lib/MILCprompts/MILCprompts.py ${SCRATCHHOME}/MILCprompts/


