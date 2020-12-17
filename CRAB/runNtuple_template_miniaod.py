import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing

import subprocess
import sys

options = VarParsing.VarParsing()
options.register('globalTag',
                 '<GT>', #default value
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "Global Tag")

options.register('nEvents',
                 500, #default value
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.int,
                 "Maximum number of processed events")

options.register('eosInputFolder',
                 '/store/relval/CMSSW_8_0_20/RelValZMM_13/GEN-SIM-RECO/PU25ns_80X_mcRun2_asymptotic_2016_TrancheIV_v4_Tr4GT_v4-v1/00000', #default value
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "EOS folder with input files")

options.register('ntupleName',
                 './DsT3MNtuple_MINIAOD.root', #default value
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "Folder and name ame for output ntuple")

options.register('runOnMC',
                 False, #default value
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.bool,
                 "Run on DATA or MC")

options.register('hltPathFilter',
                 "all", #default value
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "Filter on paths (now only accepts all or IsoMu20)")

if options.hltPathFilter == "all" :
    pathCut   = "all"
    filterCut = "all"
elif options.hltPathFilter == "IsoMu20" :
    pathCut   = "HLT_IsoMu20_v"
    if options.runOnMC :
        filterCut = "hltL3crIsoL1sMu16L1f0L2f10QL3f20QL3trkIsoFiltered0p09"
    else :
        filterCut = "hltL3crIsoL1sMu18L1f0L2f10QL3f20QL3trkIsoFiltered0p09"
        
else :
    print "[" + sys.argv[0] + "]:", "hltPathFilter=", options.hltPathFilter, "is not a valid parameter!"
    sys.exit(100)


process = cms.Process("DsTauNtuple")



process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(10000)

process.load("TrackingTools/TransientTrack/TransientTrackBuilder_cfi")
process.load('Configuration.Geometry.GeometrySimDB_cff')

process.load("Configuration.StandardSequences.GeometryRecoDB_cff")
process.load("Configuration.StandardSequences.MagneticField_38T_cff")
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
from Configuration.AlCa.GlobalTag_condDBv2 import GlobalTag
process.GlobalTag.globaltag = cms.string(options.globalTag)

process.load('RecoMET.METFilters.badGlobalMuonTaggersAOD_cff')
#switch on tagging mode:
process.badGlobalMuonTagger.taggingMode = cms.bool(True)
process.cloneGlobalMuonTagger.taggingMode = cms.bool(True)

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1000) )

process.load("FWCore.MessageService.MessageLogger_cfi")
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(options.nEvents)  )
process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring(),
        secondaryFileNames = cms.untracked.vstring()
)

process.load('DsTau23Mu.T3MNtuple.TrackCollectionProducer_cfi')

process.unpackedPatTrigger = cms.EDProducer('PATTriggerObjectStandAloneUnpacker',
                                            patTriggerObjectsStandAlone = cms.InputTag( 'slimmedPatTrigger' ),
                                            triggerResults              = cms.InputTag( 'TriggerResults::HLT' ),
                                            unpackFilterLabels = cms.bool(True))

process.TFileService = cms.Service('TFileService',
                                   fileName = cms.string("DsT3MNtuple.root")
                                   )


process.source.fileNames = ['/store/data/Run2018D/DoubleMuonLowMass/MINIAOD/PromptReco-v2/000/325/159/00000/1403B072-371A-764C-9B25-A172D8B1A884.root'] #data
#process.source.fileNames = [''] #minbias
#process.source.fileNames = ['/store/user/wangjian/DsToTau_TauTo3Mu_November2020/RunIIAutumn18MiniAOD-102X/201107_171229/0000/BPH-RunIIAutumn18MiniAOD-00158_144.root'] #ds_tau
#process.source.fileNames = [''] #bd_tau
#process.source.fileNames = ['/store/user/wangjian/BpToTau_TauTo3Mu_November2020/RunIIAutumn18MiniAOD-102X/201112_084651/0000/BPH-RunIIAutumn18MiniAOD-00158_339.root'] #bu_tau
#process.source.fileNames = ['/store/mc/RunIIFall17MiniAODv2/DsToPhiPi_ToMuMu_MuFilter_TuneCUEP8M1_13TeV-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/50000/76D80325-41C0-E911-9905-AC1F6BAC7C0A.root'] #ds_phipi

####################### TauNtuple (MINIAOD version) ######################
from SkimProduction.CRAB.NtupleConfig_cff import setupTauNtuple
setupTauNtuple(process)
process.T3MTree.miniAODRun = cms.bool(True)
process.T3MTree.DataMCType = cms.untracked.string('<DMCType>')
process.T3MTree.doMC = cms.bool(<MC>)
process.T3MTree.doFullMC = cms.bool(<MCFull>)
process.T3MTree.btagsCvsB = cms.InputTag('none')
process.T3MTree.btagsMVA = cms.InputTag('none')
process.T3MTree.btagsCSV = cms.InputTag('none')
process.T3MTree.btagDeepCSV = cms.InputTag('none')  # absent in AOD/MINIAOD
process.T3MTree.triggerSummary = cms.InputTag('none')
process.T3MTree.trks = cms.InputTag('TrackCollection:pfTracks:DsTauNtuple')
process.T3MTree.pvs = cms.InputTag("offlineSlimmedPrimaryVertices")
process.T3MTree.triggerObjects = cms.InputTag('unpackedPatTrigger')
process.T3MTree.genParticles = cms.InputTag('prunedGenParticles::PAT')
process.T3MTree.pileupSummary = cms.InputTag('slimmedAddPileupInfo')

process.TrackCollection.PFCandidateTag = cms.InputTag('<PFCandidateTag>')
process.TrackCollection.LostTrackTag = cms.InputTag('<LostTrackTag>')

#process.tagger = cms.Path(process.badGlobalMuonTagger)
process.DsTauNtuple = cms.Sequence(process.T3MTree)
process.p = cms.Path(process.TrackCollection * process.unpackedPatTrigger * process.DsTauNtuple)
process.schedule = cms.Schedule(process.p)
