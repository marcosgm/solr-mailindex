===Option A: MIMEmail upload to SOLR CELL===

MDA => mimeFile.txt => curl -F mimeFile.txt to SOLRCELL 

Advantages:
SOLR does all the job

Problem:
- No attachment separation in the index: if a mail has more than 2 attachments, we see all their content appended in the same "attachment" field. This makes the search engine less useful
- It requires a second curl to upload metadata informations (like URLs to every original PDF)


SCHEMA:		No Multivalued attachment. Must support for default mailHeaders
SOLRCONFIG:	SolrCELL activated
UPLOADURL:	Complex, must map <meta> tags to fields on every request

===Option B: MIMEmail to TIKA, then upload XHTML chunks to regular SOLR===

MDA => mimeFile => java -jar TIKA mimeXML => split by <div class="email-entry"> > (foreach email-entry) curl "<field name="attachments" update="add">"$(XML of email-entry)"</field>" to SOLR (regular) 

Advantages:
- One <attachment> field per attachment. We can properly populate the index.

Problem 
1) I need to use XML upload to add the content to the MultiValue field "attachments". But the information to upload is already XML. Should URLEncode or Base64 the content?
2) I REALLY neeed to manually split the attachments using <div class="email-entry">. It seems impossible to do it automatically with SOLRCELL and the "capture" option &capture=div (no class suport here). Maybe using SolrJ instead of CURL??
3) It requires one curl command per "email-entry"

SCHEMA:		Multivalued attachments + customized mailHeaders, no need for default ones
SOLRCONFIG:	No SolrCELL
UPLOADURL:	2 different ones: one for uploading metadata headers, other for the attachments


===Option C: attachment_file upload to SOLR CELL===
MDA => mimeFile => ripmime => (foreach file) curl "extract&literal.messageID=$MESSAGEID" -F "attachment=@file1.pdf" to SOLRCELL

according to DOC: literal.<fieldname>=<value> - Create a field with the specified value. May be multivalued if the Field is multivalued.

Advantages
- default SOLRCELL parsing: will save some useful metadata (filename, original document date), even if it will take some extra work

Problem
1) No idea if attachment=(content of the file) will call SOLRCELL and put its content in the multivalue "attachment" field. Sounds tricky. Try -F "literal.attachment" (POST attribute instead of GET attribute)
2) Need to parse the _headers_ file and populate the index with the mail metadata
3) Need to deal with default extracted fields (set them as ignored with "&capture=meta&fmap.meta=ignored_meta")

SCHEMA:		Multivalued attachments + customized mailHeaders, no need for default ones + ignore default SOLR CELL (like Author, etc)
SOLRCONFIG:	SolrCELL activated
UPLOADURL:	2 different ones: one for uploading metadata headers, other for the attachments (using solrcell)


===Option D attachment_file to TIKA then upload XHTML to regular SOLR===
MDA => mimeFile => ripmime => (foreach non-text file) java -jar TIKA file1.pdf => curl "update&literal.messageID=$MESSAGEID" -F "attachment=@file1_tika.xml" to SOLR (regular)

Advantages
- full control and granularity

Problem
1) (same as option C) No idea if attachment=(content of the file) will put its content in the multivalue "attachment" field. Sounds tricky
2) (same as option B) How to embed XHTML in an XML text field?
3) Need to parse the _headers_ file and populate the index entry with the mail metadata

SCHEMA:		Multivalued attachments + customized mailHeaders, no need for default ones
SOLRCONFIG:	No SolrCELL
UPLOADURL:	2 different ones: one for uploading metadata headers, other for the attachments (using solrcell)




|||||||||SOLUTION||||||||||||||

For updating a multivalue field, use JSON uploading http://wiki.apache.org/solr/UpdateJSON#Atomic_Updates

curl "http://localhost:8983/solr/mail/update?literal.messageId=1234&commit=true&literal.attachmentNames=Example3" --data-binary '{"add":{"doc":{"messageId":"12345","attachment":{"add":"<email>Example3</email>"}}}}' -H 'Content-type: application/json' -v

