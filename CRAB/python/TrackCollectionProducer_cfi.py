import FWCore.ParameterSet.Config as cms

TrackCollection = cms.EDProducer('TrackCollectionProducer',
                                 PFCandidateTag = cms.InputTag('packedPFCandidates::RECO'),
                                 LostTrackTag = cms.InputTag('lostTracks::RECO')
                                 )
