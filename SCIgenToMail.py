#!/usr/bin/python

import urllib2, re, sys

def getSciGenHTML():
    anotherone="http://apps.pdos.lcs.mit.edu/cgi-bin/scigen.cgi?"
    response = urllib2.urlopen(urllib2.Request(anotherone))
#will do 301 to http://apps.pdos.lcs.mit.edu/scicache/209/scimakelatex.75574.none.html
    return response.read()

def parseHTMLforPDFseed(paper):
#HTML result: 
#Download a <a href="/cgi-bin/scigen.cgi?seed=830&type=ps&">
#    Postscript</a>
#    or <a href="/cgi-bin/scigen.cgi?seed=830&type=pdf&">PDF</a> 
#    version of this paper.<br>
    seedpattern="seed=(\d+)"
    result=re.search(seedpattern,paper)
    if result:
        seed=result.group(1)
        return seed
    else:
        sys.exit(1)
 
def savePDFtoFile(seed,filepath):
    pdfurl="http://apps.pdos.lcs.mit.edu/cgi-bin/scigen.cgi?seed=%s&type=pdf&" %seed
    print("... Sending HTTP GET to %s" % pdfurl)
    u = urllib2.urlopen(urllib2.Request(pdfurl))
    data = u.read()
    u.close()
    
    FILE = open(filepath, "w")
    FILE.write(data)
    FILE.close()
    print("... Saved PDF to %s" % filepath)
    
if __name__ == "__main__":
    paper = getSciGenHTML()
    seed=parseHTMLforPDFseed(paper)
    savePDFtoFile(seed,"/tmp/scigen-%s.pdf" %seed)
