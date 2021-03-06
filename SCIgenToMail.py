#!/usr/bin/python

import urllib2, re, sys, smtplib, os
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

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
    
def sendPDFtoMail(pdfpath,emailaddress,erase=True):
    me=emailaddress #from me to myself
    pdfname=os.path.basename(pdfpath)
    msg = MIMEMultipart()
    msg['Subject'] = 'Paper %s' % pdfname
    msg['From'] = me
    msg['To'] = emailaddress

    body = MIMEText ("See attached my <b> LATEST <a href='http://apps.pdos.lcs.mit.edu/'>SCIGEN</a> <u> PAPER </u> </b>", "html")
    msg.attach(body)
    fp = open(pdfpath, 'rb')
    pdf = MIMEApplication(fp.read(),"pdf; name ='%s'" %pdfname) 
    fp.close()
    msg.attach(pdf)

    s = smtplib.SMTP('localhost')
    s.sendmail(me, emailaddress, msg.as_string())
    s.quit()

    if erase == True:
        os.remove(pdfpath)

if __name__ == "__main__":
    paper = getSciGenHTML()
    seed=parseHTMLforPDFseed(paper)
    pdfpath="/tmp/scigen-%s.pdf" %seed
    savePDFtoFile(seed,pdfpath)
    sendPDFtoMail(pdfpath,emailaddress="solr.test@savoirfairelinux.com")

