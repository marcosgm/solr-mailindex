# If on Python 2.X
from __future__ import print_function
from email.Parser import HeaderParser

import pysolr
import os

# Setup a Solr instance. The timeout is optional.
solr = pysolr.Solr('http://localhost:8983/solr/', timeout=10)

tikaJarPath=""

class mimeFolderObject :
    def __init__ (self, path, id):
        self.path   = path
        self.id     = id
        self.arrayDocs = [] #is a list of dictionaries
        #every docDictionary has an id (Message-ID), an attachmentName (string) and an attachment (text)
        #if we find a "textfile" file, then we send its content to the "content" field
        #similarly, the _headers_ file must be parsed and sent to their corresponding fields

    def _iterate(self):
        for file in os.listdir(self.path):
            ffile=os.path.join(self.path,file)
            if (file.startswith("textfile")):
                self.arrayDocs.append(self.getTextDic(ffile))
            elif (file.startswith("_headers_")):
                self.arrayDocs.append(self.getHeadersDic(ffile))
            elif (file.endswith("_tikaxml")):
                self.arrayDocs.append(self.getTextDic(ffile))
#            elif (os.path.isfile(ffile)):
#                self.arrayDocs.append(self.getTikaDic(ffile))
        return
    def getTikaDic(self,file):
        return "tika!"
    def getTextDic(self,file):
        ret={}
        f=open(file)
        ret["Message-ID"]   = self.id
        ret["attachment"]   = f.read()
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
id="20130314165928.2BD997FA7A@liferay-hydroqc-cluster1.mtllab.sfl"
mm=mimeFolderObject("/opt/SOLRTEST/mailarchive/2013/03/"+id,id)

mm._iterate()
print (mm.arrayDocs)
