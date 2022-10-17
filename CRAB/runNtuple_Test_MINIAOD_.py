import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing

import subprocess
import sys

options = VarParsing.VarParsing()
options.register('globalTag',
                 '102X_upgrade2018_realistic_v21', #default value
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "Global Tag")

options.register('nEvents',
                 -1, #default value
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

process.bareTaus = cms.EDFilter("PATTauRefSelector",
   src = cms.InputTag("slimmedTaus"),
   cut = cms.string("tauID('byCombinedIsolationDeltaBetaCorrRaw3Hits') < 1000.0 && pt>18") #miniAOD tau from hpsPFTauProducer have pt>18 and decaymodefinding ID
   )
   
process.goodPrimaryVertices = cms.EDFilter("VertexSelector",
  src = cms.InputTag("offlineSlimmedPrimaryVertices"),
  cut = cms.string("!isFake && ndof > 4 && abs(z) <= 24 && position.Rho <= 2"), #cut on good primary vertexes
  filter = cms.bool(False), # if True, rejects events . if False, produce emtpy vtx collection
)

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

#Begin Tau Tagging (for MiniAOD)

from RecoTauTag.RecoTau.TauDiscriminatorTools import noPrediscriminants
process.load('RecoTauTag.Configuration.loadRecoTauTagMVAsFromPrepDB_cfi')
from RecoTauTag.RecoTau.PATTauDiscriminationByMVAIsolationRun2_cff import *

process.rerunDiscriminationByIsolationMVArun2v1raw = patDiscriminationByIsolationMVArun2v1raw.clone(
   PATTauProducer = cms.InputTag('slimmedTaus'),
   Prediscriminants = noPrediscriminants,
   loadMVAfromDB = cms.bool(True),
   mvaName = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1"), # name of the training you want to use
   mvaOpt = cms.string("DBoldDMwLT"), # option you want to use for your training (i.e., which variables are used to compute the BDT score)
   verbosity = cms.int32(0)
)

process.rerunDiscriminationByIsolationMVArun2v1VLoose = patDiscriminationByIsolationMVArun2v1VLoose.clone(
   PATTauProducer = cms.InputTag('slimmedTaus'),    
   Prediscriminants = noPrediscriminants,
   toMultiplex = cms.InputTag('rerunDiscriminationByIsolationMVArun2v1raw'),
   key = cms.InputTag('rerunDiscriminationByIsolationMVArun2v1raw:category'),
   loadMVAfromDB = cms.bool(True),
   mvaOutput_normalization = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_mvaOutput_normalization"), # normalization fo the training you want to use
   mapping = cms.VPSet(
      cms.PSet(
         category = cms.uint32(0),
         cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_WPEff90"), # this is the name of the working point you want to use
         variable = cms.string("pt"),
      )
   )
)

# here we produce all the other working points for the training
process.rerunDiscriminationByIsolationMVArun2v1Loose = process.rerunDiscriminationByIsolationMVArun2v1VLoose.clone()
process.rerunDiscriminationByIsolationMVArun2v1Loose.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_WPEff80")
process.rerunDiscriminationByIsolationMVArun2v1Medium = process.rerunDiscriminationByIsolationMVArun2v1VLoose.clone()
process.rerunDiscriminationByIsolationMVArun2v1Medium.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_WPEff70")
process.rerunDiscriminationByIsolationMVArun2v1Tight = process.rerunDiscriminationByIsolationMVArun2v1VLoose.clone()
process.rerunDiscriminationByIsolationMVArun2v1Tight.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_WPEff60")
process.rerunDiscriminationByIsolationMVArun2v1VTight = process.rerunDiscriminationByIsolationMVArun2v1VLoose.clone()
process.rerunDiscriminationByIsolationMVArun2v1VTight.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_WPEff50")
process.rerunDiscriminationByIsolationMVArun2v1VVTight = process.rerunDiscriminationByIsolationMVArun2v1VLoose.clone()
process.rerunDiscriminationByIsolationMVArun2v1VVTight.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_WPEff40")

# this sequence has to be included in your cms.Path() before your analyzer which accesses the new variables is called.
process.rerunMvaIsolation2SeqRun2 = cms.Sequence(
   process.rerunDiscriminationByIsolationMVArun2v1raw
   *process.rerunDiscriminationByIsolationMVArun2v1VLoose
   *process.rerunDiscriminationByIsolationMVArun2v1Loose
   *process.rerunDiscriminationByIsolationMVArun2v1Medium
   *process.rerunDiscriminationByIsolationMVArun2v1Tight
   *process.rerunDiscriminationByIsolationMVArun2v1VTight
   *process.rerunDiscriminationByIsolationMVArun2v1VVTight
)

# embed new id's into new tau collection
embedID = cms.EDProducer("PATTauIDEmbedder",
   src = cms.InputTag('slimmedTaus'),
   tauIDSources = cms.PSet(
      byIsolationMVArun2v1DBoldDMwLTrawNew = cms.InputTag('rerunDiscriminationByIsolationMVArun2v1raw'),
      byVLooseIsolationMVArun2v1DBoldDMwLTNew = cms.InputTag('rerunDiscriminationByIsolationMVArun2v1VLoose'),
      byLooseIsolationMVArun2v1DBoldDMwLTNew = cms.InputTag('rerunDiscriminationByIsolationMVArun2v1Loose'),
      byMediumIsolationMVArun2v1DBoldDMwLTNew = cms.InputTag('rerunDiscriminationByIsolationMVArun2v1Medium'),
      byTightIsolationMVArun2v1DBoldDMwLTNew = cms.InputTag('rerunDiscriminationByIsolationMVArun2v1Tight'),
      byVTightIsolationMVArun2v1DBoldDMwLTNew = cms.InputTag('rerunDiscriminationByIsolationMVArun2v1VTight'),
      byVVTightIsolationMVArun2v1DBoldDMwLTNew = cms.InputTag('rerunDiscriminationByIsolationMVArun2v1VVTight'),
      )
   )
setattr(process, "NewTauIDsEmbedded", embedID)

#End Tau Tagging

import RecoVertex.PrimaryVertexProducer.OfflinePrimaryVertices_cfi
process.offlinePrimaryVertices = RecoVertex.PrimaryVertexProducer.OfflinePrimaryVertices_cfi.offlinePrimaryVertices.clone()

from RecoTauTag.RecoTau.RecoTauCombinatoricProducer_cfi import combinatoricRecoTaus
process.combinatoricRecoTaus = combinatoricRecoTaus.clone()

from RecoTauTag.RecoTau.RecoTauCleaner_cfi import RecoTauCleaner
process.hpsPFTauProducerSansRefs = RecoTauCleaner.clone(
    src = cms.InputTag("combinatoricRecoTaus")
)
process.hpsPFTauProducerSansRefs.cleaners[1].src = cms.InputTag("hpsSelectionDiscriminator")

from RecoTauTag.RecoTau.RecoTauPiZeroUnembedder_cfi import RecoTauPiZeroUnembedder
process.hpsPFTauProducer = RecoTauPiZeroUnembedder.clone(
    src = cms.InputTag("hpsPFTauProducerSansRefs")
)

## Selection of taus that pass the HPS selections: pt > 15, mass cuts, tauCone cut
from RecoTauTag.RecoTau.PFRecoTauDiscriminationByHPSSelection_cfi import hpsSelectionDiscriminator, decayMode_1Prong0Pi0, decayMode_1Prong1Pi0, decayMode_1Prong2Pi0, decayMode_2Prong0Pi0, decayMode_2Prong1Pi0, decayMode_3Prong0Pi0, decayMode_3Prong1Pi0

process.hpsPFTauDiscriminationByDecayModeFindingNewDMs = hpsSelectionDiscriminator.clone(
    PFTauProducer = cms.InputTag('hpsPFTauProducer'),
    decayModes = cms.VPSet(
        decayMode_1Prong0Pi0,
        decayMode_1Prong1Pi0,
        decayMode_1Prong2Pi0,
        decayMode_2Prong0Pi0,
        decayMode_2Prong1Pi0,
        decayMode_3Prong0Pi0,
        decayMode_3Prong1Pi0,
    )
)

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


#process.source.fileNames = ['/store/data/Run2018D/DoubleMuonLowMass/MINIAOD/PromptReco-v2/000/325/159/00000/1403B072-371A-764C-9B25-A172D8B1A884.root'] #data

#process.source.fileNames = ['/store/user/wangjian/DsToTau_TauTo3Mu_November2020/RunIIAutumn18MiniAOD-102X/201107_171229/0000/BPH-RunIIAutumn18MiniAOD-00158_980.root',   # ds to tau
#                            '/store/user/wangjian/DsToTau_TauTo3Mu_November2020/RunIIAutumn18MiniAOD-102X/201107_171229/0000/BPH-RunIIAutumn18MiniAOD-00158_981.root',
#                            '/store/user/wangjian/DsToTau_TauTo3Mu_November2020/RunIIAutumn18MiniAOD-102X/201107_171229/0000/BPH-RunIIAutumn18MiniAOD-00158_982.root']

#process.source.fileNames = ['file:/afs/cern.ch/work/m/mmadhu/4B536A0D-9E6B-2249-906C-0501C109F09D.root'] #Z to Tau miniaod sample

#process.source.fileNames = ['/store/mc/RunIIAutumn18MiniAOD/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/MINIAODSIM/102X_upgrade2018_realistic_v15-v1/00000/0038605E-C94B-574F-AF1F-000435E9A26E.root']

#process.source.fileNames = ['file:0038605E-C94B-574F-AF1F-000435E9A26E.root']

process.source.fileNames = ['/store/user/cherepan/z2tautau_3mu_GEN_KinFit/z2tautau_3mu_GEN_KinFit14_03_2020_MiniAOD/220721_102947/0000/z2tautau_3mu_GEN_KinFit_MiniAOD_1.root']


#process.source.fileNames = ['/cmsuf/data/store/user/wangjian/BpToTau_TauTo3Mu_November2020/RunIIAutumn18MiniAOD-102X/201112_084651/0000/BPH-RunIIAutumn18MiniAOD-00158_70.root', # bp to tau
#                            '/cmsuf/data/store/user/wangjian/BpToTau_TauTo3Mu_November2020/RunIIAutumn18MiniAOD-102X/201112_084651/0000/BPH-RunIIAutumn18MiniAOD-00158_71.root']


#process.source.fileNames = ['/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_501.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_502.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_503.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_504.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_505.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_506.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_507.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_508.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_509.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_510.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_511.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_512.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_513.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_514.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_515.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_516.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_517.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_518.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_519.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_520.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_521.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_522.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_523.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_524.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_525.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_526.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_527.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_528.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_529.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_530.root',
#                            '/store/user/wangjian/B0ToTau_TauTo3Mu/RunIIAutumn18MiniAOD-102X/200324_184847/0000/BPH-RunIIAutumn18MiniAOD-00276_531.root']



#process.source.fileNames = [''] #minbias
#process.source.fileNames = ['/store/user/wangjian/DsToTau_TauTo3Mu_November2020/RunIIAutumn18MiniAOD-102X/201107_171229/0000/BPH-RunIIAutumn18MiniAOD-00158_144.root'] #ds_tau
#process.source.fileNames = [''] #bd_tau
#process.source.fileNames = ['/store/user/wangjian/BpToTau_TauTo3Mu_November2020/RunIIAutumn18MiniAOD-102X/201112_084651/0000/BPH-RunIIAutumn18MiniAOD-00158_339.root'] #bu_tau
#process.source.fileNames = ['/store/mc/RunIIFall17MiniAODv2/DsToPhiPi_ToMuMu_MuFilter_TuneCUEP8M1_13TeV-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/50000/76D80325-41C0-E911-9905-AC1F6BAC7C0A.root'] #ds_phipi

####################### TauNtuple (MINIAOD version) ######################
from SkimProduction.CRAB.NtupleConfig_cff import setupTauNtuple
setupTauNtuple(process)
process.T3MTree.miniAODRun = cms.bool(True)
process.T3MTree.DataMCType = cms.untracked.string('z2tautau_tau3mu')
process.T3MTree.doMC = cms.bool(True)
process.T3MTree.doFullMC = cms.bool(False)
process.T3MTree.doTaus = cms.bool(True)
process.T3MTree.btagsCvsB = cms.InputTag('none')
process.T3MTree.btagsMVA = cms.InputTag('none')
process.T3MTree.btagsCSV = cms.InputTag('none')
process.T3MTree.btagDeepCSV = cms.InputTag('none')  # absent in AOD/MINIAOD
process.T3MTree.triggerSummary = cms.InputTag('none')
process.T3MTree.trks = cms.InputTag('TrackCollection:pfTracks:DsTauNtuple')
process.T3MTree.pvs = cms.InputTag("offlineSlimmedPrimaryVertices")
process.T3MTree.triggerObjects = cms.InputTag('unpackedPatTrigger')
process.T3MTree.genParticles = cms.InputTag('prunedGenParticles')
process.T3MTree.pileupSummary = cms.InputTag('slimmedAddPileupInfo')


process.TrackCollection.PFCandidateTag = cms.InputTag('packedPFCandidates')
process.TrackCollection.LostTrackTag = cms.InputTag('lostTracks')

#process.tagger = cms.Path(process.badGlobalMuonTagger)


process.DsTauNtuple = cms.Sequence(process.T3MTree)


updatedTauName = "slimmedTausPlusDeepTau" #name of pat::Tau collection with new tau-Ids
import RecoTauTag.RecoTau.tools.runTauIdMVA as tauIdConfig
tauIdEmbedder = tauIdConfig.TauIDEmbedder(process, cms, debug = False,
                    updatedTauName = updatedTauName,
                    toKeep = ["deepTau2017v2p1", #deepTau TauIDs
                               ])
tauIdEmbedder.runTauID()
# Path and EndPath definitions


#process.p = cms.Path(process.TrackCollection * process.unpackedPatTrigger *process.rerunMvaIsolation2SeqRun2 * process.NewTauIDsEmbedded * process.offlinePrimaryVertices * process.combinatoricRecoTaus * process.hpsPFTauProducerSansRefs * process.hpsPFTauProducer * process.hpsPFTauDiscriminationByDecayModeFindingNewDMs *  process.DsTauNtuple)
#process.p = cms.Path(process.TrackCollection * process.unpackedPatTrigger *process.rerunMvaIsolation2SeqRun2 * process.NewTauIDsEmbedded * process.rerunMvaIsolationSequence *  getattr(process,updatedTauName) *  process.DsTauNtuple)

process.p = cms.Path(process.TrackCollection * process.unpackedPatTrigger * process.rerunMvaIsolationSequence *  getattr(process,updatedTauName) *  process.DsTauNtuple)
process.schedule = cms.Schedule(process.p)
