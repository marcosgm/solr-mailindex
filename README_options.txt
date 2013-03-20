== IMAP DataImportHandler ==

It does work, but just with emails with no attachments. When processAtachment=true, an error occurs quietly, that makes the handling of a MIME multipart message go unnoticed by the dataimporthandler. We can see on the logs that X mails ar found, but the GUI show the count of mails with no attachments.
We even found the java code that crashes, it is due to a call to a getContent() method on a Part object, that returns null, which according to the JavaMail doc it should never happen.

We tried running solr 4.1, 4.2, on Java 6, Java 7, on Jetty and Tomcat, but we have always the same result. A couple of other Solr users have reported the same problem in the mailing list, but no proper issue has ben reported yet. 


== MBOX DataImportHandler ==

Not tried yet


== Manual upload ==

4 options here, depending on whether we split or not the MIME file and whether we use UploadRequestHandler (SOLR CELL) or the regular upload using an external Tika first.

===Option A: MIMEmail upload to SOLR CELL===

MDA => mimeFile.txt => curl -F mimeFile.txt to SOLRCELL 

Advantages:
SOLR does all the job
We can store the .eml file and let the user download the full email.

Problem:
1) No attachment separation in the index: if a mail has more than 2 attachments, we see all their content appended in the same "attachment" field. This makes the search engine less useful
2) It requires a second curl to upload metadata informations (like URLs to every original PDF)


SCHEMA:		No Multivalued attachment. Must support for default mailHeaders
SOLRCONFIG:	SolrCELL activated
UPLOADURL:	Complex, must map <meta> tags to fields on every request

===Option B: MIMEmail to TIKA, then upload XHTML chunks to regular SOLR===

MDA => mimeFile => java -jar TIKA mimeXML => split by <div class="email-entry"> > (foreach email-entry) curl "<field name="attachments" update="add">"$(XML of email-entry)"</field>" to SOLR (regular) 

Advantages:
- One <attachment> field per attachment. We can properly populate the index.

Problem 
1) (same as option A) Mixed attachment content: It is impossible to split the attachments using <div class="email-entry"> and using the "map" option when uploading. 
2) I need to use "JSON upload" to be able to upload a XHTML text
3) It requires one curl command per "email-entry"
4) We still have to store the attachment files separatedly.

SCHEMA:		Multivalued attachments + customized mailHeaders, no need for default ones
SOLRCONFIG:	No SolrCELL
UPLOADURL:	2 different ones: one for uploading metadata headers, other for the attachments


===Option C: attachment_file upload to SOLR CELL===
MDA => mimeFile => ripmime => (foreach file) curl "extract&literal.messageID=$MESSAGEID" -F "attachment=@file1.pdf" to SOLRCELL

according to DOC: literal.<fieldname>=<value> - Create a field with the specified value. May be multivalued if the Field is multivalued.

Advantages
- default SOLRCELL parsing: will save some useful metadata (filename, original document date), even if it will take some extra work

Problem
#1) No idea if attachment=(content of the file) will call SOLRCELL and put its content in the multivalue "attachment" field. Sounds tricky. Try -F "literal.attachment" (POST attribute instead of GET attribute)
1) Only one attachment saved, (no multivalue support)
2) Need to parse the _headers_ file and populate the index with the mail metadata
3) Need to deal with default extracted fields (set them as ignored with "&capture=meta&fmap.meta=ignored_meta")

SCHEMA:		Multivalued attachments + customized mailHeaders, no need for default ones + ignore default SOLR CELL (like Author, etc)
SOLRCONFIG:	SolrCELL activated
UPLOADURL:	2 different ones: one for uploading metadata headers, other for the attachments (using solrcell)


===Option D attachment_file to TIKA then upload XHTML to regular SOLR===
MDA => mimeFile => ripmime => (foreach non-text file) java -jar TIKA file1.pdf => curl "update&literal.messageID=$MESSAGEID" -F "attachment=@file1_tika.xml" to SOLR (regular)

Advantages
- full control and granularity. All attachments saved separatedly

Problem
1) (same as option B) Need to use "JSON upload", it is more complex. Eventually will cause bad syntax in JSON.
2) Need to parse the _headers_ file and populate the index entry with the mail metadata
3) we get a list of attachments, a list of attachmentNames, but no relationship between the content and it's name.

SCHEMA:		Multivalued attachments + customized mailHeaders, no need for default ones
SOLRCONFIG:	No SolrCELL
UPLOADURL:	2 different ones: one for uploading metadata headers, other for the attachments (using solrcell)




|||||||||SOLUTION||||||||||||||

For updating a multivalue field, use JSON uploading http://wiki.apache.org/solr/UpdateJSON#Atomic_Updates

curl "http://localhost:8983/solr/mail/update?literal.messageId=1234&commit=true&literal.attachmentNames=Example3" --data-binary '{"add":{"doc":{"messageId":"12345","attachment":{"add":"<email>Example3</email>"}}}}' -H 'Content-type: application/json' -v

