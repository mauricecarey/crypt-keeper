# Crypt-Keeper
Crypt-Keeper is a simple and scalable web service for keeping file encryption credentials out-of-band to the file being protected and exchanged. This is different than many contemporary file exchange services in that the storage mechanism does not have to be trusted to keep your data secret. Crypt-Keeper leverages AWS S3 for storage in order to take advantage of nearly infinite storage capacity, ease of management, availability, and of course huge scalability. For full details please see [my blog introducing Crypt-Keeper](http://www.mauricecarey.com/2017/04/01/secure-file-exchange-for-mortals/). 

## Service
You can find more information on the [Django Crypt-Keeper server](crypt-keeper-django/README.md) in the crypt-keeper-django directory of this repository, that file has information on how to use the Django based server.

## Design
For more information on the design of Crypt-Keeper see [the design documents](DESIGN.md).

