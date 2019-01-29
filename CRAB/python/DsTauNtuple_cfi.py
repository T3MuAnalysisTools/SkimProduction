import FWCore.ParameterSet.Config as cms


T3MTree = cms.EDAnalyzer('T3MNtuple',
                           mid = cms.int32(15),
                           MC = cms.bool(False),
                           passhlt = cms.bool(True),
                           wideSB = cms.bool(False),
                           do2mu = cms.bool(True), # do 2 mu category or not
                           muons = cms.InputTag("muons"),
                           pvs = cms.InputTag("offlinePrimaryVertices"),
                           svs = cms.InputTag("inclusiveSecondaryVertices"),
                           trks = cms.InputTag("generalTracks"),
                           btagsCvsB = cms.InputTag("pfCombinedCvsBJetTags"),
                           btagsMVA = cms.InputTag("pfCombinedMVAV2BJetTags"),
                           btagsCSV = cms.InputTag("pfCombinedSecondaryVertexV2BJetTags"),
                           pfcands = cms.InputTag("particleFlow"),
                           triggerBitsH = cms.InputTag("TriggerResults", "", "HLT"),
                           triggerSummary = cms.InputTag("hltTriggerSummaryAOD", "", "HLT"),
                           beamSpotHandle = cms.InputTag("offlineBeamSpot"),
                           pileupSummary = cms.InputTag("addPileupInfo"),
                           genParticles = cms.InputTag("genParticles"),
                           AlgInputTag = cms.InputTag( "gtStage2Digis" ),
                           BadGlbMuonFilter = cms.InputTag("badGlobalMuonTagger")
                           )
