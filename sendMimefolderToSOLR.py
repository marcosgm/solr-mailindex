#!/usr/bin/python
# If on Python 2.X
from __future__ import print_function
from email.Parser import HeaderParser
from optparse import OptionParser
import json

import pysolr
import os

# Setup a Solr instance. The timeout is optional.
solr = pysolr.Solr('http://192.168.103.160:8983/solr/mail/', timeout=10)

tikaJarPath=""

''' 
It represents a folder with the MIME content of an email, split by attachment. It holds an array of dictionaries. Every dictionary represents the parsed text and metadata of every file, plus other attributes like the attachmentURL, which is the public URL to download the file. There is also one dictionary with the metadata elements of the mail headers.
'''
class mimeFolderObject :
    def __init__ (self, path, messageid, archiveurl):
        self.path   = path
        self.id     = messageid
        self.arrayDocs = [] #is a list of dictionaries
        #every docDictionary has an id (Message-ID), an attachmentName (string) and an attachment (text)
        #if we find a "textfile" file, then we send its content to the "content" field
        #similarly, the _headers_ file must be parsed and sent to their corresponding fields
        self.archiveURL=archiveurl
        self._iterate()

    def _iterate(self):
        for filename in os.listdir(self.path):
            ffile=os.path.join(self.path,filename)
            if (filename.startswith("textfile") and os.path.getsize(ffile)>0):
                self.arrayDocs.append(self.getTextDic(ffile, filename))
            elif (filename.startswith("_headers_")):
                self.arrayDocs.append(self.getHeadersDic(ffile))
            elif (filename.endswith("_tikaxml")):
                self.arrayDocs.append(self.getTextDic(ffile, filename[:filename.find("_tikaxml")]))
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
        
    def _setAddJsonValue (self, dictelem, key):
        olddictvalue = dictelem[key]
        dictelem[key]={}
        dictelem[key]["add"]=olddictvalue
        
    def serializeArraySolrJSON (self):
        ''' Return an array of dictionaries where their values are {"add":value}, that will permit Solr addition to multipleValue items '''
        updateJsonObj=[]
        for d in self.arrayDocs:
            copiedval=d.copy()
            #if it is an attachment, change their "attachment" value for another dictionary with the key "add"  so SOLR will use the MultiValue field features
            if "attachment" in copiedval: 
                self._setAddJsonValue(copiedval,"attachment")
            if "attachmentURL" in copiedval: 
                self._setAddJsonValue(copiedval,"attachmentURL")
            if "attachmentName" in copiedval: 
                self._setAddJsonValue(copiedval,"attachmentName")
            updateJsonObj.append(copiedval)
        return updateJsonObj
            


# How you'd index data using multiple values.
#solr.add([
#    {
#        "attachmentName": 
#            {
#               "add":  "doc1"
#            },
#        "attachment": 
#            {
#               "add":  "This is the first doc"
#            },
#    },{
#        "attachmentName": 
#            {
#               "add":  "doc2"
#            },
#        "attachment": 
#            {
#               "add":  "Now the second doc"
#            },
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
    if not options.messageid or not options.folder or not options.solrurl or not options.archiveurl:
        parser.error("Invalid number of arguments")

    print (options.messageid, options.folder, options.solrurl, options.archiveurl)
    mm=mimeFolderObject(options.folder, options.messageid,  options.archiveurl)

    solrupdate=mm.serializeArraySolrJSON()
    addDict={}
    addDict["add"]=[]
    for d in solrupdate:
        x={}
        x["doc"]=d
        addDict["add"].append(x)
    
    print (json.dumps(addDict))

#    print (json.dumps(solrupdate))
#    solr.add(solrupdate)
#curl "http://localhost:8983/solr/mail/update?literal.messageId=1234&commit=true&literal.attachmentNames=Example3" --data-binary '{"add":{"doc":{"messageId":"12345","attachment":{"add":"<email>Example3</email>"}}}}' -H 'Content-type: application/json' -v

        

if __name__ == "__main__":
        main()
