#!/usr/bin/env python

import os
import argparse

def setcrabconfig(datasetname,prodtag,Site,OutputPath):
    jobtag = datasetname.split("/")[2]
    outputdatatag = prodtag+"_"+jobtag
    crabname = "crab_"+jobtag+".py"
    crabconf=open(crabname,"w")
    crabconf.write ("from WMCore.Configuration import Configuration  \n")
    crabconf.write ("config = Configuration()  \n\n")
    crabconf.write ("config.section_(\"General\")  \n")
    crabconf.write ("config.General.requestName = '"+jobtag+"'\n")
    crabconf.write ("config.General.workArea =  '%s' \n\n" %  prodtag)
    crabconf.write ("config.section_(\"JobType\") \n")
    crabconf.write ("config.JobType.pluginName = 'Analysis' \n")
    crabconf.write ("config.JobType.psetName = 'runNtuple.py'  \n\n")
    crabconf.write ("config.section_(\"Data\")  \n\n")
    crabconf.write ("config.Data.inputDataset = '%s' \n" % str(datasetname) )
    crabconf.write ("config.Data.inputDBS  = 'global' \n")
    crabconf.write ("config.Data.splitting = 'LumiBased' \n")
    crabconf.write ("config.Data.unitsPerJob = 20 \n")
    crabconf.write ("config.Data.totalUnits = -1 \n")
    crabconf.write ("config.Data.lumiMask = 'Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt' \n")
    crabconf.write ("config.Data.publication = True \n")
    crabconf.write ("config.Data.outLFNDirBase = '%s' \n" % OutputPath)
    crabconf.write ("config.Data.outputDatasetTag = '%s' \n\n" % outputdatatag )
    crabconf.write ("config.section_(\"Site\") \n")
    crabconf.write ("config.Site.storageSite = '%s' \n" % Site)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--input-file",help="input file; [Default: %(default)s] ", action="store", default = 'datasets.dat')
    parser.add_argument("-t", "--tag",help="Tag the production; [Default: %(default)s] ",  type=str, action="store", default = '2019DataProduction')
    parser.add_argument("-p", "--process",help="process name; [Default: %(default)s] ",  type=str, action="store", default = '2019DataProduction')
    parser.add_argument("-s", "--site-run",help="Site to run; [Default: %(default)s] ",  type=str, action="store", default = 'T2_FR_IPHC')
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
    submitall=open("SubmitAllToCrab.sh","w")
    with open(datasetsFile) as fIn:
        for line in fIn:
            line = line.strip()
            
            if not line:
                continue

            if '#' in line:
                continue
            jobtag= line.split("/")[2]
            print "Data set to be configured: ", line
            crabname = "crab_"+jobtag+".py"
            submitall.write("crab submit -c %s\n" % crabname)
            setcrabconfig(line,args.tag,args.site_run, args.path_to_store)   

    print "====================== "
    print "DataSetFile: ", datasetsFile
    print "Do source SubmitAllToCrab.sh  to submit all jobs \n" 
    print "Run a single test job before submitting ! \n" 
