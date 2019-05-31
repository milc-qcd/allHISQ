# Scripts supporting job queue management
# spawnjob.py and check_completed.py

import sys, os, yaml, subprocess
from StringIO import StringIO

######################################################################
def lockFileName(todoFile):
    """Directory entry"""
    return todoFile + ".lock"

######################################################################
def setTodoLock(lockFile):
    """Set lock file"""

    if os.access(lockFile, os.R_OK):
        print "Error. Lock file present. Quitting."
        sys.exit(1)

    subprocess.call(["touch", lockFile])
    
######################################################################
def removeTodoLock(lockFile):
    """Remove lock file"""
    subprocess.call(["rm", lockFile])


############################################################
def updateParam(param, paramUpdate):
    """Update the param dictionary according to terms in paramUpdate"""

    # Updating is recursive in the tree so we can update selected branches
    # leaving the remainder untouched
    for b in paramUpdate.keys():
        try:
            k = paramUpdate[b].keys()
            n = len(k)
        except AttributeError:
            n = 0

        if b in param.keys() and n > 0:
            # Keep descending until we run out of branches
            updateParam(param[b], paramUpdate[b])
        else:
            # Then stop, replacing just the last branch or creating a new one
            param[b] = paramUpdate[b]

    return param

############################################################
def loadParam(YAML):
    """Load a YAML parameter file"""

    # Initial parameter file
    try:
        param = yaml.load(open(YAML,'r'))
    except:
        print "ERROR: Error loading the parameter file", YAML
        sys.exit(1)

    return param

######################################################################
def readTodo(todoFile, lockFile):
    """Read the todo file"""
    
    setTodoLock(lockFile)
    todoList = dict()
    try:
        with open(todoFile) as todo:
            todoLines = todo.readlines()
    except IOError:
        print "Can't open", todoFile
        sys.exit(1)

    for line in todoLines:
        if len(line) == 1:
            continue
        a = line.split()
        todoList[a[0]] = a

    todo.close()
    return todoList

######################################################################
def cmpToDoEntries(td1, td2):
    """Compare quark keys.  This order is for multimass KS"""

    (stream1, cfg1) = td1.split(".")
    (stream2, cfg2) = td2.split(".")

    # Sort first on stream, then on cfg
    order = cmp(stream1, stream2)
    if order == 0:
        order = cmp(int(cfg1), int(cfg2))

    return order

######################################################################
def writeTodo(todoFile, lockFile, todoList):
    """Write the todo file"""

    # Back up the files
    subprocess.call(["mv", todoFile, todoFile + ".bak"])

    try:
        todo = open(todoFile, "w")

    except IOError:
        print "Can't open", todoFile, "for writing"
        sys.exit(1)
            
    for line in sorted(todoList, cmpToDoEntries):
        a = tuple(todoList[line])
        if len(a) == 4:
            print >>todo, "%s %s %s %s" % a
        elif len(a) == 3:
            print >>todo, "%s %s %s" % a
        elif len(a) == 2:
            print >>todo, "%s %s" % a
        elif len(a) == 1:
            print >>todo, "%s" % a

    todo.close()

    removeTodoLock(lockFile)

######################################################################
def concatenate(files):
    """Concatenate a list of files into a StringIO object."""
    out = StringIO()
    for file in files:
        with open(file, 'r') as f:
            out.writelines(f.readlines())
            out.write('\n')
    out.seek(0)
    return out

######################################################################
def readParams(files):
    """Load a set of YAML parameter files into a single dictionary.
    First file in list should contain global YAML references."""
    filestring = concatenate(files)
    return yaml.load(filestring)
