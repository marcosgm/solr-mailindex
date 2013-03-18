#!/usr/bin/python
# If on Python 2.X
from __future__ import print_function
from email.Parser import HeaderParser
from optparse import OptionParser

import pysolr
import os

# Setup a Solr instance. The timeout is optional.
solr = pysolr.Solr('http://localhost:8983/solr/', timeout=10)

tikaJarPath=""

class mimeFolderObject :
    def __init__ (self, path, messageid, archiveurl):
        self.path   = path
        self.id     = messageid
        self.arrayDocs = [] #is a list of dictionaries
        #every docDictionary has an id (Message-ID), an attachmentName (string) and an attachment (text)
        #if we find a "textfile" file, then we send its content to the "content" field
        #similarly, the _headers_ file must be parsed and sent to their corresponding fields
        self.archiveURL=archiveurl

    def _iterate(self):
        for filename in os.listdir(self.path):
            ffile=os.path.join(self.path,filename)
            if (filename.startswith("textfile") and os.path.getsize(filename)>0):
                self.arrayDocs.append(self.getTextDic(ffile, filename))
            elif (filename.startswith("_headers_")):
                self.arrayDocs.append(self.getHeadersDic(ffile))
            elif (filename.endswith("_tikaxml")):
                self.arrayDocs.append(self.getTextDic(ffile, file[:filename.find("_tikaxml")]))
#            elif (os.path.isfile(ffile)):
#                self.arrayDocs.append(self.getTikaDic(ffile))
        return
    def getTikaDic(self,file):
        return "tika!"
    def getTextDic(self,file, filename):
        ret={}
        f=open(file)
        ret["Message-ID"]   = self.id
        ret["attachment"]   = f.read()
        ret["attachmentName"]   = filename
        ret["attachmentURL"]    = self.archiveURL+filename
        return ret
    def getHeadersDic(self,file):
        ret={}
        f=open(file)
        p=HeaderParser().parse(f)
        ret["Message-ID"]   = self.id
        ret["subject"]      = p.__getitem__("Subject")
        ret["retmailfrom"]  = p.__getitem__("From")
        ret["sentDate"]     = p.__getitem__("Date")
        ret["xMailer"]      = p.__getitem__("User-Agent")
        ret["allTo"]        = p.__getitem__("To")
        return ret
        



# How you'd index data.
#solr.add([
#    {
#        "id": "doc_1",
#        "title": "A test document",
#    },
#    {
#        "id": "doc_2",
#        "title": "The Banana: Tasty or Dangerous?",
#    },
#])
#id="20130314165928.2BD997FA7A@liferay-hydroqc-cluster1.mtllab.sfl"
#mm=mimeFolderObject("/opt/SOLRTEST/mailarchive/2013/03/"+id,id)

#mm._iterate()

#./sendMIMEfolderToSOLR.py --id $MESSAGEID --folder $ARCHIVEDEST --solrurl $SOLRURL --archiveUrl $ARCHIVEURL

def main():
    parser = OptionParser("Usage: %prog -m|--messageid X -f|-folder X -s|--solrURL X -a|--archiveURL X")
    parser.add_option("-m", "--messageid", dest="messageid", type="string", help="message-ID of the e-mail")
    parser.add_option("-f", "--folder", dest="folder",type="string",  help="folder with MIME files")
    parser.add_option("-s", "--solrURL", dest="solrurl", type="string", help="Update URL of the SOLR server")
    parser.add_option("-a", "--archiveURL", dest="archiveurl", type="string", help="Archive URL for recovering the files over HTTP, FTP, SMB, etc")
    
    (options, args) = parser.parse_args()
    print (str(len(args)))
    if len(args) != 4:
            parser.error("incorrect number of arguments + "+str(len(args)))

    print (options.messageid, options.folder, options.solrurl, options.archiveurl)
    mm=mimeFolderObject(options.folder, options.messageid,  options.archiveurl)

    print (mm.arrayDocs)

if __name__ == "__main__":
        main()
