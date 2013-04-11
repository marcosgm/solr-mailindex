#!/bin/bash
#get through STDIN a new mail
#store mail in its full form under the MAILDIR folder
#then call the archiveMail.sh method to separate the attachments and store them using a UUID folder in an archived file structure

#we will store the .eml file in $MAILDIR/2013/02/idofthemail-12354@yahoo.com/idofthemail-12354@yahoo.com.eml
#attachments will be placed in  $MAILDIR/2013/02/idofthemail-12354@yahoo.com/attachment1.pdf

####Phase 1: store the .eml file in today's folder
MAILDIR="/opt/tmpmaildir"
UUID=$(uuidgen)
TMPMAIL=$MAILDIR/tmp/$UUID  #random temp folder
cat - > $TMPMAIL
#need to to this in 2 steps to avoid: "Delivery error (command mda.sh 10064 wrote to stderr: head: write error: Broken pipe"
MSGID=$(head -n 500 $TMPMAIL |formail -xMessage-Id) #extract Message-ID, regardless of upper or lowercase
MESSAGEID=$(echo $MSGID |sed 's/[< >]//g') #remove <,>, and space
if [ -z $MESSAGEID ]; then
    MESSAGEID=$UUID   
fi

YEARMONTH=$(date +"%Y/%m")
ARCHIVE="/var/ftp/mailindex"
ARCHIVEDEST=$ARCHIVE/$YEARMONTH/$MESSAGEID
mkdir -p $ARCHIVE/$YEARMONTH
mv $TMPMAIL /$ARCHIVEDEST.eml
#now we have in a single file the full mail, MIME encoded

####Phase2: will send the .eml file to SOLR using $MESSAGEID as unique ID
#SOLRCELL CAN ACCEPT MIMEFILES AND EXTRACT THE DATA. WE JUST HAVE TO MAP SOME VALUES, AND ADD OTHER INFO (like links to the archived attachments) AFTERWARDS, USSING MESSAGEID
curl -S -s "http://localhost:8983/solr/mailindex/update/extract?literal.messageId=$MESSAGEID&commit=true&fmap.content=attachment&fmap.Message-From=from&fmap.Creation-Date=sentDate" -F "myfile=@$ARCHIVEDEST.eml" 
#capture=meta&fmap.meta=ignored_meta

####Phase 3: ripmime will create a folder with the same name as the .eml file, filled with the attachments 

#ripmime receives MIME msg by stdin, overwrite if we process twice the same message (waranteed to be unique thanks to messageID folder
#lets call ripmime to chop the MIMEfile into multiple files with attachments
cat $ARCHIVEDEST.eml | ripmime -i - --overwrite -e -d  $ARCHIVEDEST #will put files in -d $ARCHIVEDEST subfolder
chmod 775 $ARCHIVEDEST
chmod 644 $ARCHIVEDEST/*

####Phase 4: we will clean some unnecesary files created by ripmime, then upload URLs to SOLR to directly download those attachments 
BASEURL="ftp://solr-test.mtl.sfl/mailindex"
find $ARCHIVEDEST -type f -print0 | while read -d $'\0' f   #whitespace problem: for f in $(ls $ARCHIVEDEST/*); do 
do
#    test ! -s "$f"  && rm "$f";  #if the file is empty, remove it
    #f is the full filename path
    filename=$(basename "$f")
    if [[ $filename == _headers_ || $filename == textfile*  ]]; then
	rm $f
    else
	#URLEncode the file
	#newfilename=$(echo -n $filename | perl -pe's/([^-_.~A-Za-z0-9])/sprintf("%%%02X", ord($1))/seg');
	newfilename=$(echo -n $filename | perl -pe's/([^-_.~A-Za-z0-9])/_/seg');
	#echo "filename was $filename and the new is $newfilename"
	if [[ $filename != $newfilename ]]; then mv "$ARCHIVEDEST/$filename" $ARCHIVEDEST/$newfilename; fi
	attachmentURL="$BASEURL/$YEARMONTH/$MESSAGEID/$newfilename"
	    #save $f URL to SORL as name
	#STUPID, DOESN't WORK    curl -S -s "http://localhost:8983/solr/mailindex/update?&commit=true&literal.messageid=$MESSAGEID&literal.attachmentURL=$attachmentURL" 
    curl -S -s "http://localhost:8983/solr/mailindex/update?&commit=true"  -H "Content-Type: text/xml" --data-binary "<add><doc><field name='messageId'>$MESSAGEID</field><field name='attachmentURL' update='add'>$attachmentURL</field></doc></add>"
    fi
  
done


###Phase 5: Upload a URL to the MIME original file
mv $ARCHIVEDEST.eml $ARCHIVEDEST #save the eml file in its subfolder

emlURL="$BASEURL/$YEARMONTH/$MESSAGEID/$MESSAGEID.eml"
#save ARCHIVEDEST.eml to SORL as "emlURL", of the eventual recovery of the original mail
curl -S -s "http://localhost:8983/solr/mailindex/update?&commit=true"  -H "Content-Type: text/xml" --data-binary "<add><doc><field name='messageId'>$MESSAGEID</field><field name='emlURL' update='add'>$emlURL</field></doc></add>"



exit 0
