#!/bin/bash

#receive as $1 a "getmail'ed" file, in maildir format, encoded using MIME
FILEPATH=$1
YEARMONTH=$(date +"%Y/%m")
FILENAME=$(basename $FILEPATH)
ARCHIVE="mailarchive"
MIMETOOL="ripmime -i - -d "
ARCHIVEDEST=$ARCHIVE/$YEARMONTH/$FILENAME

mkdir -p $ARCHIVEDEST
cat $FILEPATH | $MIMETOOL $ARCHIVEDEST
rm $FILEPATH
