from CRABClient.UserUtilities import config, getUsernameFromSiteDB
config = config()

config.General.requestName = 'minBias_pythia8_MC_generation_1MEvents_005'
config.General.workArea = 'crab_projects'
config.General.transferOutputs = True
config.General.transferLogs = False

config.JobType.pluginName = 'PrivateMC'
config.JobType.psetName = 'MinBias_13TeV_config_test.py'

config.Data.outputPrimaryDataset = 'MinBias_Pythia8_1MEvents_005'
config.Data.splitting = 'EventBased'
config.Data.unitsPerJob = 1000 
NJOBS = 50  # This is not a configuration parameter, but an auxiliary variable that we use in the next line.
config.Data.totalUnits = config.Data.unitsPerJob * NJOBS
config.Data.outLFNDirBase = '/store/user/%s/' % (getUsernameFromSiteDB())
config.Data.publication = True
config.Data.outputDatasetTag = 'MinBias_Pythia8_1MEvents_005'

config.Site.storageSite = 'T2_US_Florida'
