from WMCore.Configuration import Configuration  
config = Configuration()  

config.section_("General")  
config.General.requestName = 'BuTau3Mu_bjoshi_CRAB3_MC2018_BuTau3Mu_13TeV_DIGI_87600497c2c6a5767aee5d92666e59c3_USER'
config.General.workArea =  'MIANIAOD_Generation_15_12_20' 
config.General.transferLogs = True 

config.section_("JobType") 
config.JobType.allowUndistributedCMSSW = True 
config.JobType.pluginName = 'Analysis' 
config.JobType.psetName = 'miniAOD-prod_PAT.py'  

config.section_("Data")  

config.Data.inputDataset = '/BuTau3Mu/bjoshi-CRAB3_MC2018_BuTau3Mu_13TeV_DIGI-87600497c2c6a5767aee5d92666e59c3/USER' 
config.Data.inputDBS  = 'phys03' 
config.Data.splitting = 'FileBased' 
config.Data.unitsPerJob = 1 
config.Data.totalUnits = -1 
#config.Data.lumiMask = 'Cert_314472-325175_13TeV_17SeptEarlyReReco2018ABC_PromptEraD_Collisions18_JSON.txt' 
config.Data.publication = True 
config.Data.outLFNDirBase = '/store/user/bjoshi' 
config.Data.outputDatasetTag = '' 

config.section_("Site") 
#config.Site.whitelist = ['T2_US_Wisconsin','T2_US_Purdue','T1_US_FNAL'] 
#config.Data.ignoreLocality = True 
config.Site.storageSite = 'T2_US_Florida' 
