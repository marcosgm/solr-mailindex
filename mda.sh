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
#rm $FILEPATH #remove original MIME file

TIKAJAR="/opt/tika/tika-app-1.3.jar"
#clean up empty files (ripmime problem?)
#whitespace problem: for f in $(ls $ARCHIVEDEST/*); do 
find $ARCHIVEDEST -type f -print0 | while read -d $'\0' f
do
    test ! -s "$f"  && rm "$f";  #if the file is empty, remove it
    filename=$(basename "$f")
    if [[ $filename != _headers_ && $filename != textfile* ]]; then
        echo $f "is going to Tika"
        java -jar $TIKAJAR -x "$f" > "${f}_tikaxml" 2>/dev/null
    fi
done


#now send the files to SOLR
SOLRURL="http://liferay-hydroqc-cluster1.mtllab.sfl:8983/solr/mail/upload"
ARCHIVEURL="http://archiveserver/$YEARMONTH/$MESSAGEID"

#SOLRCELL CAN ACCEPT MIMEFILES AND EXTRACT THE DATA. WE JUST HAVE TO MAP SOME VALUES, AND ADD OTHER INFO (like links to the archived attachments) AFTERWARDS, USSING MESSAGEID
#PROBLEM: we have to map the tag <div class="email-entry"> to an attachment
#curl "http://localhost:8983/solr/mail/update/extract?literal.messageId=$MESSAGEID&commit=true&fmap.content=attachment&capture=meta&fmap.meta=ignored_meta&fmap.Message-From=from&fmap.Creation-Date=sentDate&" -F "myfile=@$FILEPATH" -v

#./sendMIMEfolderToSOLR.py --folder $ARCHIVEDEST --solrurl $SOLRURL --archiveUrl $ARCHIVEURL

#exit OK, probably getmail will remove the mail from IMAP
exit 0
