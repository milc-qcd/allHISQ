#! /usr/bin/env python3

# Python 3 version

# Run check_completed.py repeatedly

import sys, os, yaml, re, subprocess, copy
from TodoUtils import *
from Cheetah.Template import Template

######################################################################
def checkComplete():
    """Check completion of queued jobs and purge scratch files"""

    cmd = ["../scripts/check_completed.py" ]

    print(cmd)
    sys.stdout.flush()
#    reply = ""
    p = subprocess.Popen(cmd)

    #     try:
    #         reply = subprocess.check_output(cmd, shell=True).decode().splitlines()
    #     except subprocess.CalledProcessError as e:
    #         print("Error checking job completion.  Return code", e.returncode)
    # 
    #     for line in reply:
    #         print(line)

    return

# For python3.7...
#    try:
#        process = subprocess.Popen(
#            cmd,
#            stdout=subprocess.PIPE,
#            stderr=subprocess.STDOUT,
#            text=True,
#            bufsize=1
#        )
        

######################################################################
def nannyLoop(YAML, YAMLLaunch):

    date = subprocess.check_output("date",shell=True).rstrip().decode()
    hostname = subprocess.check_output("hostname",shell=True).rstrip().decode()
    print(date, "Check completed process", os.getpid(), "started on", hostname)
    sys.stdout.flush()

    param = loadParam(YAML)

    paramLaunch = loadParam(YAMLLaunch)
    param = updateParam(param, paramLaunch)

    # Keep going until
    #   we see a file called "STOP" OR
    #   we have exhausted the list OR
    #   there are job submission or queue checking errors

    while True:

        if os.access("STOP", os.R_OK):
            print("Check_complete process stopped because STOP file is present")
            break

        if os.access("HELLO", os.R_OK):
            print("Check_complete: I'm on the job")

        todoFile = param['nanny']['todofile']

        # Check completion and purge scratch files for completed jobs
        checkComplete()
        
        subprocess.call(["sleep", "120"])

############################################################
def main():

    # Parameter file
    YAML = "params-machine.yaml"
    YAMLLaunch = "../scripts/params-launch.yaml"

    nannyLoop(YAML, YAMLLaunch)


############################################################
main()

