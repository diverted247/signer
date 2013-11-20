import os
from flask import Flask , jsonify, session , redirect , url_for, send_from_directory , escape , request , make_response, render_template
from pyPdf import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from StringIO import StringIO
from PIL import Image
from werkzeug import secure_filename
from base64 import decodestring
import re
import uuid
import hashlib
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.ses.connection import SESConnection
import time
import cStringIO
from flask.ext.sqlalchemy import SQLAlchemy
import string
from flask_sslify import SSLify
import urllib
import requests
from xhtml2pdf import pisa
from io import BytesIO
import datetime
import markdown

# configuration
#########################################

app = Flask(__name__)

app.debug = True

sslify = SSLify( app )

S3 = S3Connection()
S3B = S3.get_bucket( os.environ[ 'AWS_S3_BUCKET' ] , validate=False )

SES = SESConnection()

app.config[ 'MAX_CONTENT_LENGTH' ] = 16 * 1024 * 1024
app.config[ 'UPLOAD_FOLDER' ] = './temp'

app.config[ 'SQLALCHEMY_DATABASE_URI' ] = os.environ[ 'DATABASE_URL' ]
db = SQLAlchemy( app )

app.secret_key = os.environ[ 'APP_SECRET_KEY' ]

ziply_salt = os.environ[ 'ZIPLY_SALT' ]

ziply_domain = os.environ[ 'ZIPLY_DOMAIN' ]

# Models
##########################################

class User( db.Model ):
    id = db.Column( db.Integer , primary_key=True )
    email = db.Column( db.String( 128 ) , unique=True )
    token = db.Column( db.String( 128 ) )

    def __init__( self , email , token ):
        self.email = email
        self.token = token

    def __repr__( self ):
        return '<User %r>' % self.email



class Template( db.Model ):
    id = db.Column( db.Integer , primary_key=True )
    userid = db.Column( db.Integer )
    name = db.Column( db.String( 100 ) )
    text = db.Column( db.Text )
    def __init__( self , userid , name , text ):
        self.userid = userid
        self.name = name
        self.text = text

    def __repr__( self ):
        return '<Template %r>' % self.name



class Draft( db.Model ):
    id = db.Column( db.Integer , primary_key=True )
    userid = db.Column( db.Integer )
    name = db.Column( db.String( 100 ) )
    text = db.Column( db.Text )
    signers = db.Column( db.Text )

    def __init__( self , userid , name , text , signers ):
        self.userid = userid
        self.name = name
        self.text = text
        self.signers = signers

    def __repr__( self ):
        return '<Draft %r>' % self.name



class Agreement( db.Model ):
    id = db.Column( db.Integer , primary_key=True )
    userid = db.Column( db.Integer )
    name = db.Column( db.String( 100 ) )
    text = db.Column( db.Text )
    signers = db.Column( db.Text )
    url = db.Column( db.Text )

    def __init__( self , userid , name , text , signers , url ):
        self.userid = userid
        self.name = name
        self.text = text
        self.signers = signers
        self.url = url

    def __repr__( self ):
        return '<Agreement %r>' % self.name



class Document( db.Model ):
    id = db.Column( db.Integer , primary_key=True )
    name = db.Column( db.String( 100 ) )
    text = db.Column( db.Text )

    def __init__( self , userid , name , text ):
        self.name = name
        self.text = text

    def __repr__( self ):
        return '<Document %r>' % self.name


#helper methods
####################################


def pdf_header( name ):
    name = name.upper()
    return """<html>
    <style>
    @page {
      margin: 1cm;
      margin-bottom: 1.5cm;
        font-family: Georgia;
        font-size: 20px;
      @frame footer {
        -pdf-frame-content: footerContent;
        bottom: 0cm;
        margin-left: 1cm;
        margin-right: 1cm;
        height: 1cm;
      }
    }
    img { zoom: 80%; }
    </style>
<body style="font-size:18px;">
    """ + datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p") + """
    <p style="font-weight:bold;font-size:20px;">""" + name + "</p>"


def pdf_footer( name ):
    return """<div id="footerContent" style="text-align:right;">""" + name + """ - Page: <pdf:pagenumber>/<pdf:pagecount>
    </div>
</body>
</html>"""


def accountHash( email ):
    return hashlib.sha512( ziply_salt + email ).hexdigest()

def accountToken( email ):
    return hashlib.sha512( ziply_salt + email + str( time.time() ) ).hexdigest()

def createPDF( filename , template  ):
    dst = BytesIO()
    pisa.CreatePDF( template , dst , show_error_as_pdf=True )
    response = make_response( dst.getvalue() )
    response.headers['Content-Disposition'] = "attachment; filename='" + filename + "'"
    response.mimetype = 'application/pdf'
    return response

def createPDF2( filename , template ):
    dst = BytesIO()
    pisa.CreatePDF( template , dst , show_error_as_pdf=True )
    return dst.getvalue()


# asset routes
####################################

@app.route('/favicon.ico')
def favicon():
    return send_from_directory( os.path.join(app.root_path , 'static' ) , 'img/favicon.ico' )

@app.route('/apple-touch-icon-57x57-precomposed.png')
def touchiconpre57():
    return send_from_directory( os.path.join(app.root_path , 'static' ) , 'img/apple-touch-icon-57x57-precomposed.png' )

@app.route('/apple-touch-icon-72x72-precomposed.png')
def touchiconpre72():
    return send_from_directory( os.path.join(app.root_path , 'static' ) , 'img/apple-touch-icon-72x72-precomposed.png' )

@app.route('/apple-touch-icon-114x114-precomposed.png')
def touchiconpre114():
    return send_from_directory( os.path.join(app.root_path , 'static' ) , 'img/apple-touch-icon-114x114-precomposed.png' )

@app.route('/apple-touch-icon-144x144-precomposed.png')
def touchiconpre144():
    return send_from_directory( os.path.join(app.root_path , 'static' ) , 'img/apple-touch-icon-144x144-precomposed.png' )

@app.route('/apple-touch-icon-precomposed.png')
def touchiconpre():
    return send_from_directory( os.path.join(app.root_path , 'static' ) , 'img/apple-touch-icon-precomposed.png' )

@app.route('/apple-touch-icon.png')
def touchicon():
    return send_from_directory( os.path.join(app.root_path , 'static' ) , 'img/apple-touch-icon.png' )


# SF integration routes
####################################


@app.route( '/salesforce/login/' )
def sf_login():
    f = { 'response_type' : 'code', 'client_id' : os.environ['SFCLIENT'] , 'redirect_uri' : 'https://' + ziply_domain + '/salesforce/auth/' }
    return redirect( "https://login.salesforce.com/services/oauth2/authorize?" + urllib.urlencode( f ) )

@app.route( '/salesforce/auth/' )
def sf_auth():
    code = request.args.get( 'code' , '' )
    payload = {'code': code , 'grant_type': 'authorization_code' , 'client_id' : os.environ['SFCLIENT'] , 'client_secret' : os.environ['SFSECRET'] , 'redirect_uri' : 'https://' + ziply_domain + '/salesforce/auth/' }
    r = requests.post( "https://login.salesforce.com/services/oauth2/token" , params=payload )
    j1 = r.json()
    headers = {
        "Authorization": "Bearer " + j1['access_token']
    }
    r2 = requests.get( j1['id'] , headers=headers )
    j2 = r2.json()
    user = User.query.filter_by( email=j2['email'] ).first()
    if user is None:
        user = User( j2['email'] , accountHash( j2['email'] ) )
        db.session.add( user )
        db.session.commit()

        #loop over documents and add Templates
        docs = Document.query.all()
        for doc in docs:
            a = Template( user.id , doc.name , doc.text )
            db.session.add( a )
            db.session.commit()

    session[ 'uid' ] = user.id
    session[ 'email' ] = user.email
    session[ 'token' ] = user.token

    return redirect( url_for( 'index' ) )


# base app routes
####################################

@app.route( '/' )
def index():
    if 'email' in session:
        return render_template( '_welcome.html' , email=session[ 'email' ] )
    return redirect( url_for( 'login' ) )


@app.route( '/agreements' )
def agreements():
    if 'email' in session:
        items = Agreement.query.filter_by( userid = session[ 'uid' ] ).all()
        return render_template( '_agreements.html' , email=session[ 'email' ] , items=items )
    return redirect( url_for( 'login' ) )


@app.route( '/drafts' )
def drafts():
    if 'email' in session:
        items = Draft.query.filter_by( userid = session[ 'uid' ] ).all()
        return render_template( '_drafts.html' , email=session[ 'email' ] , items=items )
    return redirect( url_for( 'login' ) )


@app.route( '/templates' )
def templates():
    if 'email' in session:
        items = Template.query.filter_by( userid = session[ 'uid' ] ).all()
        return render_template( '_templates.html' , email=session[ 'email' ] , items = items )
    return redirect( url_for( 'login' ) )


@app.route( '/template/edit/<id>' , methods=[ 'GET' , 'POST' ] )
def template_edit( id ):
    if 'email' in session:
        item = Template.query.filter_by( id = id ).first()
        if request.method == 'POST':
            if item.userid is int( session[ 'uid' ] ):
                item.name = request.form['name']
                item.text = request.form['text']
                db.session.commit()
            return redirect( '/template/edit/' + id  )
        else:
            if item.userid is int( session[ 'uid' ] ):
                return render_template( '_template_edit.html' , email=session[ 'email' ] , item = item )
            return render_template( '_404.html' , email = session[ 'email' ] ) , 404
    return redirect( url_for( 'login' ) )


@app.route( '/template/delete/<id>' , methods=[ 'GET' ] )
def template_delete( id ):
    if 'email' in session:
        item = Template.query.filter_by( id = id ).first()
        if item.userid is int( session[ 'uid' ] ):
            db.session.delete( item )
            db.session.commit()
        return redirect( url_for( 'templates') )
    return redirect( url_for( 'login' ) )


@app.route( '/template/pdf/<id>' , methods=[ 'GET' ] )
def template_pdf( id ):
    if 'email' in session:
        item = Template.query.filter_by( id = id ).first()
        if item.userid is int( session[ 'uid' ] ):
            path = item.name + '.pdf'
            header = pdf_header( item.name )
            markdn = markdown.markdown( item.text )
            footer = pdf_footer( item.name )
            return createPDF( path , header + markdn + footer );
        return render_template( '_404.html' , email = session[ 'email' ] ) , 404
    return redirect( url_for( 'login' ) )


@app.route( '/draft/new/<id>' , methods=[ 'GET' ] )
def draft_new( id ):
    if 'email' in session:
        item = Template.query.filter_by( id = id ).first()
        if item.userid is int( session[ 'uid' ] ):
            a = Draft( item.userid , item.name , item.text , session[ 'email' ] )
            db.session.add( a )
            db.session.commit()
            return redirect( '/draft/edit/' + str( a.id ) )
        return render_template( '_404.html' , email = session[ 'email' ] ) , 404
    return redirect( url_for( 'login' ) )


@app.route( '/draft/edit/<id>' , methods=[ 'GET' , 'POST' ] )
def draft_edit( id ):
    if 'email' in session:
        item = Draft.query.filter_by( id = id ).first()
        if request.method == 'POST':
            if item.userid is int( session[ 'uid' ] ):
                item.name = request.form['name']
                item.text = request.form['text']
                item.signers = request.form['signers']
                db.session.commit()
            return redirect( '/draft/edit/' + id  )
        else:
            if item.userid is int( session[ 'uid' ] ):
                return render_template( '_draft_edit.html' , email=session[ 'email' ] , item = item )
            return render_template( '_404.html' , email = session[ 'email' ] ) , 404
    return redirect( url_for( 'login' ) )


@app.route( '/draft/delete/<id>' , methods=[ 'GET' ] )
def draft_delete( id ):
    if 'email' in session:
        item = Draft.query.filter_by( id = id ).first()
        if item.userid is int( session[ 'uid' ] ):
            db.session.delete( item )
            db.session.commit()
        return redirect( url_for( 'drafts') )
    return redirect( url_for( 'login' ) )


@app.route( '/draft/pdf/<id>' , methods=[ 'GET' ] )
def draft_review( id ):
    if 'email' in session:
        item = Draft.query.filter_by( id = id ).first()
        if item.userid is int( session[ 'uid' ] ):
            path = item.name + '.pdf'
            header = pdf_header( item.name )
            markdn = markdown.markdown( item.text )
            footer = pdf_footer( item.name )
            return createPDF( path , header + markdn + footer );
        return render_template( '_404.html' , email = session[ 'email' ] ) , 404
    return redirect( url_for( 'login' ) )


@app.route( '/draft/sign/<id>' , methods=[ 'GET' , 'POST' ] )
def draft_sign( id ):
    if 'email' in session:
        item = Draft.query.filter_by( id = id ).first()
        if item.userid is int( session[ 'uid' ] ):
            return render_template( '_draft_sign.html' , email=session[ 'email' ] , item = item )
        return render_template( '_404.html' , email = session[ 'email' ] ) , 404
    return redirect( url_for( 'login' ) )


@app.route( '/draft/complete/<id>' , methods=[ 'POST' ] )
def draft_complete( id ):
    if 'email' in session:
        item = Draft.query.filter_by( id = id ).first()
        if item.userid is int( session[ 'uid' ] ):
            sigLength = int( request.form[ 'signature_length' ] )
            signAdd = ""
            for x in range( 0 , sigLength ):
                imageFileId = "temp/" + id + "_" + str(x) + ".png"
                signAdd = signAdd + "<br/><img src='" + imageFileId + "'/>"
                datauri = request.form[ 's_' + str(x) ]
                imagestr = re.search( r'base64,(.*)' , datauri ).group(1)
                imageFileOut = open( imageFileId , 'wb' )
                imageFileOut.write( imagestr.decode( 'base64' ) )
                imageFileOut.close()
            path = item.name + '.pdf'
            header = pdf_header( item.name )
            markdn = markdown.markdown( item.text )
            footer = pdf_footer( item.name )
            data = createPDF2( path , header + markdn + signAdd + footer );
            outpath = '/' + session[ 'token' ] + '/' + str( int( time.time() ) ) + '.pdf'
            k = S3B.new_key( outpath )
            k.set_contents_from_file( StringIO( data ) )
            a = Agreement( item.userid , item.name , item.text , item.signers , outpath )
            db.session.delete( item )
            db.session.add( a )
            db.session.commit()

        return "0"
    return "0"


@app.route( '/agreement/<id>' , methods=[ 'GET' ] )
def agreement_view( id ):
    if 'email' in session:
        item = Agreement.query.filter_by( id = id ).first()
        if item.userid is int( session[ 'uid' ] ):
            return render_template( '_agreement_view.html' , email=session[ 'email' ] , item = item )
        return render_template( '_404.html' , email = session[ 'email' ] ) , 404
    return redirect( url_for( 'login' ) )


@app.route( '/agreement/pdf/<id>' , methods=[ 'GET' ] )
def agreement_pdf( id ):
    if 'email' in session:
        item = Agreement.query.filter_by( id = id ).first()
        if item.userid is int( session[ 'uid' ] ):
            key = S3B.get_key( item.url )
            if key:
                pdf_out = key.get_contents_as_string()
                response = make_response( pdf_out )
                response.mimetype = 'application/pdf'
                return response
        return render_template( '404.html' , email = session[ 'email' ] ) , 404
    return redirect( url_for( 'login' ) )


@app.route( '/account' )
def account():
    if 'email' in session:
        return render_template( '_account.html' , email=session[ 'email' ] )
    return redirect( url_for( 'login' ) )


@app.route( '/account/restore' , methods=[ 'GET' ] )
def account_restore():
    if 'email' in session:
        docs = Document.query.all()
        for doc in docs:
            a = Template( int( session[ 'uid' ] ) , doc.name , doc.text )
            db.session.add( a )
            db.session.commit()
        return redirect( url_for( 'account' ) )
    return redirect( url_for( 'login' ) )


@app.route( '/login' , methods=[ 'GET' ] )
def login():
    return render_template( '_login.html' )


@app.route( '/logout' )
def logout():
    # remove the uid from the session if it's there
    session.pop( 'email' , None )
    session.pop( 'token' , None )
    session.pop( 'uid' , None )
    return redirect( url_for( 'login' ) )
