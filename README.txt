AUTHOR:	
	Ryan Chrisco, 3/29/2015
FILES: 
	project.py
	database_Setup.py
	static/style.css
	templates/layout.html
	templates/home.html
	templates/category_list.html
	templates/item.html
	templates/add_item.html
	templates/add_user.html
	templates/delete.html
	templates/edit.html
	templates/login.html
	templates/add_category.html
	templates/error.html
DESCRIPTION: 
	A website that stores and displays a list of "items", grouped by "category", along with descriptions.
DIRECTIONS: 
	Install Postgres SQL 9.3.6
    Create a database named "item_catalog.db" in Postgres by issuing the command "createdb item_catalog.db" from the shell
    Install Python 2.7.6
    Run "database_Setup.py" from the shell (this creates all necessary DB objects)
    Run "project.py" from the shell (this starts the webservice)
    Access it at "localhost:5000/home" (URL mappings are identical to those in the demonstration project)
    	-localhost:5000/catalog/<CATEGORY_NAME>/items			Displays a list of items in a specified category
    	-localhost:5000/catalog/<CATEGORY_NAME>/<ITEM_NAME>		Displays specific item
    	-localhost:5000/catalog/<ITEM_NAME>/edit				Displays an item and allows for editing
    	-localhost:5000/catalog/<ITEM_NAME>/delete				Displays an item and prompts for deletion
    	-localhost:5000/catalog/add_item						Displays a form that allows an item to be added (must be logged in)
    	-localhost:5000/catalog/add_category					Displays a form that allows a category to be added (must be logged in)
    	-localhost:5000/catalog/add_user						Displays a form that allows a user to be added (must be logged in)
    	-localhost:5000/catalog.json							Displays a JSON string response
NOTES: 
	The webservice creates a default user under the name password "admin/admin" for ease of testing.
	Once logged in, any user can create another user (but may not delete old users).