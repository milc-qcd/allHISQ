#! /bin/bash

# Copy files from the NFS area to gpfs in preparation for job submission

# Super_HISQ files

GPFSHOME=/gpfs/alpine/proj-shared/phy131/detar
NFSHOME=/ccs/home/detar

SRC=${NFSHOME}/allHISQ
DST=${GPFSHOME}/allHISQ

BINFILES="\
ks_spectrum_hisq \
ks_spectrum_hisq.hotfix \
"

for f in ${BINFILES}
do
    rsync -auv ${SRC}/bin/$f ${DST}/bin/
done

SCRIPTFILES=" \
allHISQFiles.py \
allHISQKeys.py \
make-allHISQ-prompts.py \
params-allHISQ-plus.yaml \
params-allHISQ.yaml \
params-launch.yaml
"

for f in ${SCRIPTFILES}
do
    rsync -auv ${SRC}/scripts/$f ${DST}/scripts/
done


ENS="l64144f211b672m0024m024m286"

ENSFILES="
lat \
make_ssd_dirs.sh \
params-ens.yaml
params-machine.yaml
prop \
purge_corrs.sh \
purge_props.sh \
purge_symlinks.sh \
rand \
run.lsf \
run0 \
"

for f in ${ENSFILES}
do
    rsync -aluv ${SRC}/${ENS}/$f ${DST}/${ENS}/
done

# Wavefunction

rsync -auv ${SRC}/wavefunction/* ${DST}/wavefunction/

# Python lib files

SRC=${NFSHOME}/python_modules
DST=${GPFSHOME}/

rsync -auv ${SRC} ${DST}

# Additional Python files

rsync -auv ${NFSHOME}/milc_qcd/python2lib/MILCprompts/MILCprompts.py ${GPFSHOME}/MILCprompts/


