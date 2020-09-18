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
# <cfgno> <[L|F]n> [<flag> [<jobid>]]
# Where cfgno is tne configuration number in the format x.nnn where x is the series letter and nnn
# is the configuration number in the series
# [L|F]n is the base source time slice for loose L and fine F solves -- e.g. F64
# (This is just a counter. The base times are converted to a precessed time in the job script.)
# If flag is empty, the job needs to be run
# If flag is "X", the job has been finished
# If it is "Q", the job was queued and <jobid> is present

# Requires TodoUtils.py and params-launch.yaml with definitions of variables needed here

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
            reply = subprocess.check_output(cmd, shell=True).decode().splitlines()
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
def nextJobSeqNo(file):
    """Read, update, write job sequence number in file"""

    fp = open(file)
    s = fp.read()
    if len(s) == 0:
        s = 0
    else:
        s = int(s.rstrip())
    fp.close()

    s = s + 1

    fp = open(file,"w")
    print(s,file=fp)
    fp.close()

    # Insert leading zeros
    return "{0:04d}".format(s)

######################################################################
def nextCfgnos( maxCases, todoList ):
    """Get next sets of cfgnos / source times from todo file"""

    # return status 1 failure, 0 success

    # Get the cfg number and source location 
    # of the next lattice from the todo file

    cfgnoTsrcs = []
    for line in sorted(todoList,key=keyToDoEntries):
        a = todoList[line]
        if len(a) < 2:
            print("ERROR: bad todo line format");
            print(a)
            sys.exit(1)
        if len(a) == 2 or a[2] != "Q" and not "X" in a[2]:
            cfgnoTsrcs.append([a[0],a[1]])
            if len(cfgnoTsrcs) >= maxCases:
                break

    ncases = len(cfgnoTsrcs)
    
    if ncases > 0:
        print("Found", ncases, "cases...", cfgnoTsrcs)

    return cfgnoTsrcs



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
def setupJob(cfgnoTsrcs, njobs, jobSeqNo):
    """Set up the job"""

    # Pack configuration numbers and source times
    c, t = list(zip(*cfgnoTsrcs))
    cfgs_milc = "/".join(c)
    tsrcs = "/".join(t)
    
    ncases = str(len(cfgnoTsrcs))
    njobs = str(njobs)

    print("Setting up myJobID", jobSeqNo, "with NCASES", ncases, "in NJOBS",
          njobs, "LATS", cfgs_milc, "TSRCS", tsrcs)

    runCmdFile="runJob" + jobSeqNo + ".sh"

    argList = [cfgs_milc, tsrcs, ncases, njobs, jobSeqNo, runCmdFile]
    scriptList = ["../scripts/params-allHISQ-plus5.yaml",
                  "../scripts/params-launch.yaml",
                  "params-ens.yaml params-machine.yaml"]

    cmd = " ".join(["python ../scripts/make-allHISQ-prompts.py"] + argList + scriptList)
    print(cmd)

    reply = ""
    try:
        reply = subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(reply)
        print("Job setup error.  Return code", e.returncode)
        sys.exit(1)

    return runCmdFile
    
######################################################################
def submitJob(param, runCmdFile, jobScript):
    """Submit the job"""

    layout = param['submit']['layout']
    njobs = layout['njobs']
    nodes = layout['basenodes'] * njobs
    NP = str(nodes * layout['ppn'])

    walltime = param['submit']['walltime']
    jobname = param['submit']['jobname']

    locale = param['submit']['locale']
    try:
        archflags = param['launch'][locale]['archflags']
    except KeyError:
        archflags = ''
    scheduler = param['launch'][locale]['scheduler']

    # Does job script exist?
    try:
        stat = os.stat(jobScript)
    except OSError:
        print("Can't find", jobScript)
        print("Quitting")
        sys.exit(1)

    # Name of file containing job launch commands
    os.environ["RUNCMDFILE"] = runCmdFile

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
        cmd = [ "sbatch", "-N", str(nodes), "-n", NP, "-t", walltime, "-J", jobname, archflags, jobScript ]
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
        jobid = jobid.decode()
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
    print(date, "Submitted job", jobid, "for runCmdFile", runCmdFile)

    return (0, jobid)

######################################################################
def markQueuedTodoEntries(cfgnoTsrcs, jobid, todoList):
    """Update the todoFile, change status to "Q" and mark the job number"""

    for c, t in cfgnoTsrcs:
        key = c + "-" + t
        todoList[key] = [ c, t, "Q", jobid ]

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
            cfgnoTsrcs = nextCfgnos(maxCases, todoList)
            ncases = len(cfgnoTsrcs)

            # If we have exhausted the todo list, stop
            if ncases <= 0:
                print("No more lattices. Nanny quitting.")
                removeTodoLock(lockFile)
                sys.exit(0)

            # We need our own jobid for setting up the job
            jobSeqNo = nextJobSeqNo("JOBSEQNO")

            # Set up the job
            runCmdFile = setupJob(cfgnoTsrcs, njobs, jobSeqNo)

            # Submit the job
            status, jobid = submitJob(param, runCmdFile, jobScript)
            
            # Job submission succeeded
            # Edit the todoFile, marking the lattice queued and indicating the jobid
            if status == 0:
                markQueuedTodoEntries(cfgnoTsrcs, jobid, todoList)
            else:
                # Job submission failed
                if status == 1:
                    # Fatal error
                    sys.exit(1)
                else:
                    print("Will retry submitting", cfgnoTsrcs, "later")

            writeTodo(todoFile, lockFile, todoList)
        sys.stdout.flush()
            
        subprocess.call(["sleep", str( param['nanny']['wait'] ) ])

        # Reload parameters in case of changes
        param = loadParam(YAML)

        paramLaunch = loadParam(YAMLLaunch)
        param = updateParam(param, paramLaunch)


######################################################################
def testJobSetup():
    """Test the job setup"""

    cfgnoTsrcs = [["x.8","L.0"],["x.8","L.24"],["x.8","L.48"],
                  ["x.14","F.0"],["x.16","L.72"],["x.18","L.96"]]
    ncases = len(cfgnoTsrcs)
    njobs = ncases
    jobSeqNo = nextJobSeqNo("JOBSEQNO")

    # Set up the job
    runCmdFile = setupJob(cfgnoTsrcs, njobs, jobSeqNo )

    print("runCmdFile =", runCmdFile)
    
############################################################
def main():

    # Set permissions
    os.system("umask 022")
    print(sys.argv)

    try:
        a = sys.argv[1]
    except:
        a = ""

    if a == 'test':
        test = True
    else:
        test = False

    # Parameter file
    YAML = "params-machine.yaml"
    YAMLLaunch = "../scripts/params-launch.yaml"

    if test:
        testJobSetup()
    else:
        nannyLoop(YAML, YAMLLaunch)


############################################################
main()

