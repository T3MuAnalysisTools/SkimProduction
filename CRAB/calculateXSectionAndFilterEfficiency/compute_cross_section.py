#!/usr/bin/env python

# EXAMPLE ON HOW TO RUN
# ./compute_cross_section.py -f datasets.txt 

from optparse import OptionParser
import os
import sys
import commands
import re
import datetime
from time import sleep

def str_to_bool(s):
    if s == 'True':
         return True
    elif s == 'False':
         return False

if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option('-f', '--datasets'      , dest="inputdataset",     default='datasets.txt',   help='primary dataset names')
    parser.add_option('-n', '--nfiles'        , dest="nfiles",           default=int(5),           help='N files to analyse')
    parser.add_option('-c', '--campaign'      , dest="campaign",         default='',               help='MC campaign to be searched for (e.g. Moriond17, ...)')
    parser.add_option('-e', '--events'        , dest="events",           default=int(1e6),         help='number of events to calculate the cross section')
    parser.add_option('-d', '--datatier'      , dest="datatier",         default='MINIAODSIM',     help='datatier (e.g. GEN-SIM, MINIAOD, ...)')
    parser.add_option(      '--mcm'           , dest="mcm",              default=False,            help='use McM prepID instead of dataset name')
    parser.add_option('-s', '--skipexisting'  , dest="skipexisting",     default=False,            help='skipexisting existing output files containing xsec results')
    parser.add_option(      '--debug'         , dest="debug",            default=False,            help='use debug options (debug couts...)')

    (args, opts) = parser.parse_args(sys.argv)
    debug = str_to_bool(str(args.debug))

    if debug: print 'debug is True!'
    
    if debug:
        print
        print 'RUNNING PARAMS: '
        print '                debug                 = ' + str(debug)
        print '                dataset               = ' + args.inputdataset
        print '                Datatier              = ' + args.datatier
        print '                number of events      = ' + str(args.events)
        print

    das_cmd = "/cvmfs/cms.cern.ch/common/dasgoclient"
    
    with open(args.inputdataset) as f:
        for line in f:
            primary_dataset_name = line.strip()#args.inputdataset

            instance=" instance=prod/phys03"
            command=das_cmd+" --query=\"dataset dataset="+primary_dataset_name+instance+"\""


            dataset_used = commands.getstatusoutput(command)[1].split("\n")
            if debug: print '=====command',command,'\n'
            dataset_used = [x.strip() for x in dataset_used][0]
    
            if debug: print 'dataset_used',dataset_used
            if debug: print 'primary_dataset_name',primary_dataset_name,'\n'
            # pick up only the first dataset of the list
            if debug: print 'dataset_used',dataset_used
            # retrieve filelist
            command=das_cmd+"  --query=\"file dataset="+dataset_used+instance+"\" "
            print " filelists   ", command
            if debug: print 'command',command
            filelist_used = "/store"+commands.getstatusoutput(command)[1].replace("\n",",").split("/store",1)[1]
            filelist_selected = filelist_used.split(',')[0:int(args.nfiles)]
            filelist_final = ""
            for x in filelist_selected:
                x+=","
                filelist_final+=x

            if debug: 
                print 'filelist_used',filelist_used.split(',')[0]
                filelist_used = filelist_used.split(',')[0]
            # compute cross section
            command = 'cmsRun genXsec_cfg.py inputFiles=\"'+filelist_final[:-1]+'\" maxEvents='+str(args.events)+" 2>&1 | tee xsec_"+primary_dataset_name.split('/')[1]+".log"
            print command
            os.system(command)
