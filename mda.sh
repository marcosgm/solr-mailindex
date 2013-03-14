#!/bin/bash
#get through STDIN a new mail
#store mail in its full form under the MAILDIR folder
#then call the archiveMail.sh method to separate the attachments and store them using a UUID folder in an archived file structure
UUID=$(uuidgen)
cat - > maildir/new/$UUID
archived=$(./archiveMail.sh maildir/new/$UUID)



#clean up empty files (MIME problem?"
YEARMONTH=$(date +"%Y/%m")
ARCHIVE="mailarchive"
ARCHIVEDEST=$ARCHIVE/$YEARMONTH/$UUID

for f in $(ls $ARCHIVEDEST/*); do test ! -s $f  && echo "$f is empty" && rm $f; done

exit 0
