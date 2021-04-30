#! /usr/bin/env python

# Python 3 version

import sys, os, yaml, re, subprocess
from TodoUtils import *
from Cheetah.Template import Template

# Nanny script for managing job queues
# C. DeTar 

# Usage

# From the ensemble directory containing params-allHISQ.yaml and the
# todo file, do:
# ../scripts/spawnjob.py

# Requires a todo file with a list of configurations to be processed

# The todo file contains the list of jobs to be done.
# The line format of the todo file is
# <cfgno> [<flag> [<jobid>]]
# If the flag is empty, the job needs to be run
# If the flag is "X", the job has been finished
# If it is flagged "Q", the job was queued and <jobid> is present

# Requires params-allHISQ.yaml with definitions of variables needed here

######################################################################
def countQueue( scheduler,  myjobname ):
    """Count my jobs in the queue"""

    user = os.environ['USER']

    if scheduler == 'LSF':
        # Should sync files before submission
        cmd = "./setup_rsync.sh"
        print(cmd)
        reply = ""
        try:
            reply = subprocess.check_output(cmd, shell=True).splitlines()
        except subprocess.CalledProcessError as e:
            print(reply)
            print("Job rsync error.  Return code", e.returncode)
            sys.exit(1)
        cmd = ' '.join(["bjobs -u", user, "| grep", user, "| grep -w", myjobname, "| wc -l"])
    elif scheduler == 'PBS':
        cmd = ' '.join(["qstat -u", user, "| grep", user, "| grep -w", myjobname, "| wc -l"])
    elif scheduler == 'SLURM':
        cmd = ' '.join(["squeue -u", user, "| grep", user, "| grep -w", myjobname, "| wc -l"])
    elif scheduler == 'Cobalt':
        cmd = ' '.join(["qstat -fu", user, "| grep", user, "| grep -w", myjobname, "| wc -l"])
    else:
        print("Don't recognize scheduler", scheduler)
        print("Quitting")
        sys.exit(1)

    nqueued = int(subprocess.check_output(cmd,shell=True))

    return nqueued

######################################################################
def nextCfgnos( maxCases, todoList ):
    """Get next sets of cfgnos from todo file"""

    # return status 1 failure, 0 success

    # Get the cfg number and source location 
    # of the next lattice from the todo file

    cfgnos = []
    for line in sorted(todoList,key=keyToDoEntries):
        a = todoList[line]
        if len(a) == 1 or a[1] != "Q" and not "X" in a[1] :
            cfgnos.append(a[0])
            if len(cfgnos) >= maxCases:
                break

    ncases = len(cfgnos)
    
    if ncases > 0:
        print("Found", ncases, "cases...", cfgnos)

    return cfgnos



######################################################################
# def nextQsubSeqno(file):
#     """Get our next qsub index"""
# 
#     try:
#         with open(file,"r") as qsubSeqFile:
#             lines = qsubSeqFile.readlines()
#     except IOError:
#         print "Can't open", file
#         sys.exit(1)
#     qsubSeqFile.close()
# 
#     qsubSeqNo = int(lines[0])
#     qsubSeqNo = qsubSeqNo + 1
# 
#     qsubSeqFile = open(file,"w")
#     print >>qsubSeqFile, qsubSeqNo
#     qsubSeqFile.close()
# 
#     return qsubSeqNo

######################################################################
def submitJob(param, cfgnos, jobScript):
    """Submit the job"""

    layout = param['submit']['layout']
    njobs = layout['njobs']
    nodes = layout['basenodes'] * njobs
    np = nodes * layout['ppn']

    walltime = param['submit']['walltime']
    jobname = param['submit']['jobname']

    locale = param['submit']['locale']
    try:
        archflags = param['launch'][locale]['archflags']
    except KeyError:
        archflags = ''
    scheduler = param['launch'][locale]['scheduler']

    # Environment variables passed to the job script
    LATS = "/".join(str(c) for c in cfgnos)
    NCASES = str(len(cfgnos))
    NJOBS = str(njobs)
    NP = str(np)
    os.environ["LATS"] = LATS
    os.environ["NCASES"] = NCASES
    os.environ["NJOBS"] = NJOBS
    os.environ["NP"] = NP

    # Does job script exist?
    try:
        stat = os.stat(jobScript)
    except OSError:
        print("Can't find", jobScript)
        print("Quitting")
        sys.exit(1)

    # Job submission command depends on locale
    if scheduler == 'LSF':
        # Should sync files before submission
        cmd = "./setup_rsync.sh"
        print(cmd)
        reply = ""
        try:
            reply = subprocess.check_output(cmd, shell=True).decode().splitlines()
        except subprocess.CalledProcessError as e:
            print(reply)
            print("Job rsync error.  Return code", e.returncode)
            sys.exit(1)
        cmd = [ "bsub", "-nnodes", str(nodes), "-W", walltime, "-J", jobname, jobScript ]
    elif scheduler == 'PBS':
        cmd = [ "qsub", "-l", ",".join(["nodes="+str(nodes), "walltime="+walltime]), "-N", jobname, jobScript ]
    elif scheduler == 'SLURM':
#        cmd = [ "sbatch", "-N", str(nodes), "-n", NP, "-t", walltime, "-J", jobname, archflags, jobScript ]
        cmd = [ "sbatch", "-N", str(nodes), "-t", walltime, "-J", jobname, archflags, jobScript ]
    elif scheduler == 'Cobalt':
        cmd = [ "qsub", "-A LatticeQCD_3", "-n", str(nodes), "-t", walltime, "--jobname", jobname, archflags, "--mode script", "--env LATS="+LATS+":NCASES="+NCASES+":NJOBS="+NJOBS+":NP="+NP, jobScript ]
    else:
        print("Don't recognize scheduler", scheduler)
        print("Quitting")
        sys.exit(1)

    cmd = " ".join(cmd)
    print(cmd)
    reply = ""
    try:
        reply = subprocess.check_output(cmd, shell=True).decode().splitlines()
    except subprocess.CalledProcessError as e:
        print(reply)
        print("Job submission error.  Return code", e.returncode)
        sys.exit(1)

    print(reply)

    # Get job ID
    if scheduler == 'LSF':
        # a.2100 Q Job <99173> is submitted to default queue <batch>
        jobid = reply[0].split()[1].split("<")[1].split(">")[0]
    elif scheduler == 'PBS':
        # 3314170.kaon2.fnal.gov submitted
        jobid = reply[0].split(".")[0]
    elif scheduler == 'SLURM':
        # Submitted batch job 10059729
        jobid = reply[len(reply)-1].split()[3]
    elif scheduler == 'Cobalt':
        # ** Project 'semileptonic'; job rerouted to queue 'prod-short'
        # ['1607897']
        jobid = reply[-1]

    if type(jobid) is bytes:
        jobid = jobid.decode('ASCII')

    date = subprocess.check_output("date",shell=True).rstrip().decode()
    print(date, "Submitted job", jobid, "for cfgs", cfgnos)

    return (0, jobid)

######################################################################
def markQueuedTodoEntries(cfgnos, jobid, todoList):
    """Update the todoFile, change status to "Q" and mark the job number"""

    for cfg in cfgnos:
        todoList[cfg] = [ cfg, "Q", jobid ]

######################################################################
def nannyLoop(YAML, YAMLLaunch):
    """Check job periodically and submit to the queue"""
    
    date = subprocess.check_output("date",shell=True).rstrip().decode()
    hostname = subprocess.check_output("hostname",shell=True).rstrip().decode()
    print(date, "Spawn job process", os.getpid(), "started on", hostname)

    param = loadParam(YAML)

    paramLaunch = loadParam(YAMLLaunch)
    param = updateParam(param, paramLaunch)

    # Keep going until
    #   we see a file called "STOP" OR
    #   we have exhausted the list OR
    #   there are job submission or queue checking errors

    while True:
        if os.access("STOP", os.R_OK):
            print("Spawn job process stopped because STOP file is present")
            break

        todoFile = param['nanny']['todofile']
        maxCases = param['nanny']['maxcases']
        njobs = param['submit']['layout']['njobs']
        jobScript = param['submit']['jobScript']
        locale = param['submit']['locale']
        launchLocale = param['launch'][locale]
        scheduler = launchLocale['scheduler']
        jobname = param['submit']['jobname']

        lockFile = lockFileName(todoFile)

        # Count queued jobs with our job name
        nqueued = countQueue( scheduler, jobname )
  
        # Submit until we have the desired number of jobs in the queue
        if nqueued < param['nanny']['maxqueue']:
            todoList = readTodo(todoFile, lockFile)

            # List a set of cfgnos
            cfgnos = nextCfgnos(maxCases, todoList)
            ncases = len(cfgnos)

            # If we have exhausted the todo list, stop
            if ncases <= 0:
                print("No more lattices. Nanny quitting.")
                removeTodoLock(lockFile)
                sys.exit(0)

            # Submit the job
            ( status, jobid ) = submitJob(param, cfgnos, jobScript)
            
            # Job submission succeeded
            # Edit the todoFile, marking the lattice queued and indicating the jobid
            if status == 0:
                markQueuedTodoEntries(cfgnos, jobid, todoList)
            else:
                # Job submission failed
                if status == 1:
                    # Fatal error
                    sys.exit(1)
                else:
                    print("Will retry submitting", cfgnos, "later")

            writeTodo(todoFile, lockFile, todoList)
        sys.stdout.flush()
            
        subprocess.call(["sleep", str( param['nanny']['wait'] ) ])

        # Reload parameters in case of changes
        param = loadParam(YAML)

        paramLaunch = loadParam(YAMLLaunch)
        param = updateParam(param, paramLaunch)


############################################################
def main():

    # Parameter file
    YAML = "params-machine.yaml"
    YAMLLaunch = "../scripts/params-launch.yaml"
    nannyLoop(YAML, YAMLLaunch)


############################################################
main()

