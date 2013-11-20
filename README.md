ziply
=====

An Open Source signing service implementation integrated with Salesforce.com and Heroku.

All libraries used within ziply are open source and all implementation code within is licensed as MIT. Please feel free to use this for any purpose you see fit.

ziply is build with python and HTML5 and it runs on any modern browser allowing you to sign and generate PDF documents from templates in markdown. The service uses SalesForce.com the OAUTH and Identity Services and thus full REST API access is available.

To deploy ziply:

- Create local development environment following this tutorial
-- https://devcenter.heroku.com/articles/getting-started-with-python
- Add environment variables in ENVIRONMENT.txt to your account.
- Deploy

IMPORTANT!!! To initalize the database you must do the following:

- $heroku run python
- $> from app import db
- $> db.create_all()  #this will create all tables

After the database is initialized everything should work as expected.

This codebase was created in a 3 week sprint for the #SalesForce $1M Hackathon.

Special thanks to:
 - Gage Morgan
 - Linda Patrick
 - Ted Patrick

Building ziply was great fun!

Enjoy!

Ted Patrick
Lead Developer


