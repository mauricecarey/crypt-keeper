# Crypt-Keeper
Crypt-Keeper is the project name for a secure document exchange service designed for use on AWS this service is also known as Document Service throughout the design documentation. You can find more information on the [Django Crypt-Keeper server](crypt-keeper-django/README.md) in the crypt-keeper-django directory of this repository, that file has information on how to use the Django based server. This document makes reference to Dynamo as the backing store however that is a roadmap feature and the currently supported backing store is Postgres. Hashicorp Vault is also mentioned as the secret store, this is also a roadmap feature and the public-private key pairs are currently stored in Postgres.

## Features
1.  All documents are stored in S3.
2.  Documents are encrypted at rest.
3.  Documents are encrypted on the client prior to transfer, so are never exposed over the wire regardless of encryption used on transfer session.
4.  Encryption keys are single use meaning they are used for only one document (envelope encryption). This provides more robust security should the document store be compromised.
5.  Scalability is restricted only by properties of AWS infrastructure. Specifically S3, ELBs, EC2, and DynamoDB. More specifically it will scale with your credit card.
6.  Availability is primarily a function of AWS infrastructure including S3, EC2, and DynamoDB. Responsible deployment of Document Service across availability zones will also be a factor.

## Document Service Design
The Document Service design is very simple supporting two primary use cases.

1.  Secure Document Upload
2.  Secure Document Download

See the [StarUML](http://staruml.io) uml-designs.mdj file in this repo for sequence diagrams of these use cases.

### Component Descriptions
#### Client
The client will be implemented in several languages for use in different scenarios. For example, you might need a client to interact with existing Python based apps. You also want to expose document services via your website so a JavaScript based client that runs completely in the users web browser will also be needed. To this end there are existing JavaScript libraries available to perform encryption operations, for example [Forge](https://github.com/digitalbazaar/forge).

#### S3
This is fairly straight forward use of the Amazon Simple Storage Service. Pre-signed URLs can be used to grant temporary access to [upload](http://docs.aws.amazon.com/AmazonS3/latest/dev/PresignedUrlUploadObject.html) or [download](http://docs.aws.amazon.com/de_de/AmazonS3/latest/dev/ShareObjectPreSignedURL.html) an object or document.

#### Document Service
Document service handles only security and metadata for documents, allowing file transfer operations to scale based on S3 rather than our specific management service. Internally document service depends on DynamoDB on a per request basis to store document metadata this allows the service to scale almost indefinitely based on the scalability of Dynamo which is a function of cost. There is also a dependency on Vault for storing the PKI credentials used to secure symmetric keys in the DynamoDB. However, this data is cacheable at the service layer reducing load on Vault. Much of the load on Vault would then be measured as a function of document service instance creation, and PKI credential expiration policies rather than the load on document service. Another factor is the decision to either use a single rotating PKI set for all Dynamo encryption or if each customer should have a separate PKI credential for securing symmetric keys. Likely a single set is sufficient since the keys will never be exposed beyond the internal AWS infrastructure. Document service also needs to handle file access ACLs.

#### DynamoDB
Dynamo will be used to store document metadata and encryption keys for secure documents. Expiration of data is a concern and should be configured to match with file lifetime. A cost effective means of removing expired records is to simply delete all records in a table via removal of the table. Therefor document ids will be mapped to unique tables based on creation time of the document id allowing an efficient rolling removal of table spaces from Dynamo. Note that this logical time based partitioning is different than the physical partitioning implemented in Dynamo.

#### Vault
Vault is used to store PKI credentials used by the document service to decrypt the symmetric keys stored in Dynamo.

### Outstanding Questions
1.  Can Vault handle the required traffic load? Assuming caching and one set of PKI credentials per service then this should not me a consideration.
2.  How do we rotate the public/private key pair used for encrypting the symmetric keys? One possibility would be to rotate on the logical Dynamo partition level. So, the service would require a set of keys for each active logical data partition. Another - probably better - way would be to store the serial number identifying the required key with the unencrypted document data in Dynamo.
3.  How do we handle notifications of document upload? S3 supports [event notification](http://docs.aws.amazon.com/de_de/AmazonS3/latest/dev/NotificationHowTo.html) on object creation.
4.  How do we deal with object expiration notifications if needed? S3 supports [server access logs](http://docs.aws.amazon.com/de_de/AmazonS3/latest/dev/ServerLogs.html) where [object expirations](https://aws.amazon.com/blogs/aws/amazon-s3-object-expiration/) can be logged.