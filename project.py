from flask import Flask, render_template, request, redirect, url_for, jsonify, session, escape
from sqlalchemy import create_engine, desc, func, and_
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Items, Categories
from functools import wraps
from flask.ext.github import GitHub

app = Flask(__name__)

#Github authorization configuration
app.config['GITHUB_CLIENT_ID'] = 'a0e593ee7bd5a5c57017'
app.config['GITHUB_CLIENT_SECRET'] = 'ea8eb7257d0524e89442fd9a097c0c3d667b11f1'
github = GitHub(app)

#Setup the ORM interface for use within this file
engine = create_engine('postgresql:///item_catalog.db')
Base.metadata.bind=engine
DBSession = sessionmaker(bind = engine)
db_session = DBSession()

# AUTHORIZATION LOGIC ##################################
#Display page for login
@app.route('/catalog/login')
def DisplayLogin():
	return github.authorize()

@app.route('/github-callback')
@github.authorized_handler
def authorized(oauth_token):
		if oauth_token is None:
			return DisplayHome(oauth_token, message="Authorization failed.")
			#return render_template('/home', message="Authorization failed.")
		#return render_template('/home', message="Authorization successful.")
		return DisplayHome(oauth_token,  message="Authorization successful.")

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
def DisplayHome(oauth_token=None, message=''):
	if oauth_token is not None:
		session['username'] = oauth_token
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
	return render_template('home.html', categories=categories, items=latest_items, loggedIn=loggedIn, message=message)

@app.route('/catalog/<string:category_id>/<string:category_item_id>/')
def DisplayCatalogItem(category_id, category_item_id):
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
	return render_template('category_list.html', items=items_in_category, categories=categories, loggedIn=loggedIn, category=category_id)

@app.route('/catalog/<string:category_item_id>/edit')
@auth_user
def DisplayEditItem(category_item_id):
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
	loggedIn = False
	if 'username' in session:
		loggedIn = True
	else:
		return render_template('error.html', loggedIn=loggedIn, message='You need to log in first.')
	try:
		#Grab the desired deletion target (by name), then delete and commit
		itemId = request.form['TargetName']
		targetItem = db_session.query(Items).filter_by(id=itemId).first()
		db_session.delete(targetItem);
		db_session.commit()
	except:
		print 'Error in delete_post(). Rolling back.'
		db_session.rollback() #Be sure to rollback due to the exception
		return render_template('error.html', loggedIn=loggedIn, message='An unrecoverable error has occured.')
	return redirect(url_for('DisplayHome'))
		

@app.route('/catalog/edit_item', methods=['POST'])
def edit_post():
	loggedIn = False
	if 'username' in session:
		loggedIn = True
	else:
		return render_template('error.html', loggedIn=loggedIn, message='You need to log in first.')
	try:
		#Grab the new item details from the form, create an item in the ORM, then merge it into the table
		itemName = request.form['NewName']
		itemDescription = request.form['NewDescription']
		itemCategory = request.form['NewCategory']
		itemId = request.form['OldId']
		newItem = Items(id=itemId, name = itemName, description = itemDescription, category = itemCategory, date_added = func.now())
		db_session.merge(newItem)
		db_session.commit()
	except:
		print 'Error in edit_post(). Rolling back.'
		db_session.rollback() #Be sure to rollback in the case of an exception
		return render_template('error.html', loggedIn=loggedIn, message='An unrecoverable error has occured.')
	return redirect(url_for('DisplayHome'))
		

@app.route('/catalog/add_item', methods=['POST'])
def add_post():
	loggedIn = False
	if 'username' in session:
		loggedIn = True
	else:
		return render_template('error.html', loggedIn=loggedIn, message='You need to log in first.')
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

@app.route('/catalog/add_category', methods=['POST'])
def add_category():
	loggedIn = False
	if 'username' in session:
		loggedIn = True
	else:
		return render_template('error.html', loggedIn=loggedIn, message='You need to log in first.')
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
