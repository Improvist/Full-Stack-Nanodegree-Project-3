from flask import Flask, render_template, request, redirect, url_for, jsonify, session, escape
from sqlalchemy import create_engine, desc, func, and_
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Items, Users, Categories
from functools import wraps
from werkzeug import generate_password_hash

app = Flask(__name__)

#Setup the ORM interface for use within this file
engine = create_engine('postgresql:///item_catalog.db')
Base.metadata.bind=engine
DBSession = sessionmaker(bind = engine)
db_session = DBSession()
#Insert default user/pass combo into Users
BasicUser = Users(name='Default',username='admin',password='admin')
db_session.merge(BasicUser)
db_session.commit()

# AUTHORIZATION LOGIC ##################################
#Display page for login
@app.route('/catalog/login')
def DisplayLogin():
	return render_template('login.html')

#Method for determining if a user is in the system
@app.route('/catalog/auth_user', methods=['POST']) 
def auth_user():
	username = request.form['username']
	password = request.form['password']
	resultSetCount = db_session.query(Users).filter(and_(Users.username==username,Users.password==password)).count()
	#If a record matches the users credentials; they are a user
	if resultSetCount > 0:
		session['username'] = username
		return redirect(url_for('DisplayHome'))
	else:
		#Alert if the user was not actually in the system
		return render_template('login.html', message='No user/password combination found.')
#Routing that removes the user's login from their session (logging them out)
@app.route('/catalog/logout', methods=['POST'])
def signout():
	if 'username' not in session:
		return redirect(url_for('DisplayHome'))
	session.pop('username',None)
	return redirect(url_for('DisplayHome'))

#Flask decorator to define which routing methods below require authorization
def auth_user(f):
	@wraps(f)
	def check_user_status(*args, **kwargs):
		if 'username' not in session:
			return redirect(url_for('DisplayLogin'))
		return f(*args, **kwargs)
	return check_user_status

# VIEW MAPPINGS ########################################
@app.route('/')
@app.route('/home')
def DisplayHome():
	#Check login status and send it to the template
	loggedIn = False
	if 'username' in session:
		loggedIn = True
	#Displays all categories and the 10 most recently added items
	try:
		categories = db_session.query(Categories).all()
		latest_items = db_session.query(Items).order_by(desc(Items.date_added)).limit(10)
	except:
		print 'An error has occurred in DisplayHome()'
		return render_template('error.html', loggedIn=loggedIn, message='An unrecoverable error has occured.')
	return render_template('home.html', categories=categories, items=latest_items, loggedIn=loggedIn)

@app.route('/catalog/<string:category_id>/<string:category_item_id>/')
def DisplayCatalogItem(category_id, category_item_id):
	#Check login status and send it to the template
	loggedIn = False
	if 'username' in session:
		loggedIn = True
	#Grab the item from the item table
	try:
		item = db_session.query(Items).filter_by(name=category_item_id).first()
	except:
		print 'An error has occured in DisplayCatalogItem.'
		return render_template('error.html', loggedIn=loggedIn, message='An unrecoverable error has occured.')
	return render_template('item.html', Item=item, loggedIn=loggedIn)

@app.route('/catalog/<string:category_id>/items')
def DisplayCategory(category_id):
	#Check login status and send it to the template
	loggedIn = False
	if 'username' in session:
		loggedIn = True
	try:
		#Grab all categories and then the list of items in the specified category
		categories = db_session.query(Categories).all()
		items_in_category = db_session.query(Items).filter_by(category=category_id).all()
	except:
		print 'Error in DisplayCategory()'
		return render_template('error.html', loggedIn=loggedIn, message='An unrecoverable error has occured.')
	return render_template('category_list.html', items=items_in_category, categories=categories, loggedIn=loggedIn)


@app.route('/catalog/add_user')
@auth_user
def DisplayAddUser():
	#Check login status and send it to the template
	loggedIn = False
	if 'username' in session:
		loggedIn = True
	return render_template('add_user.html', loggedIn=loggedIn)

@app.route('/catalog/<string:category_item_id>/edit')
@auth_user
def DisplayEditItem(category_item_id):
	#Check login status and send it to the template
	loggedIn = False
	if 'username' in session:
		loggedIn = True
	try:
		categories = db_session.query(Categories).all()
		item = db_session.query(Items).filter_by(name=category_item_id).first()
	except:
		print 'Error in DisplayEditItem'
		return render_template('error.html', loggedIn=loggedIn, message='An unrecoverable error has occured.')
	return render_template('edit.html', OldItem=item, options=categories, loggedIn=loggedIn)

@app.route('/catalog/<string:category_item_id>/delete')
@auth_user
def DisplayDeleteItem(category_item_id):
	#Check login status and send it to the template
	loggedIn = False
	if 'username' in session:
		loggedIn = True
	try:
		item = db_session.query(Items).filter_by(name=category_item_id).first()
	except:
		print 'An error has occurred in DisplayDeleteItem()'
		return render_template('error.html', loggedIn=loggedIn, message='An unrecoverable error has occured.')
	return render_template('delete.html', item=item, loggedIn=loggedIn, message='Are you sure you want to delete this item?')

@app.route('/catalog/add_item')
@auth_user
def DisplayAddItem():
	#Check login status and send it to the template
	loggedIn = False
	if 'username' in session:
		loggedIn = True
	try:
		#Grab all categories to display in page
		options = db_session.query(Categories).all()
	except:
		print 'Error in DisplayAddItem().'
		return render_template('error.html', loggedIn=loggedIn, message='An unrecoverable error has occured.')
	return render_template('add_item.html', options=options, loggedIn=loggedIn)

@app.route('/catalog/add_category')
@auth_user
def DisplayAddCategory():
	#Check login status and send it to the template
	loggedIn = False
	if 'username' in session:
		loggedIn = True
	return render_template('add_category.html', loggedIn=loggedIn)

@app.route('/catalog.json')
def DisplayCatalogJson():
	try:
		#Grab all of the items from the DB
		full_catalog = db_session.query(Items).all()
	except:
		print 'An error has occcurred in DisplayCatalogJson()'
		return "{message : 'ERROR'}"
	#Return the JSON-strong of the list of items under the array name "AllItems"
	return jsonify(AllItems=[i.serialize for i in full_catalog])

# LOGIC CONTROLLERS #########################################
# All of the logic controllers intercept on POST to receive form submissions
@app.route('/catalog/delete_item', methods=['POST'])
def delete_post():
	#Check login status and send it to the template if necessary
	loggedIn = False
	if 'username' in session:
		loggedIn = True
	try:
		#Grab the desired deletion target (by name), then delete and commit
		itemName = request.form['TargetName']
		targetItem = db_session.query(Items).filter_by(name=itemName).first()
		db_session.delete(targetItem);
		db_session.commit()
	except:
		print 'Error in delete_post(). Rolling back.'
		db_session.rollback() #Be sure to rollback due to the exception
		return render_template('error.html', loggedIn=loggedIn, message='An unrecoverable error has occured.')
	return redirect(url_for('DisplayHome'))
		

@app.route('/catalog/edit_item', methods=['POST'])
def edit_post():
	#Check login status and send it to the template if necessary
	loggedIn = False
	if 'username' in session:
		loggedIn = True
	try:
		#Grab the new item details from the form, create an item in the ORM, then merge it into the table
		itemName = request.form['NewName']
		itemDescription = request.form['NewDescription']
		itemCategory = request.form['NewCategory']
		newItem = Items(name = itemName, description = itemDescription, category = itemCategory, date_added = func.now())
		db_session.merge(newItem)
		db_session.commit()
	except:
		print 'Error in edit_post(). Rolling back.'
		db_session.rollback() #Be sure to rollback in the case of an exception
		return render_template('error.html', loggedIn=loggedIn, message='An unrecoverable error has occured.')
	return redirect(url_for('DisplayHome'))
		

@app.route('/catalog/add_item', methods=['POST'])
def add_post():
	#Check login status and send it to the template if necessary
	loggedIn = False
	if 'username' in session:
		loggedIn = True
	try:
		#Grab the new item and add/commit it to the DB
		itemName = request.form['ItemName']
		itemDescription = request.form['ItemDescription']
		itemCategory = request.form['ItemCategory']
		newItem = Items(name = itemName, description = itemDescription, category = itemCategory, date_added = func.now())
		db_session.add(newItem)
		db_session.commit()
	except:
		print 'Error in add_post(). Rolling back.'
		db_session.rollback() #Rollback DB in case of error
		return render_template('error.html', loggedIn=loggedIn, message='An unrecoverable error has occured.')
	return redirect(url_for('DisplayHome'))

@app.route('/catalog/add_user', methods=['POST'])
def add_user():
	#Check login status and send it to the template if necessary
	loggedIn = False
	if 'username' in session:
		loggedIn = True
	try:
		#Grab the new user data from the form and add/commit it to the DB
		realName = request.form['RealName']
		userName = request.form['Username']
		password = request.form['Password']
		cpass = request.form['ConfirmPassword']
		#If the passwords don't match, notify the user and do not insert
		if cpass != password:
			return render_template('add_user.html', message='Passwords do not match. Try again.', loggedIn=loggedIn)
		newUser = Users(name=realName, username=userName, password=password)
		db_session.add(newUser)
		db_session.commit()
	except:
		print 'Error in add_user(). Rolling back.'
		db_session.rollback() #Be sure to rollback if there's an exception
		return render_template('error.html', loggedIn=loggedIn, message='An unrecoverable error has occured.')
	return redirect(url_for('DisplayHome'))

@app.route('/catalog/add_category', methods=['POST'])
def add_category():
	#Check login status and send it to the template if necessary
	loggedIn = False
	if 'username' in session:
		loggedIn = True
	try:
		#Grab new category information from the form and add/commit it to the DB
		catName = request.form['CategoryName']
		catDescription = request.form['CategoryDescription']
		newCategory = Categories(name=catName, description=catDescription, date_added=func.now())
		db_session.add(newCategory)
		db_session.commit()
	except:
		print 'Error in add_category(). Rolling back.'
		db_session.rollback() #Be sure to rollback on an exception
		return render_template('error.html', loggedIn=loggedIn, message='An unrecoverable error has occured.')
	return redirect(url_for('DisplayHome'))

# DEBUG CODE #############################################

if __name__ == '__main__':
	app.secret_key = 'TEST'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
