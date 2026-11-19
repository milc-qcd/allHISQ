#! /bin/bash

# Creates a fiducial list of loose-solve data paths with line counts

# Point this script to the "data" directory for a complete instance
# of the output correlator tree with correlator files.

# Usage

#   make_tar_fiducial_new.sh <path>

# where <path> is the path to the "data" subdirectory
# containing the fiducial set of correlator files

if [ $# -lt 1 ]
then
    echo "Usage $0 <path>"
    exit 1
fi

path=$1
corrfid="corr.fiducial"

if [ ! -d $path ]
then
    echo "$path is not a directory"
    exit 1
fi

pushd $path
filelist=`find . -name '*corr*' -print`
popd

if [ -z "$filelist" ]
then
    echo "No files found"
    exit 1
fi

# Get configuration number from first corr file in list
example=`echo "${filelist}" | head -1`
cfg=`echo $example | awk -F_ '{print $2}'`

cat /dev/null > $corrfid  # Start with a clean file
for f in ${filelist}
do
    # Replace configuration number with "CFG"
    g=`echo $f | sed 's/'${cfg}'/CFG/'`
    echo $g `wc -l $path/$f | awk '{print $1}'` >> $corrfid
done
