#! /usr/bin/env python2.7

import sys, os, yaml, re, subprocess
from MILCprompts import *
from allHISQKeys import *
from allHISQFiles import *
from Cheetah.Template import Template


ens = "l2464f211b600m0102m0509m635"
series = "a"
latPath = "/lqcdproj/diskCache/HISQ/" + ens + "/v5"
scratchBase = '/lqcdproj/fermimilcheavylight/detar/allHISQ/' + ens + 'test'
rndPath = scratchBase + '/rand'
propPath = scratchBase + '/prop'
projectBase = '/projects/heavylight/hisq/allHISQ/a0.12/' + ens + 'test'
corrPath = projectBase + '/corr'
eigPath = projectBase + '/eigen'
Nvecs = 0
#errsLight = [ 1e-3, 1e-5, 1e-7, 1e-9 ] # Light-quark L2 residuals
errsLight = [ 1e-7 ] # Light-quark L2 residuals
errsHeavy = [ 1e-5 ] # Heavy-quark residuals (Fermilab-type)
massesL = [ 0.0102, 0.053476 ]
massesH = [ 0.6363, 1.2726,]
naiksH = [ -0.229787, -0.521 ]

######################################################################
def geometry():

    dim = [24, 24, 24, 64]
    seed = 30194
    try:
        jobID = os.environ['PBS_JOBID'].split(".").pop(0)
    except KeyError:
        jobID = "none"

    layoutSciDAC = { 'node': "1 1 1 1", 'io': "1 1 1 1" }
    work = ks_spectrum('test', dim, seed, jobID, layoutSciDAC)

    return work

######################################################################
def lattice(work, cfg):

    latName = ens + series + "." + cfg
    loadLat = ("reload_serial", latPath+"/"+latName )
    u0str = "0.8350"
    gFix = "no_gauge_fix"
    saveLat = ('forget',)
    apelink = { 'weight': 0.05, 'iter': 20 }
    uOrigin = [0, 0, 0, 0]
    bc = "antiperiodic"
    gauge = Gauge(loadLat, u0str, gFix, saveLat, apelink, uOrigin, bc)
    work.newGauge(gauge)

    return work

######################################################################
def eigen(work, seriesCfg):

    eigName = "eig_" + ens + "." + seriesCfg
    eigPathName = eigPath + "/" + eigName

    if Nvecs == 0:
        load = None
        save = None
    else:
        load = ( 'reload_serial_ks_eigen', eigPathName)
        save = ( 'forget_ks_eigen', )
        try:
            stat = os.stat(eigPathName)
        except OSError:
            load = ( 'fresh_ks_eigen', )
            save = ( 'save_parallel_ks_eigen', eigPathName)
            
    eigs = Eigen(load, Nvecs, save)
    work.newEigen(eigs)
    
    return work

######################################################################
def source(work, seriesCfg, tsrc):

    rwNcolor = 1
    rwSubset = 'corner'
    rwMom = [0, 0, 0]
    scaleFactor = None
    rwLabel = 'RW'
    rndName = "rnd_" + ens + "_" + str(tsrc) + "." + seriesCfg
    rndPathName = rndPath + "/" + rndName

    # Create the zero-momentum random wall source
    save = ("save_serial_scidac_ks_source", rndPathName)
    src = RandomColorWallSource(tsrc, rwNcolor, rwSubset, rwMom, 
                                scaleFactor, rwLabel, save )
    rwSrcDum = work.addBaseSource(src)

    # Create a reloaded random wall source
    loadRnd = ('load_source_serial', rndPathName)
    saveRnd = ('forget_source',)
    src = VectorFieldSource(loadRnd, [0,0,0,tsrc], rwNcolor, rwSubset, 
                            rwMom, scaleFactor, rwLabel, saveRnd )

    rwSrcRead = work.addBaseSource(src)

    return work, rwSrcDum, rwSrcRead

######################################################################
def dummyProp(work, rwSrcDum):

    twist = [ 0, 0, 0 ]
    check = 'sourceonly'
    maxCG = { 'iters': 10, 'restarts': 1 }
    precision = 1

    thisSet = KSsolveSet(rwSrcDum, twist, check, maxCG, precision)
    
    mass = 1.
    naik_epsilon = 0.
    load = ('fresh_ksprop',)
    save = ('forget_ksprop',)
    residual = { 'L2': 1., 'R2': 0. }

    thisQ = KSsolveElement(mass, naik_epsilon, load, save, residual)

    thisSet.addPropagator(thisQ)
    work.addPropSet(thisSet)

    return work
    
######################################################################
def KSElementL(thisSet, quarks, work, mass, naik, seriesCfg):

    load = ('fresh_ksprop',)
    for errL in errsLight:
        propName = 'prop_m' + str(mass) + '-e' + str(errL) + '_' + ens + seriesCfg
        propPathName = propPath + propName
        save = ('save_parallel_scidac_ksprop', propPathName)
        residual = { 'L2': errL, 'R2': 0. }
        thisP = KSsolveElement(mass, naik, load, save, residual)
        thisSet.addPropagator( thisP )

        thisQ  = QuarkIdentitySink( thisP, 'd', save )
        quarks[str(mass)][str(errL)] = thisQ
        work.addQuark(thisQ)
        # Set load to resume CG to continue to a smaller residual
        load = ('reload_serial_ksprop', propPathName)

    return thisSet, quarks, work

######################################################################
def KSElementH(thisSet, quarks, work, mass, naik, seriesCfg):

    load = ('fresh_ksprop',)
    for errH in errsHeavy:
        propName = 'prop_m' + str(mass) + '-e' + str(errH) + '_' + ens + seriesCfg
        propPathName = propPath + propName
        save = ('save_parallel_scidac_ksprop', propPathName)
        residual = { 'L2': 0., 'R2': errH }
        thisP = KSsolveElement(mass, naik, load, save, residual)
        thisSet.addPropagator( thisP )

        thisQ  = QuarkIdentitySink( thisP, 'd', save )
        quarks[str(mass)][str(errH)] = thisQ
        work.addQuark(thisQ)
        # Set load to resume CG to continue to a smaller residual
        load = ('reload_serial_ksprop', propPathName)

    return thisSet, quarks, work

######################################################################
def KSSet(work, rwRndRead, seriesCfg):

    twist = [ 0, 0, 0 ]
    check = 'yes'
    maxCG = { 'iters': 4000, 'restarts': 5 }
    precision = 2
    quarks = {}

    # Light-quark propagators
    for massL in massesL:
        quarks[str(massL)] = {}
        thisSet = KSsolveSet(rwRndRead, twist, check, maxCG, precision)
        thisSet, quarks, work = KSElementL(thisSet, quarks, work, massL, 0., seriesCfg)
        work.addPropSet(thisSet)
    
    # Heavy-quark propagators
    for massH, naikH in zip(massesH, naiksH):
        quarks[str(massH)] = {}
        thisSet = KSsolveSet(rwRndRead, twist, check, maxCG, precision)
        thisSet, quarks, work = KSElementH(thisSet, quarks, work, massH, naikH, seriesCfg)
        work.addPropSet(thisSet)

    return work, quarks
    
######################################################################
def meson2pts(work, quarks, tsrc, seriesCfg):

    # Make heavy-light 2pts for each mass and CG residual
    for massL in massesL:
        for massH in massesH:
            for errL in errsLight:
                for errH in errsHeavy:
                    npts = list()
                    prefix = 'H5_e' + str(errL) + '_' + str(errH) + '_'
                    pmom = 'p000'
                    phase = 1
                    rwNorm = 1.
                    stSnk = 'G5-G5'
                    om = [0, 0, 0]
                    thisNpt = MesonNpt(prefix, pmom, (phase,'/',rwNorm), 
                                       [stSnk], om, ('EO','EO','EO'))
                    npts.append( thisNpt )
                    
                    # Generate the pair stanza
                    quarkL = quarks[str(massL)][str(errL)]
                    quarkH = quarks[str(massH)][str(errH)]
                    rOffset = [0,0,0,tsrc]
                    corrName = "corr2pt." + seriesCfg
                    corrPathName = corrPath + '/' + corrName
                    spectSave = ( 'save_corr_fnal', corrPathName )
                    spect = MesonSpectrum(quarkL, quarkH, rOffset, npts, spectSave)
                    work.addMeson(spect)

    return work


######################################################################
def main():

    # Geometry: non-repeating stanza
    work = geometry()

    # Iterate over cfgs
    for cfgno in range(1000, 1005, 5):
        cfg = str(cfgno)
        seriesCfg = codeCfg(series,cfg) # Combines series and cfg number
        work = lattice(work, cfg)
        work = eigen(work, seriesCfg)

        # Iterate over source times
        for tsrc in range(0, 12, 12):
            work, rwSrcDum, rwSrcRead = source(work, seriesCfg, tsrc)
            work = dummyProp(work, rwSrcDum)
            work, quarks = KSSet(work, rwSrcRead, seriesCfg)
            work = meson2pts(work, quarks ,tsrc, seriesCfg)
            
    work.generate()

######################################################################
main()
