MAIL ARCHIVING AND INDEXING USING SOLR

[![Git](https://app.soluble.cloud/api/v1/public/badges/2feb32b5-6963-46a0-b73f-8479857aad45.svg?orgId=568518005652)](https://app.soluble.cloud/repos/details/github.com/marcosgm/solr-mailindex?orgId=568518005652)  
====

This is a proof-of-concept of a tool used to download mails from an IMAP folder, parse them, store with the attachments, arhived in a filesystem and index the result using SOLR

Mails can always be retrieved thanks to the archive filesystem structure. SOLR will index all fields and use a UUID field to match together the MAIL text and metadata with its attachments

REQUIREMENTS 
====
yum install getmail python-requests ripmime procmail

pysolr.py from https://github.com/toastdriven/pysolr
