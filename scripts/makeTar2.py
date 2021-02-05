#! /usr/bin/env python

import sys, os, re, subprocess

# Create a tar file from "data" and "logs" under the "run" directory tree

# Usage

#  makeTar2.py <run> <seriesCfg> <tarList>

#  run        The run directory name containing "data" and "logs"
#  seriesCfg  The configuraition label, as in a.505
#  tarList    The complete list of paths to the correlator data, starting from the "loose"
#             or "fine" subdirectories

# Format of tarList: one line for each correlator file
# but with "CFG" in place of the configuration number and a line count for
# data for a single time slice.  These values are used in conjunction with
# the antiquark_source_origin to determine completeness

# Format ...
# pi/m0.0024-m0.0024-p100/corr2pt_CFG 177
# pi/m0.0024-m0.0024-p222/corr2pt_CFG 177

#######################################################################
def decodeSeriesCfg(seriesCfg):
    """Decode series, cfg, as it appeaers in the todo file"""
    return seriesCfg.split(".")

######################################################################
def codeCfg(suffix, cfg):
    """Encode tsrc and cfg for file names"""
    if suffix == '' or suffix == None:
        config = { 'series': 'a', 'trajectory': int(cfg) }
    else:
        config = { 'series': suffix, 'trajectory': int(cfg) }
    return '%(series)s%(trajectory)06d' % config

######################################################################
def main():

    if len(sys.argv) < 4:
        print("Usage")
        print(sys.argv[0], "<run> <seriesCfg> <jobID>")
        sys.exit(1)

    ( run, seriesCfg, jobID ) = sys.argv[1:4]

    series, cfg = decodeSeriesCfg(seriesCfg)
    s06Cfg = codeCfg(series, cfg)

    # Name of the tar file to be produced
    tarFile = "Job" + jobID + "_" + s06Cfg + ".tar.bz2"
    tarDir = os.path.join(run, "tar")

    cmd = ' '.join(["mkdir -p", tarDir])
    print(cmd)
    try:
        subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print("ERROR: can't make directory", tarDir)
        sys.exit(1)

    tarPath = os.path.join(tarDir, tarFile)

    fileList = os.path.join(run, "foo")

    cmd = ' '.join(["pushd", run, "; find data -name \'*"+s06Cfg+"\' -print > foo; popd"])
    print(cmd)
    try:
        subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print("ERROR: can't list data files in", fileList)
        sys.exit(1)

    cmd = ' '.join(["pushd", run, "; find logs -name \'*"+s06Cfg+"\' -print >> foo; popd"])
    print(cmd)
    try:
        subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print("ERROR: can't list log files in", fileList)
        sys.exit(1)

    cmd = ' '.join(["tar -C ", run, "-cjf ", tarPath, "-T ", fileList])
    print(cmd)
    try:
        subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print("ERROR: can't create", tarPath, "from", fileList)
        sys.exit(1)

######################################################################
main()
