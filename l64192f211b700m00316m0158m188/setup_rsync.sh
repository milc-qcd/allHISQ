#! /bin/bash

# Copy files from the NFS area to $CSCRATCH in preparation for running

SCRATCHHOME=$1
NFSHOME=${HOME}

SRC=${NFSHOME}/allHISQ
DST=${SCRATCHHOME}/allHISQ/scratch

BINFILES="\
ks_spectrum_hisq \
ks_spectrum_hisq.2021feb6 \
ks_spectrum_hisq.2020sep17 \
ks_spectrum_hisq.open_all \
"

for f in ${BINFILES}
do
    rsync -auv ${SRC}/bin/$f ${DST}/bin/
done

ENS="l64192f211b700m00316m0158m188"

ENSFILES="
run2 \
"

for f in ${ENSFILES}
do
    rsync -aluv ${SRC}/${ENS}/$f ${DST}/${ENS}/
done



