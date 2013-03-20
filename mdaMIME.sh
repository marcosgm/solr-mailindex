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
ARCHIVEDEST=$ARCHIVE/$YEARMONTH/$MESSAGEID
mkdir -p $ARCHIVE/$YEARMONTH
mv $FILEPATH $ARCHIVEDEST.eml

#SOLRCELL CAN ACCEPT MIMEFILES AND EXTRACT THE DATA. WE JUST HAVE TO MAP SOME VALUES, AND ADD OTHER INFO (like links to the archived attachments) AFTERWARDS, USSING MESSAGEID
curl "http://localhost:8983/solr/mail/update/extract?literal.messageId=$MESSAGEID&commit=true&fmap.content=attachment&capture=meta&fmap.meta=ignored_meta&fmap.Message-From=from&fmap.Creation-Date=sentDate&literal.emailURL=http%3A%2F%2Fmyserver%2Farchive%2F$ARCHIVEDEST.eml" -F "myfile=@$ARCHIVEDEST.eml" 


#exit OK, probably getmail will remove the mail from IMAP
exit 0
