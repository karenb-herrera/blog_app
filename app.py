from flask import (Flask, render_template, request, redirect, session, flash)
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash, check_password_hash
import yaml
import os

app = Flask(__name__)
Bootstrap(app)
ckeditor = CKEditor(app)

# Setup
with open('db.yaml', 'r') as file:
    db = yaml.load(file, Loader=yaml.SafeLoader)
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' #return rows as dictionary, not tuples
mysql = MySQL(app)

app.config['SECRET_KEY'] = os.urandom(24) # to sign a cookie with a secure key of 24 bytes

# Index route
@app.route('/')
def index():
    cur = mysql.connection.cursor()

    # Get blogs for FYP
    get_query_info = cur.execute("SELECT * FROM blog")

    # If you found at least one entry in the query
    if get_query_info > 0:
        # Get all blogs
        blogs = cur.fetchall()
        cur.close()
        return render_template('index.html', blogs=blogs)
    
    cur.close()
    return render_template('index.html', blogs=None)

# All blogs route
@app.route('/blogs/<int:id>/')
def blogs(id):
    cur = mysql.connection.cursor()

    # Get all blogs
    get_query_blogs = cur.execute("SELECT * FROM blog WHERE blog_id = {}".format(id))

    # If you found at lease one entry in the query
    if get_query_blogs > 0:
        # Get the blog with the specific id
        blog = cur.fetchone()
        return render_template('blog.html', blog=blog)
    return 'Blog not found'

# Register route
@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_details = request.form

        # Check if the passwords are matching
        if user_details['password'] != user_details['confirm_password']:
            flash('Passwords do not match! Try again.', 'danger')
            return render_template('register.html')
        
        cur = mysql.connection.cursor()
        # Get all ther info and POST it to the database in user table
        cur.execute("INSERT INTO user(first_name, last_name, username, email, password) VALUES(%s,%s,%s,%s,%s)", \
                    (user_details['first_name'], user_details['last_name'], user_details['username'], user_details['email'], generate_password_hash(user_details['password'])))
        
        mysql.connection.commit()
        cur.close()
        flash('Thank you for registering!', 'success')
        return redirect('/login')
    return render_template('register.html')

# Login route
@app.route('/login/', methods=['GET', 'POST'])
def login():
        if request.method == 'POST':
            user_info = request.form
            username = user_info['username']

            cur = mysql.connection.cursor()
            # Get the username that matches the correct info from the database
            confirming_user = cur.execute("SELECT * FROM user WHERE username = %s", (username,))

            # If you found at least one entry in the query
            if confirming_user > 0:
                user = cur.fetchone()

                # Secure checking with hash encryption
                if check_password_hash(user['password'], user_info['password']):
                    session['firstName'] = user['first_name']
                    session['lastName'] = user['last_name']
                    session['user_id'] = user['user_id']
                    session['login'] = True
                    flash('Welcome ' + session['firstName'] + ". We missed you!", 'success')
                else:
                    cur.close()
                    flash('Password is invalid', 'danger')
                    return render_template('login.html')
            else:
                cur.close()
                flash('User does not exist', 'danger')
                return render_template('login.html')
            
            cur.close()
            return redirect('/')
        
        return render_template('login.html')

# Write a new post
@app.route('/posting/',methods=['GET', 'POST'])
def posting():
    if request.method == 'POST':
        # If the user is not logged
        if 'firstName' not in session:
            return redirect('/login')
        
        post = request.form
        title = post['title']
        content = post['content']
        author = session['firstName'] + ' ' + session['lastName']

        cur = mysql.connection.cursor()

        # POST an entry in the post db 
        cur.execute("INSERT INTO blog(title, content, author) VALUES(%s, %s, %s)", (title, content, author))
        mysql.connection.commit()
        cur.close()

        flash("Congrats on posting! We hope it gets viral!", 'success')
        return redirect('/')
    return render_template('posting.html')

# View my profile
@app.route('/profile/')
def profile():
    cur = mysql.connection.cursor()

    # Get all posts entry from the db
    author = session['firstName'] + ' ' + session['lastName']
    result = cur.execute("SELECT * FROM blog WHERE author = %s", (author,))

    # If you found at least one entry in the query
    if result > 0:
        all_blogs = cur.fetchall()
        return render_template('profile.html', all_blogs=all_blogs)
    else:
        return render_template('profile.html', all_blogs=None)
    
# Edit post
@app.route('/edit-post/<int:id>/', methods=['GET', 'POST'])
def edit_post(id):
    if request.method == 'POST':
        cur = mysql.connection.cursor()

        # Get the correct post and UPDATE it
        title = request.form['title']
        content = request.form['content']
        cur.execute("UPDATE blog SET title = %s, content = %s WHERE blog_id = %s", (title, content, id,))

        mysql.connection.commit()
        cur.close()
        flash('Blog updated successfully', 'success')
        return redirect('/blogs/{}'.format(id))
    
    cur = mysql.connect.cursor()
    result = cur.execute("SELECT * FROM blog WHERE blog_id = %s", (id,))

    # If you found at least one entry in the query, edit it
    if result> 0:
        blog = cur.fetchone()
        blog_form = {}
        blog_form['title'] = blog['title']
        blog_form['content'] = blog['content']
        return render_template('edit-post.html', blog_form=blog_form)

# Delete post
@app.route('/delete-post/<int:id>/')
def delete_post(id):
    cur = mysql.connection.cursor()

    # Find the respective post and DELETE it
    cur.execute("DELETE FROM blog WHERE blog_id = {}".format(id))
    mysql.connection.commit()
    flash("Your blog has been deleted", 'success')
    return redirect('/profile')

# Logout route
@app.route('/logout/')
def logout():
    session.clear()
    flash("You have been logged out", 'info')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)