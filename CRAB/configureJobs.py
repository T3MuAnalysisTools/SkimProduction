#!/usr/bin/env python

import os
import sys
import argparse

def setcrabconfig2(DataSets,JobTags,DataMCTypes,ProdInstance,GlobalTags, prodtag, Site, OutputPath, LumiMask):
    submitall=open("SubmitAllByCrab.sh","w")
    reportall=open("ReportAllByCrab.sh","w")
    statusall=open("CheckStatusAllByCrab.sh","w")
    for (datasets, jobtag, dmctype, prodintance, gt) in zip(DataSets,JobTags,DataMCTypes,ProdInstance,GlobalTags):
        runNtupleFileName = "runNtuple_"+str(dmctype)+".py"
        with open('runNtuple_template.py', 'r') as file :
            filedata = file.read()
            filedata = filedata.replace('<GT>', gt)
            filedata = filedata.replace('<DMCType>', dmctype)
            if "data"  in dmctype:  
                filedata = filedata.replace('<MC>', str(False))
                filedata = filedata.replace('<MCFull>', str(False))
            elif "minbias"  in dmctype:  
                filedata = filedata.replace('<MC>', str(True))
                filedata = filedata.replace('<MCFull>', str(True))
            else:
                filedata = filedata.replace('<MC>', str(True))
                filedata = filedata.replace('<MCFull>', str(False))
            with open(runNtupleFileName, 'w') as file:
                file.write(filedata)
        outputdatatag = prodtag+"_"+jobtag
        crabname = "crab_"+outputdatatag+".py"
        submitall.write("crab submit -c %s\n" % crabname)
        reportall.write("crab report "+prodtag+"/%s\n" % jobtag)
        statusall.write("crab status -d "+prodtag+"/%s --long\n" % jobtag)
        crabconf=open(crabname,"w")
        crabconf.write ("from WMCore.Configuration import Configuration  \n")
        crabconf.write ("config = Configuration()  \n\n")
        crabconf.write ("config.section_(\"General\")  \n")
        crabconf.write ("config.General.requestName = '"+jobtag+"'\n")
        crabconf.write ("config.General.workArea =  '%s' \n" %  prodtag)
        crabconf.write ("config.General.transferLogs = True \n\n")
        crabconf.write ("config.section_(\"JobType\") \n")
        crabconf.write ("config.JobType.allowUndistributedCMSSW = True \n")
        crabconf.write ("config.JobType.pluginName = 'Analysis' \n")
        crabconf.write ("config.JobType.psetName = '%s'  \n\n"  % runNtupleFileName)
        crabconf.write ("config.section_(\"Data\")  \n\n")
        crabconf.write ("config.Data.inputDataset = '%s' \n" % str(datasets) )
        crabconf.write ("config.Data.inputDBS  = '%s' \n" % str(prodintance) )
        if "data" in dmctype:
            crabconf.write ("config.Data.splitting = 'LumiBased' \n")
            crabconf.write ("config.Data.unitsPerJob = 100 \n")
        else:
            crabconf.write ("config.Data.splitting = 'FileBased' \n")
            crabconf.write ("config.Data.unitsPerJob = 5 \n")
        crabconf.write ("config.Data.totalUnits = -1 \n")
        if "data" in dmctype:
            crabconf.write ("config.Data.lumiMask = '%s' \n" % LumiMask)
        else:
            crabconf.write ("#config.Data.lumiMask = '%s' \n" % LumiMask)
        crabconf.write ("config.Data.publication = True \n")
        crabconf.write ("config.Data.outLFNDirBase = '%s' \n" % OutputPath)
        crabconf.write ("config.Data.outputDatasetTag = '%s' \n\n" % outputdatatag )
        crabconf.write ("config.section_(\"Site\") \n")
        crabconf.write ("#config.Site.whitelist = ['T2_US_Wisconsin','T2_US_Purdue','T1_US_FNAL'] \n" )
        crabconf.write ("#config.Data.ignoreLocality = True \n" )
        crabconf.write ("config.Site.storageSite = '%s' \n" % Site)
        


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--input-file",help="input file; [Default: %(default)s] ", action="store", default = 'datasets.dat')
    parser.add_argument("-t", "--tag",help="Tag the production; [Default: %(default)s] ",  type=str, action="store", default = '2019DataProduction')
    parser.add_argument("-s", "--site-run",help="Site to run; [Default: %(default)s] ",  type=str, action="store", default = 'T2_US_Florida')
    parser.add_argument("-o", "--path-to-store",help="Path to store the output files; [Default: %(default)s] ",  type=str, action="store", default = '/store/user/cherepan')
    parser.add_argument("-j", "--json",help="LumiMask JSON file; [Default: %(default)s] ",  type=str, action="store", default = 'Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt')
    args = parser.parse_args()

    datasetsFile = args.input_file
    if not os.path.isfile(datasetsFile):
        print "File %s not found!!!" % datasetsFile
        sys.exit()

    crabJobsFolder = "crab_" + args.tag
    if os.path.isdir(crabJobsFolder):
        print "Folder %s already exists, please change tag name or delete it" % crabJobsFolder
        sys.exit()
    os.system ("voms-proxy-init -voms cms")
    DataSets = []
    GlobalTags = []
    ProdInstance = []
    DataMCTypes = []
    JobTags = []
    with open(datasetsFile) as fIn:
        for line in fIn:
            line = line.strip()
            if not line:
                continue
            if '#' in line:
                continue
            if "<GT>" in line:
                GT = line.split(":")
            if "Path" in line:
                DataSets.append(line.split(":")[1].strip())
                JT=(line.split(":")[1]).split("/")[1].strip()+"__"+(line.split(":")[1]).split("/")[2].strip()
                if len(JT) > 100:
                    JobTags.append( JT[:99])
                else:
                    JobTags.append( JT)

            if "DataMCType" in line:
                DataMCTypes.append(line.split(":")[1].strip())

            if "Prod" in line:
                PI = line.split(":")
                ProdInstance.append(line.split(":")[1].strip())
            if "GT" in line:
                GlobalTags.append(line.split(":")[1].strip())
    sizelist=[len(DataSets),len(JobTags), len(DataMCTypes), len(ProdInstance), len(GlobalTags)]
    if not all(number == sizelist[0] for number in sizelist):
        print "Something is not right with your config file; Please check again your ",datasetsFile
        sys.exit()
    print "====================== "
    print "Data/MC Sample to be configured: "
    for n in DataSets:
        print "--->  ", n
    setcrabconfig2(DataSets,JobTags,DataMCTypes,ProdInstance,GlobalTags,args.tag,args.site_run, args.path_to_store,args.json)   



    print "\n\nDo 'source SubmitAllByCrab.sh'  to submit all jobs" 
    print "Do 'source CheckStatusAllByCrab.sh'  to check the status of all jobs" 
    print "Do 'source ReportAllByCrab.sh'  to report  all jobs " 
    print "\nFor help with crab3  consult with  https://twiki.cern.ch/twiki/bin/view/CMSPublic/CRAB3AdvancedTutorial  \n\n"
#    print "Run a small scale job before submitting ! \n" 

