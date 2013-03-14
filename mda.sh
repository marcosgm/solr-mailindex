#!/bin/bash
#get through STDIN a new mail
#store mail in its full form under the MAILDIR folder
#then call the archiveMail.sh method to separate the attachments and store them using a UUID folder in an archived file structure
UUID=$(uuidgen)
MAILDIR="/opt/SOLRTEST/maildir"
TMPMAIL=$MAILDIR/tmp/$UUID  #random temp folder
cat - > $TMPMAIL
#need to to this in 2 steps to avoid: "Delivery error (command mda.sh 10064 wrote to stderr: head: write error: Broken pipe"
MSGID=$(head -n 500 $TMPMAIL |formail -xMessage-Id) #extract Message-ID, regardless of upper or lowercase
MESSAGEID=$(echo $MSGID |sed 's/[< >]//g') #remove <,>, and space

if [ -z $MESSAGEID ]; then
    MESSAGEID=$UUID   
fi
FILEPATH=$MAILDIR/new/$MESSAGEID
mv $TMPMAIL $FILEPATH
#now we have in a single file $FILEPATH the full mail, MIME encoded

YEARMONTH=$(date +"%Y/%m")
ARCHIVE="/opt/SOLRTEST/mailarchive"
MIMETOOL="ripmime -i - --overwrite -e -d " #receives MIME msg by stdin, overwrite if we process twice the same message (waranteed to be unique thanks to messageID folder
ARCHIVEDEST=$ARCHIVE/$YEARMONTH/$MESSAGEID
mkdir -p $ARCHIVEDEST

#lets call ripmime to chop the MIMEfile into multiple files with attachments
cat $FILEPATH | $MIMETOOL $ARCHIVEDEST #will put files in -d $ARCHIVEDEST
rm $FILEPATH #remove original MIME file

#clean up empty files (ripmime problem?)
for f in $(ls $ARCHIVEDEST/*); do 
    test ! -s $f  && rm $f;  #if the file is empty, remove it
done

#now send the files to SOLR
SOLRURL="http://liferay-hydroqc-cluster1.mtllab.sfl:8983/solr/mail/upload"
ARCHIVEURL="http://archiveserver/$YEARMONTH/$MESSAGEID"

#./endMIMEfolderToSOLR.py --folder $ARCHIVEDEST --solrurl $SOLRURL --archiveUrl $ARCHIVEURL

#exit OK, probably getmail will remove the mail from IMAP
exit 0
