#!/usr/bin/env python2

from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker, relationship, joinedload
from database_setup import Categorie, Base, CategorieItem, User
import string
import random
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response, jsonify
import requests
import psycopg2



app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "catalog"


engine = create_engine('postgresql://catalog:catalog/catalog')
Base.metadata.bind = engine
Session = sessionmaker(bind=engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def Showlogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if not make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius:150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash('Successfully disconnected.')
        return redirect(url_for('index'))
    else:
        response = make_response(
            json.dumps(
                'Failed to revoke token for given user.',
                400))
        response.headers['Content-Type'] = 'application/json'
        flash('Failed to revoke token for given user.')
        return redirect(url_for('index'))

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None


@app.route('/')
def index():
    categories = session.query(Categorie).all()
    '''items = session.query(CategorieItem).filter_by(
        CategorieItem.id).order_by(
        CategorieItem.id.desc()).limit(9).all()'''
    items = session.query(CategorieItem).order_by(
        CategorieItem.id.desc()).limit(9).all()
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template(
        'index.html',
        categories=categories,
        items=items,
        STATE=state)


@app.route('/catalog')
@app.route('/catalog/<string:categorie_name>/')
@app.route('/catalog/<string:categorie_name>/items')
def ShowItem(categorie_name='Soccer'):
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    categories = session.query(Categorie).all()
    categorie = session.query(Categorie).filter_by(name=categorie_name).one()
    items = session.query(CategorieItem).filter_by(
        categorie_name=categorie.name).all()
    if 'username' not in login_session:
        return render_template(
            'publiccatalog&item.html',
            categories=categories,
            categorie=categorie,
            items=items,
            STATE=state)
    else:
        return render_template(
            'catalog&item.html',
            categories=categories,
            categorie=categorie,
            items=items,
            STATE=state)


@app.route('/catalog/<string:categorie_name>/<string:item_name>')
def ShowInfo(categorie_name, item_name):
    categorie = session.query(Categorie).filter_by(name=categorie_name).one()
    item = session.query(CategorieItem).filter_by(name=item_name).one()
    creator = getUserInfo(item.user_id)
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template(
            'publicinfo.html', categorie=categorie, creator=creator,
            item=item)
    else:
        return render_template(
            'info.html',
            categorie=categorie,
            item=item,
            creator=creator)


@app.route('/catalog/<string:categorie_name>/new', methods=['GET', 'POST'])
def CreateItem(categorie_name):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newItem = CategorieItem(
            name=request.form['name'],
            description=request.form['description'],
            user_id=login_session['user_id'],
            categorie_name=categorie_name)
        session.add(newItem)
        flash('New Item %s Successfully Created' % newItem.name)
        session.commit()

        return redirect(url_for('ShowItem', categorie_name=categorie_name))
    else:
        return render_template('newitem.html', categorie_name=categorie_name)


@app.route(
    '/catalog/<string:categorie_name>/<string:item_name>/edit',
    methods=[
        'GET',
        'POST'])
def EditItem(categorie_name, item_name):
    editedItem = session.query(CategorieItem).filter_by(name=item_name).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedItem.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this item. Please create your own item in order to edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        flash('%s Successfully Edited' % editedItem.name)
        session.commit()
        return redirect(url_for('ShowItem', categorie_name=categorie_name))
    else:
        return render_template(
            'edititem.html', categorie_name=categorie_name, item=editedItem)


@app.route(
    '/catalog/<string:categorie_name>/<string:item_name>/delete',
    methods=[
        'GET',
        'POST'])
def DeleteItem(categorie_name, item_name):
    itemToDelete = session.query(CategorieItem).filter_by(name=item_name).one()
    C = session.query(Categorie).filter_by(name=categorie_name).one()
    if 'username' not in login_session:
        return redirect('/login')
    if itemToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this item. Please create your own item in order to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        flash('%s Successfully Deleted' % itemToDelete.name)
        session.commit()
        return redirect(url_for('ShowItem', categorie_name=categorie_name))
    else:
        return render_template('deletitem.html', A=C, B=itemToDelete)


# JSON APIs
@app.route('/catalog.json')
def CategoriesJSON():
    categories = session.query(Categorie).options(
        joinedload(Categorie.items)).all()
    data = dict(categories=[dict(c.serializable, items=[i.serializable
                                                        for i in c.items])
                            for c in categories])
    return jsonify(data)


# JSON APIs
@app.route('/catalog/<string:categorie_name>/JSON')
def EachCategoriesJSON(categorie_name):
    categorie = session.query(Categorie).filter_by(name=categorie_name).one()
    items = session.query(CategorieItem).filter_by(
        categorie_name=categorie.name).all()
    return jsonify(CategorieItems=[i.serializable for i in items])


# JSON APIs
@app.route('/catalog/<string:categorie_name>/<string:item_name>/JSON')
def EachItemJSON(categorie_name, item_name):
    categorie = session.query(Categorie).filter_by(name=categorie_name).one()
    item = session.query(CategorieItem).filter_by(
        categorie_name=categorie.name).filter_by(
        name=item_name).one()
    return jsonify(CategorieItems=item.serializable)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
