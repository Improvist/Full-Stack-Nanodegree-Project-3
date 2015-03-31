AUTHOR:	
	Ryan Chrisco, 3/30/2015
FILES: 
	project.py
	database_setup.py
	static/style.css
	templates/layout.html
	templates/home.html
	templates/category_list.html
	templates/item.html
	templates/add_item.html
	templates/delete.html
	templates/edit.html
	templates/login.html
	templates/add_category.html
	templates/error.html
DESCRIPTION: 
	A website that stores and displays a list of "items", grouped by "category", along with descriptions.
	Uses Github authentication for user authentication.
DIRECTIONS:
	Manual: 
		Install Postgres SQL 9.3.6 (http://www.postgresql.org/download/)
	    Create a database named "item_catalog.db" in Postgres by issuing the command "createdb item_catalog.db" from the shell
	    Install Python 2.7.6 (https://www.python.org/downloads/) - check to ensure you have the "functools" module
	    Install Flask 0.10 (http://flask.pocoo.org/docs/0.10/installation/)
	    Install SQLAlchemy 1.0 (http://www.sqlalchemy.org/download.html)
	    Install Github-Flask (https://github-flask.readthedocs.org/en/latest/)
    ----
    With Vagrant:
    	Install Vagrant (https://www.vagrantup.com/)
    	Install VirtualBox (https://www.virtualbox.org/)
    	Close the fullstack-nanodegree-vm-repository  (https://github.com/udacity/fullstack-nanodegree-vm/tree/master/vagrant)
    	Install Github-Flask
    	Ensure you have all necessary installations by verifying them individually. If one is missing, use the links above to download it and install it.
    ----
    Either with Vagrant or Manually, you then will run these commands:
	    Run "database_Setup.py" from the shell (this creates all necessary DB objects)
	    Run "project.py" from the shell (this starts the webservice)
	    Access it at "localhost:5000/home" (URL mappings are identical to those in the demonstration project)
	    	-localhost:5000/catalog/<CATEGORY_NAME>/items			Displays a list of items in a specified category
	    	-localhost:5000/catalog/<CATEGORY_NAME>/<ITEM_NAME>		Displays specific item
	    	-localhost:5000/catalog/<ITEM_NAME>/edit				Displays an item and allows for editing (must be logged in)
	    	-localhost:5000/catalog/<ITEM_NAME>/delete				Displays an item and prompts for deletion (must be logged in)
	    	-localhost:5000/catalog/add_item						Displays a form that allows an item to be added (must be logged in)
	    	-localhost:5000/catalog/add_category					Displays a form that allows a category to be added (must be logged in)
	    	-localhost:5000/catalog.json							Displays a JSON string response