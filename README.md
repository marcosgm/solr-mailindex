MAIL ARCHIVING AND INDEXING USING SOLR
====

This is a proof-of-concept of a tool used to download mails from an IMAP folder, parse them, store with the attachments, arhived in a filesystem and index the result using SOLR

Mails can always be retrieved thanks to the archive filesystem structure. SOLR will index all fields and use a UUID field to match together the MAIL text and metadata with its attachments

REQUIREMENTS 
====
yum install getmail python-requests ripmime procmail

pysolr.py from https://github.com/toastdriven/pysolr
