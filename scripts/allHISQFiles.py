# File naming and handling procedures for the Bpilnu project
# C. DeTar 5 April 2018

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
            print "WARNING: Can't create directories", path

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
                 multiJobName, createLink):
        self.localDir = localDir
        self.remoteDir = remoteDir
        self.localSubdirs = localSubdirs
        self.remoteSubdirs = remoteSubdirs
        self.fileName = name
        self.mode = mode
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
            self.pathSymLink = self.remoteDirs
        else:
            self.localDirs = buildPath(self.localDir, self.localSubdirs)
            makePath(self.localDirs)
            self.pathLocal = os.path.join(self.localDirs, self.fileName)
            self.pathSymLink = self.localDirs

        # Create symlink to file if requested
        if self.multiJobName != None and self.createLink:
            self.pathSymLink = os.path.join(self.pathSymLink, self.multiJobName)
            if verbose:
                print "Creating symlink to", self.pathLocal, "from", self.pathSymLink
            # Create the target file if it doesn't exist
            if self.mode == 'w' and not os.access(self.pathLocal, os.R_OK):
                f = open(self.pathLocal, 'w')
                f.close()
            try:
                os.symlink(self.pathLocal, self.pathSymLink)
            except OSError:
                print "WARNING: ln -s failed for", self.pathSymLink
        else:
            self.pathSymLink = None

        if not 'w' in self.mode:
            # Is the file already local?
            if os.access(self.pathLocal, os.R_OK):
                if verbose:
                    print "Using existing",self.pathLocal
                self.staged = True

            # Perhaps it is in partfile format locally
            # We check only vol0000 and assume all other parts are in place
            elif os.access(self.pathLocal+'.vol0000', os.R_OK):
                if verbose:
                    print "Using existing partfile",self.pathLocal
                self.staged = True
                
            elif checkSSDList(self.pathLocal):
                if verbose:
                    print "SSD list has",self.pathLocal
                self.staged = True

            # If not local, then fetch it
            elif os.access(self.pathRemote, os.R_OK):
                cmd = ' '.join(('/usr/bin/rsync -auv', self.pathRemote, self.pathLocal))
                if verbose:
                    print '#',cmd
                try:
                    subprocess.check_output(cmd, shell = True)
                except subprocess.CalledProcessError as e:
                    print "WARNING: rsync failed for", e.cmd
                    print "return code", e.returncode
                self.staged = True
            else:
                self.staged = False
                if 'r' in self.mode:
                    if verbose:
                        print "WARNING: can't find", self.pathRemote

    def openwrite(self):
        if self.fd == None:
            try:
                self.fd = open(self.pathLocal,'w')
            except IOError:
                print "WARNING: Can't open", self.pathLocal
                self.fd = None
        return self.fd

    def close(self):
        try:
            self.fd.close()
        except:
            print "WARNING: Close failed for", self.fileName
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
                    print "#", cmd
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
                    print "WARNING: rename failed for", self.pathSymLink
            # Otherwise, just remove the symlink
            else:
                if verbose:
                    print "Removing sym link", self.pathSymLink
                try:
                    os.remove(self.pathSymLink)
                except OSError:
                    print "WARNING: remove failed for", self.pathSymLink

        # Copy file to archive if needed
        if verbose:
            print "#", self.pathLocal, "->", self.pathRemote
        if not 'x' in self.mode and os.access(self.pathLocal, os.R_OK):
            if(self.pathLocal != self.pathRemote):
                cmd = ' '.join(('/usr/bin/rsync -auv --no-p --no-o --no-g', self.pathLocal, self.pathRemote))
                if verbose:
                    print cmd
                try:
                    subprocess.check_output(cmd, shell = True)
                except subprocess.CalledProcessError as e:
                    print "WARNING: rsync failed for", e.cmd
                    print "return code", e.returncode
        else:
            if verbose:
                print self.pathLocal, "not stored, because either mode is", self.mode,"or read access is", os.access(self.pathLocal, os.R_OK)
            pass

    def delete_staged(self):
        if(self.staged and self.pathLocal != self.pathRemote):
            cmd = ' '.join(('/bin/rm', self.pathLocal))
            if verbose:
                print cmd
            try:
                subprocess.check_output(cmd, shell = True)
            except subprocess.CalledProcessError as e:
                print "WARNING: /bin/rm failed for", e.cmd
                print "return code", e.returncode

    pass 

######################################################################
def codeCfg(suffix, cfg):
    """Encode tsrc and cfg for file names"""
    if suffix == '' or suffix == None:
        config = { 'series': 'a', 'trajectory': int(cfg) }
    else:
        config = { 'series': suffix, 'trajectory': int(cfg) }
    return '%(series)s%(trajectory)06d' % config

######################################################################
def codeTsrcCfg(tsrcConfigId):
    """Encode tsrc and cfg for file names"""
    (tsrc, suffix, cfg) = tsrcConfigId
    configId = codeCfg(suffix, cfg)
    return 't%d.%s' % (tsrc, configId)
######################################################################
def codeTsrcSym(tsrcConfigId,kjob):
    """Encode tsrc and kjob for file names"""
    (tsrc, suffix, cfg) = tsrcConfigId
    return 't%d.j%02d' % (tsrc, kjob)
######################################################################
def ensFile(pfx, run, tsrcConfigId):
    """Standard file name pattern containing the ensemble name, time source, and configuration"""
    sfx = codeTsrcCfg(tsrcConfigId)
    return  '%s_%s_%s' % (pfx, run, sfx)

######################################################################
def milc2FNAL(suffix, cfg):
    """Convert MILC cfg to FNAL"""
    leading = 0
    if suffix == 'b':
        leading = 5
    elif suffix == 'c':
        leading = 6
    return '%d%05d' % (leading, cfg)

######################################################################
def rndFile(sq, run, tsrcConfigId):
    """Construct random source name"""
    return ensFile('rnd' + sq, run, tsrcConfigId)

######################################################################
def latFileCoul( run, suffix, cfg):
    """Convention for Coulomb-gauge-fixed lattice file names"""
    return 'l%s%s-Coul.%d.ildg' % (run, suffix, int(cfg))

######################################################################
def latFileEig( run, suffix, cfg):
    """Convention for eigenpair file names"""
    return 'eigPRIMME%snv600er10%s.%d' % (run, suffix, int(cfg))

######################################################################
def latFileMILCv5( run, suffix, cfg):
    """Convention for MILC v5 lattice file names"""
    return 'l%s%s.%d' % (run, suffix, int(cfg))

######################################################################
def propNameKS(qkKey, run, tsrcConfigId):
    """Construct KS propagator file name"""
    return ensFile( 'prop_' + qkKey, run, tsrcConfigId )

######################################################################
def propNameClover(qkKey, run, tsrcConfigId):
    """Construct KS propagator file name"""
    return ensFile( 'prop_' + qkKey, run, tsrcConfigId )

######################################################################
def corr3ptFileName(chan, run, extT, tsrcConfigId):
    """Construct 3pt correlator file name"""
    (tsrc, suffix, cfg) = tsrcConfigId
    return 'corr3pt_T%d_%s' % (extT,  codeCfg(suffix, cfg))

######################################################################
def corr2ptFileName(chan, run, tsrcConfigId):
    """Construct 2pt correlator file name"""
    (tsrc, suffix, cfg) = tsrcConfigId
    return 'corr2pt_%s' % codeCfg(suffix, cfg)

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
    return 'p%d%d%d' % tuple(mom)
    
######################################################################
def massSubdir2pt(mQk, mAQk, mom):
    """Construct subdirectory name for 2pt correlator files"""
    return '-'.join([mQk, mAQk, momLabel(mom)])

######################################################################
def massSubdir3pt(mQkS, mQkP, mQkD, mom):
    """Construct subdirectory name for 2pt correlator files"""
    return '-'.join([mQkP, mQkS, mQkD, momLabel(mom)])

######################################################################
def logFileName(run, tsrcConfigId, jobid, tag, seqno):
    """Construct log file (stdout) name"""
    (tsrc, suffix, cfg) = tsrcConfigId
    # return 'logJob%s_%s_%s' % (jobid, seqno, codeTsrcCfg(tsrcConfigId))
    return 'logJob%s%s.%s' % (tag, jobid, codeCfg(suffix, cfg))

######################################################################
def logFileSymLink(run, tsrcConfigId, jobid, tag, seqno, kjob, njobs):
    """Construct log file (stdout) name"""
    (tsrc, suffix, cfg) = tsrcConfigId
    if njobs == 1:
        return None
    else:
        return 'logJob%s%s_%s_%s' % (tag, jobid, seqno, codeTsrcSym(tsrcConfigId, kjob))

######################################################################
def outFileName(run, tsrcConfigId, jobid, tag, seqno):
    """Construct log file (stdout) name"""
    return 'outJob%s%s_%s_%s' % (tag, jobid, seqno, codeTsrcCfg(tsrcConfigId))

######################################################################
def outFileSymLink(run, tsrcConfigId, jobid, tag, seqno, kjob, njobs):
    """Construct log file (stdout) name"""
    if njobs == 1:
        return None
    else:
        return 'outJob%s%s_%s_%s' % (tag, jobid, seqno, codeTsrcSym(tsrcConfigId, kjob))

######################################################################
def errFileName(run, tsrcConfigId, jobid, tag, seqno):
    """Construct error file (stderr) name"""
    return 'errJob%s%s_%s_%s' % (tag, jobid, seqno, codeTsrcCfg(tsrcConfigId))

######################################################################
def errFileSymLink(run, tsrcConfigId, jobid, tag, seqno, kjob, njobs):
    """Construct error file (stderr) name"""
    if njobs == 1:
        return None
    else:
        return 'errJob%s%s_%s_%s' % (tag, jobid, seqno, codeTsrcSym(tsrcConfigId, kjob))

######################################################################
def inFileName(run, tsrcConfigId, jobid, tag, seqno):
    """Construct input file (stdin) name"""
    return 'inJob%s%s_%s_%s' % (tag, jobid, seqno, codeTsrcCfg(tsrcConfigId))

######################################################################
def inFileSymLink(run, tsrcConfigId, jobid, tag, seqno, kjob, njobs):
    """Construct input file (stdin) name"""
    if njobs == 1:
        return None
    else:
        return 'inJob%s%s_%s_%s' % (tag, jobid, seqno, codeTsrcSym(tsrcConfigId, kjob))

######################################################################
def tarFileName(configId, jobid, tag):
    """Construct tar file name"""
    (suffix, cfg) = configId
    return 'Job%s%s_%s.tar.bz2' % (tag, jobid, codeCfg(suffix, cfg))


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

