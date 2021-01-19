Setup your list of samples that you want to run as, for example:  inputFiles/Prod_26_03_2019.dat; 

```
usage: configureJobs.py [-h] [-f INPUT_FILE] [-t TAG] [-s SITE_RUN]
                        [-o PATH_TO_STORE] [-j JSON] [-d DATA_TIER]

optional arguments:
  -h, --help            show this help message and exit
  -f INPUT_FILE, --input-file INPUT_FILE
                        input file; [Default: datasets.dat]
  -t TAG, --tag TAG     Tag the production; [Default: 2019DataProduction]
  -s SITE_RUN, --site-run SITE_RUN
                        Site to run; [Default: T2_US_Florida]
  -o PATH_TO_STORE, --path-to-store PATH_TO_STORE
                        Path to store the output files; [Default:
                        /store/user/cherepan]
  -j JSON, --json JSON  LumiMask JSON file; [Default: Cert_294927-306462_13TeV
                        _PromptReco_Collisions17_JSON.txt]
  -d DATA_TIER, --data-tier DATA_TIER
                        Data tier of the input fies AOD/MINIAOD; Default is
                        AOD, if otherwise use option MINIAOD; [Default: AOD]


```
Important: 
1) Take care about the TAG option and PATH_TO_STORE


