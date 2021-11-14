# File naming and handling procedures for the allHISQB project
# C. DeTar 5 April 2018

# Python 3 version

import os, sys, re, subprocess

verbose = False

######################################################################
def remoteRootDir(root, lrun):
    """Root of remote files for the current ensemble"""
    return os.path.join( root, lrun )

######################################################################
def archiveRootDir(root, afm, lrun):
    """Root of remote files for the current ensemble"""
    return os.path.join( root, afm, lrun )

######################################################################
def addRootPaths(param):
    """Add parameter-dependent archive and remote paths to dictionary"""

    ensemble = param['ensemble']
    run = ensemble['run']
    lrun = 'l' + run
    afm = 'a' + ensemble['afm']
    root = param['files']['root']
    remoteRoot = remoteRootDir(param['remoteRoot'], lrun )
    archiveRoot = archiveRootDir(param['archiveRoot'], afm, lrun)
    # Add to the parameter dictionary
    root['remote'] = remoteRoot
    root['remoteSSD'] = "DW_JOB_STRIPED"
    root['archive'] = archiveRoot

######################################################################
def localPath(filename):
    """Generic path for local files"""
    return os.path.join( localRoot, filename )

#####################################################################
def buildPath(root, dirs):
    """Build path from root plus a list of subdirs"""
    r = root
    if dirs != None:
        for d in dirs:
            r = os.path.join(r, d)
    return r

#####################################################################
def makePath(path):
    """Make directories"""
    try:
        stat = os.stat(path)
    except OSError:
        try:
            os.makedirs(path)
        except OSError:
            print("WARNING: Can't create directories", path)

#####################################################################
def checkSSDList(path):
    """See if 'path' is in the list of files presumably on the SSD"""
    return False

#####################################################################
# Class for staging files from the remote path to a local path for MPP execution
# Also used to archive (store) result files
# For multijob running for stdin, stdout, stdeff we use symlinks to map the
# internally constructed names with ".jnn" suffixes to the actual file names.

# 'w' in "mode" means don't fetch.  Store if it doesn't exist.
# 'x' in "mode" means scratch only. Fetch if available. Don't store
# 'r' in "mode" means must fetch.  Store if it doesn't exist.
class StageFile:
    """Staging and saving files"""
    def __init__(self, localDir, localSubdirs, remoteDir, remoteSubdirs, name, mode, 
                 multiJobSubDirs, multiJobName, createLink):
        self.localDir = localDir
        self.remoteDir = remoteDir
        self.localSubdirs = localSubdirs
        self.remoteSubdirs = remoteSubdirs
        self.fileName = name
        self.mode = mode
        self.multiJobSubDirs = multiJobSubDirs
        self.multiJobName = multiJobName
        self.createLink = createLink

        self.staged = False
        self.fd = None

        self.remoteDirs = buildPath(self.remoteDir, self.remoteSubdirs)
        makePath(self.remoteDirs)
        self.pathRemote = os.path.join(self.remoteDirs, self.fileName)

        # If no local directory specified, then use remote path
        if self.localDir == None:
            self.localDirs = None
            self.pathLocal = self.pathRemote
        else:
            self.localDirs = buildPath(self.localDir, self.localSubdirs)
            makePath(self.localDirs)
            self.pathLocal = os.path.join(self.localDirs, self.fileName)

        # Create symlink to file if requested
        if self.multiJobName != None and self.createLink:
            print("remoteDir:", self.remoteDir, "multiJobSubDirs:", self.multiJobSubDirs)
            print("multiJobName", self.multiJobSubDirs)
            self.symLinkDirs = buildPath(self.remoteDir, self.multiJobSubDirs)
            self.pathSymLink = os.path.join(self.symLinkDirs, self.multiJobName)

            if verbose:
                print("Creating symlink to", self.pathLocal, "from", self.pathSymLink)
            # Create the target file if it doesn't exist
            if self.mode == 'w' and not os.access(self.pathLocal, os.R_OK):
                f = open(self.pathLocal, 'w')
                f.close()
            try:
                os.symlink(self.pathLocal, self.pathSymLink)
            except OSError:
                print("WARNING: ln -s failed for", self.pathSymLink)
        else:
            self.pathSymLink = None

        if not 'w' in self.mode:
            # Is the file already local?
            if os.access(self.pathLocal, os.R_OK):
                if verbose:
                    print("Using existing",self.pathLocal)
                self.staged = True

            # Perhaps it is in partfile format locally
            # We check only vol0000 and assume all other parts are in place
            elif os.access(self.pathLocal+'.vol0000', os.R_OK):
                if verbose:
                    print("Using existing partfile",self.pathLocal)
                self.staged = True
                
            elif checkSSDList(self.pathLocal):
                if verbose:
                    print("SSD list has",self.pathLocal)
                self.staged = True

            # If not local, then fetch it
            elif os.access(self.pathRemote, os.R_OK):
                cmd = ' '.join(('/usr/bin/rsync -auv', self.pathRemote, self.pathLocal))
                if verbose:
                    print('#',cmd)
                try:
                    subprocess.check_output(cmd, shell = True)
                except subprocess.CalledProcessError as e:
                    print("WARNING: rsync failed for", e.cmd)
                    print("return code", e.returncode)
                self.staged = True
            else:
                self.staged = False
                if 'r' in self.mode:
                    if verbose:
                        print("WARNING: can't find", self.pathRemote)

    def openwrite(self):
        if self.fd == None:
            try:
                self.fd = open(self.pathLocal,'w')
            except IOError:
                print("WARNING: Can't open", self.pathLocal)
                self.fd = None
        return self.fd

    def close(self):
        try:
            self.fd.close()
        except:
            print("WARNING: Close failed for", self.fileName)
        self.fd = None

    def exist(self):
        return self.staged
    
    def name(self):
        return self.fileName
    
    def path(self):
        if self.pathSymLink != None:
            # Strip any .jnn from the symlink name
            return re.sub('\.j\d\d$','',self.pathSymLink)
        else:
            return self.pathLocal

    def pathremote(self):
        return self.pathRemote

    def dirLocal(self):
        return self.localDirs

    def dirRemote(self):
        return self.remoteDirs

    def bzip2(self):
        filebz2 = re.compile(".*\.bz2$")
        if not filebz2.search(self.pathLocal):
            if os.access(self.pathLocal, os.R_OK):
                cmd = ' '.join(('bzip2', self.pathLocal))
                if verbose:
                    print("#", cmd)
                subprocess.check_output(cmd, shell = True)
            self.pathLocal = self.pathLocal + '.bz2'
            if not filebz2.search(self.pathRemote):
                self.pathRemote = self.pathRemote + '.bz2'

    def store(self):
        # Don't store if it doesn't exist
        if not self.staged:
            return
        # Reconcile multijob symlink with permanent name
        if self.pathSymLink != None:
            # If the symlink was not created, change the name instead
            if not self.createLink:
                try:
                    os.rename(self.pathSymLink, self.pathLocal)
                except OSError:
                    print("WARNING: rename failed for", self.pathSymLink)
            # Otherwise, just remove the symlink
            else:
                if verbose:
                    print("Removing sym link", self.pathSymLink)
                try:
                    os.remove(self.pathSymLink)
                except OSError:
                    print("WARNING: remove failed for", self.pathSymLink)

        # Copy file to archive if needed
        if verbose:
            print("#", self.pathLocal, "->", self.pathRemote)
        if not 'x' in self.mode and os.access(self.pathLocal, os.R_OK):
            if(self.pathLocal != self.pathRemote):
                cmd = ' '.join(('/usr/bin/rsync -auv --no-p --no-o --no-g', self.pathLocal, self.pathRemote))
                if verbose:
                    print(cmd)
                try:
                    subprocess.check_output(cmd, shell = True)
                except subprocess.CalledProcessError as e:
                    print("WARNING: rsync failed for", e.cmd)
                    print("return code", e.returncode)
        else:
            if verbose:
                print(self.pathLocal, "not stored, because either mode is", self.mode,"or read access is", os.access(self.pathLocal, os.R_OK))
            pass

    def delete_staged(self):
        if(self.staged and self.pathLocal != self.pathRemote):
            cmd = ' '.join(('/bin/rm', self.pathLocal))
            if verbose:
                print(cmd)
            try:
                subprocess.check_output(cmd, shell = True)
            except subprocess.CalledProcessError as e:
                print("WARNING: /bin/rm failed for", e.cmd)
                print("return code", e.returncode)

    pass 

######################################################################
def codeCfg(suffix, cfg):
    """Encode suffix and cfg for file names
       takes a, 120 -> a000120"""
    if suffix == '' or suffix == None:
        series = 'a'
    else:
        series = suffix
    return "{0:s}{1:06d}".format(series,int(cfg))

######################################################################
def codeTsrc(prec, tsrc):
    """Encode prec and tsrc for file names
       takes L 32 -> L032"""
    return "{0:s}{1:03d}".format(prec, tsrc)

######################################################################
def codePrecTsrcCfg(precTsrcConfigId):
    """Encode tsrc and cfg for file names
       takes [P, 32, a, 120] -> t32P.a000120"""
    (prec, tsrc, suffix, cfg) = precTsrcConfigId
    configId = codeCfg(suffix, cfg)
    return "t{0:d}{1:s}.{2:s}".format(tsrc, prec, configId)
######################################################################
def codePrecTsrcSym(precTsrcConfigId,kjob):
    """Encode tsrc and kjob for file names
       takes [P, 32, a, 120], 4 -> t32P.a000120.j04"""
    (prec, tsrc, suffix, cfg) = precTsrcConfigId
    return "t{0:d}{1:s}.j{2:02d}".format(tsrc, prec, kjob)
######################################################################
def ensFile(pfx, run, precTsrcConfigId):
    """Standard file name pattern containing the ensemble name, time source, and configuration"""
    sfx = codePrecTsrcCfg(precTsrcConfigId)
    return  "{0:s}_{1:s}_{2:s}".format(pfx, run, sfx)

######################################################################
def milc2FNAL(suffix, cfg):
    """Convert MILC cfg to FNAL"""
    leading = 0
    if suffix == 'b':
        leading = 5
    elif suffix == 'c':
        leading = 6
    return "{0:d}{1:05d}".format(leading, cfg)

######################################################################
def rndFile(sq, run, precTsrcConfigId):
    """Construct random source name"""
    return ensFile('rnd' + sq, run, precTsrcConfigId)

######################################################################
def latFileCoul( run, suffix, cfg):
    """Convention for Coulomb-gauge-fixed lattice file names"""
    return "l{0:s}{1:s}-Coul.{2:d}.ildg".format(run, suffix, int(cfg))

######################################################################
def latFileEig( run, suffix, cfg):
    """Convention for eigenpair file names"""
    return "eigPRIMME{0:s}nv600er10{1:s}.{2:d}".format(run, suffix, int(cfg))

######################################################################
def latFileMILCv5( run, suffix, cfg):
    """Convention for MILC v5 lattice file names"""
    return "l{0:s}{1:s}.{2:d}".format(run, suffix, int(cfg))

######################################################################
def propNameKS(qkKey, run, precTsrcConfigId):
    """Construct KS propagator file name"""
    return ensFile( 'prop_' + qkKey, run, precTsrcConfigId )

######################################################################
def propNameClover(qkKey, run, precTsrcConfigId):
    """Construct KS propagator file name"""
    return ensFile( 'prop_' + qkKey, run, precTsrcConfigId )

######################################################################
def corr3ptFileName(chan, run, extT, precTsrcConfigId):
    """Construct 3pt correlator file name"""
    (prec, tsrc, suffix, cfg) = precTsrcConfigId
    return "corr3pt_T{0:d}_{1:s}".format(extT,  codeCfg(suffix, cfg))

######################################################################
def corr2ptFileName(chan, run, precTsrcConfigId):
    """Construct 2pt correlator file name"""
    (prec, tsrc, suffix, cfg) = precTsrcConfigId
    return "corr2pt_{0:s}".format(codeCfg(suffix, cfg))

######################################################################
def massLabel(qk, mk):
    """Construct mass label"""
    if qk['type'] == 'clover':
        return "k" + mk
    elif qk['type'] == 'KS':
        return "m" + mk
    
######################################################################
def momLabel(mom):
    """Construct momentum label"""
    return "p{0:d}{1:d}{2:d}".format(*tuple(mom))
    
######################################################################
def massSubdir2pt(mQk, mAQk, mom):
    """Construct subdirectory name for 2pt correlator files"""
    return '-'.join([mQk, mAQk, momLabel(mom)])

######################################################################
def massSubdir3pt(mQkS, mQkP, mQkD, mom):
    """Construct subdirectory name for 2pt correlator files"""
    return '-'.join([mQkP, mQkS, mQkD, momLabel(mom)])

######################################################################
def logFileName(run, precTsrcConfigId, jobid, tag, seqno):
    """Construct log file (stdout) name
       takes run1a, [ P, 32, a, 120 ], 52343, X, step1 -> logJobX52343.a000120"""
    (prec, tsrc, suffix, cfg) = precTsrcConfigId
    # return "logJob{0:s}_{1:s}_{2:s}".format(jobid, seqno, codeTsrcCfg(precTsrcConfigId))
    return "logJob{0:s}{1:s}.{2:s}".format(tag, jobid, codeCfg(suffix, cfg))

######################################################################
def logFileSymLink(run, precTsrcConfigId, jobid, tag, seqno, kjob, njobs):
    """Construct log file (stdout) name
       takes run1a, [ P, 32, a, 120 ], 52343, X, step1, 4, 12 -> logJobX52343_t32.a000120.j04"""
    if njobs == 1:
        return None
    else:
        return "logJob{0:s}{1:s}_{2:s}_{3:s}".format(tag, jobid, seqno, 
                codePrecTsrcSym(precTsrcConfigId, kjob))

######################################################################
def outFileName(run, precTsrcConfigId, jobid, tag, seqno):
    """Construct log file (stdout) name
       takes run1a, [ P, 32, a, 120 ], 52343, X, step1 -> outJob52343_step1_t32P.a000120"""
    return "outJob{0:s}{1:s}_{2:s}_{3:s}".format(tag, jobid, seqno, codePrecTsrcCfg(precTsrcConfigId))

######################################################################
def outFileSymLink(run, precTsrcConfigId, jobid, tag, seqno, kjob, njobs):
    """Construct log file (stdout) name
       takes run1a, [ P, 32, a, 120 ], 52343, X, step1, 4, 12 -> outJob52343_step1_t32P.a000120.j04"""
    if njobs == 1:
        return None
    else:
        return "outJob{0:s}{1:s}_{2:s}_{3:s}".format(tag, jobid, seqno,
                                                     codePrecTsrcSym(precTsrcConfigId, kjob))

######################################################################
def errFileName(run, precTsrcConfigId, jobid, tag, seqno):
    """Construct error file (stderr) name"""
    return "errJob{0:s}{1:s}_{2:s}_{3:s}".format(tag, jobid, seqno, codePrecTsrcCfg(precTsrcConfigId))

######################################################################
def errFileSymLink(run, precTsrcConfigId, jobid, tag, seqno, kjob, njobs):
    """Construct error file (stderr) name"""
    if njobs == 1:
        return None
    else:
        return "errJob{0:s}{1:s}_{2:s}_{3:s}".format(tag, jobid, seqno,
                                                     codePrecTsrcSym(precTsrcConfigId, kjob))

######################################################################
def inFileName(run, precTsrcConfigId, jobid, tag, seqno):
    """Construct input file (stdin) name"""
    return "inJob{0:s}{1:s}_{2:s}_{3:s}".format(tag, jobid, seqno, codePrecTsrcCfg(precTsrcConfigId))

######################################################################
def inFileSymLink(run, precTsrcConfigId, jobid, tag, seqno, kjob, njobs):
    """Construct input file (stdin) name"""
    if njobs == 1:
        return None
    else:
        return "inJob{0:s}{1:s}_{2:s}_{3:s}".format(tag, jobid, seqno,
                                                    codePrecTsrcSym(precTsrcConfigId, kjob))

######################################################################
def prefixSpinTaste( pfx, spinTaste ):
    """Convert spin-taste prefix from gamma notation to bilinear notation
    For example, GXT-GT is converted to T14-V4"""
    gSpin, gTaste = spinTaste.split("-")
    pSpin = pfx[gSpin]
    pTaste = pfx[gTaste]
    prefix = '-'.join([ pSpin, pTaste])
    return prefix

######################################################################
def prefix3pt(pfx, stP, stC, extT, mQkP):
    """Make prefix for 3pt correlator"""
    prefixP = prefixSpinTaste(pfx, stP)
    prefixC = prefixSpinTaste(pfx, stC)
    prefix = '_'.join([prefixP, prefixC, 'T'+str(extT), mQkP])
    return prefix

######################################################################
def prefix2pt(pfx, stSnk):
    """Make prefix for 2pt correlator"""
    return prefixSpinTaste(pfx, stSnk)

