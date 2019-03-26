#!/usr/bin/env python

import os
import sys
import argparse


def setcrabconfig2(DataSets,JobTags,DataMCTypes,ProdInstance,GlobalTags, prodtag, Site, OutputPath):
    submitall=open("SubmitAllByCrab.sh","w")
    for (datasets, jobtag, dmctype, prodintance, gt) in zip(DataSets,JobTags,DataMCTypes,ProdInstance,GlobalTags):
        runNtupleFileName = "runNtuple_"+str(dmctype)+".py"
        with open('runNtuple_template.py', 'r') as file :
            filedata = file.read()
            filedata = filedata.replace('<GT>', gt)
            filedata = filedata.replace('<DMCType>', dmctype)
            if "data"  in dmctype:  
                filedata = filedata.replace('<MC>', str(False))
            else:
                filedata = filedata.replace('<MC>', str(True))
            with open(runNtupleFileName, 'w') as file:
                file.write(filedata)
        outputdatatag = prodtag+"_"+jobtag
        crabname = "crab_"+outputdatatag+".py"
        submitall.write("crab submit -c %s\n" % crabname)
        crabconf=open(crabname,"w")
        crabconf.write ("from WMCore.Configuration import Configuration  \n")
        crabconf.write ("config = Configuration()  \n\n")
        crabconf.write ("config.section_(\"General\")  \n")
        crabconf.write ("config.General.requestName = '"+jobtag+"'\n")
        crabconf.write ("config.General.workArea =  '%s' \n\n" %  prodtag)
        crabconf.write ("config.section_(\"JobType\") \n")
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
            crabconf.write ("config.Data.unitsPerJob = 200 \n")
        crabconf.write ("config.Data.totalUnits = -1 \n")
        if "data" in dmctype:
            crabconf.write ("config.Data.lumiMask = 'Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt' \n")
        else:
            crabconf.write ("#config.Data.lumiMask = 'Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt' \n")
        crabconf.write ("config.Data.publication = True \n")
        crabconf.write ("config.Data.outLFNDirBase = '%s' \n" % OutputPath)
        crabconf.write ("config.Data.outputDatasetTag = '%s' \n\n" % outputdatatag )
        crabconf.write ("config.section_(\"Site\") \n")
        crabconf.write ("config.Site.storageSite = '%s' \n" % Site)
        


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--input-file",help="input file; [Default: %(default)s] ", action="store", default = 'datasets.dat')
    parser.add_argument("-t", "--tag",help="Tag the production; [Default: %(default)s] ",  type=str, action="store", default = '2019DataProduction')
#    parser.add_argument("-p", "--process",help="process name; [Default: %(default)s] ",  type=str, action="store", default = '2019DataProduction')
    parser.add_argument("-s", "--site-run",help="Site to run; [Default: %(default)s] ",  type=str, action="store", default = 'T2_US_Florida')
    parser.add_argument("-o", "--path-to-store",help="Path to store the output files; [Default: %(default)s] ",  type=str, action="store", default = '/store/user/cherepan')
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
    DataMCTypes = []
    JobTags = []
    ProdInstance = []            
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
                JobTags.append((line.split(":")[1]).split("/")[2].strip())
            if "DataMCType" in line:
                DataMCTypes.append(line.split(":")[1].strip())
                if "data" in line.split(":")[1]:
                    ProdInstance.append("global")
                else:
                    ProdInstance.append("phys03")
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
    setcrabconfig2(DataSets,JobTags,DataMCTypes,ProdInstance,GlobalTags,args.tag,args.site_run, args.path_to_store)   



    print "\n\nDo source SubmitAllByCrab.sh  to submit all jobs \n" 
    print "Run a small scale job before submitting ! \n" 
