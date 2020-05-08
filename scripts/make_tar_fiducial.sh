#! /bin/bash

# Creates a fiducial list of loose-solve data paths with line counts

# Choose a complete tar file and run this script in a directory
# where it can unpack it

# Usage

#   make_tar_fiducial.sh <tarfile> <n>

# where <tarfile> is the fiducial tar file
# n is the number of loose source times in the job

if [ $# -lt 2 ]
then
    echo "Usage $0 <tarfile>"
    exit 1
fi

tarfile=$1
n=$2
tarfid="tar.fiducial"

# Get configuration number from tarfile name
# format is Job993823_c001268.tar.bz2

cfg=`echo $tarfile | awk -F_ '{print $2}' | awk -F. '{print $1}'`

tar -xjf $tarfile
cat /dev/null > $tarfid  # Start with a clean file
for f in `tar -tjf $tarfile data/loose`
do
    # Replace configuration number with "CFG"
    g=`echo $f | sed 's/'${cfg}'/CFG/' | sed 's|/data/loose||'`
    echo $g `wc -l $f | awk '{print $1/'${n}'}'` >> $tarfid
done
