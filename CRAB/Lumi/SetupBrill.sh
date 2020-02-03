  export PATH=$HOME/.local/bin:/afs/cern.ch/cms/lumi/brilconda-1.1.7/bin:$PATH
  export PATH=$HOME/.local/bin:/nfshome0/lumipro/brilconda/bin:$PATH
  pip uninstall brilws
  pip install --install-option="--prefix=$HOME/.local" brilws
  pip show brilws
  brilcalc --version
#  brilcalc lumi -b "STABLE BEAMS" -u /fb -i processedLumis.json --normtag /afs/cern.ch/user/l/lumipro/public/normtag_file/normtag_DATACERT.json


