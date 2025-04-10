# Blog Application with Flask
Created a Blog Web Application with Flask, Jinja, and MySQL.
The app supports user registration, login, posting into the blog, editig or deleting the blog, and seeing their profile
Used many BootStrap templates found online for the front end desing

**NOTE: Im not attaching the db.yaml file since it has confidential information

### Database schema
* _**user.db**_
	+ **user_id** => int primary key, auto incremented at insersion
	+ **first_name** => varchar, stores user's first name
	+ **last_name** => varchar, stores user's last name
	+ **username** => varchar, stores user's username, unique values in the db
	+ **email** =>varchar, stores user's email, unique values in the db
	+ **password** => varchar, stores user's password, uses hash

* _**blog.db**_
	+ **blog id** => int primary key, auto incremented at insersion
	+ **title** => varchar, stores the blog post's title
	+ **author** => varchar, stores the blog post's author (first name + last name)
	+ **content**=> varchar, stores the blog post's content or body