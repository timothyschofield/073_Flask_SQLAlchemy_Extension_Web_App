"""
    Demonstrates Flask-SQLAlchemy extension with routes and web interface
    
    20 August 2024
    
    From
    https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/quickstart/
    
    Flask-SQLAlchemy is a wrapper around SQLAlchemy. 
    You should follow the SQLAlchemy Tutorial:
        https://docs.sqlalchemy.org/en/20/tutorial/index.html
    This program shows how to set up Flask-SQLAlchemy itself, not how to use SQLAlchemy. 
    Flask-SQLAlchemy sets up the engine and scoped session automatically, so you can skip those parts of the SQLAlchemy tutorial.
    
    pip list
    Flask   3.0.3
    
    pip install --upgrade SQLAlchemy
    SQLAlchemy  2.0.32
    
    pip install --upgrade Flask-SQLAlchemy
    Flask-SQLAlchemy  3.1.1
    
    To run:
    In terminal
    export FLASK_APP=app
    export FLASK_ENV=development
    flask run
    
    Ctrl-C to quit
    
    Go to http://127.0.0.1:5000
"""
import os
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy


#### Initialize the Extension ####
# If desired, you can enable SQLAlchemy’s native support for data classes by adding MappedAsDataclass as an additional parent class.
# https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html#native-support-for-dataclasses-mapped-as-orm-models
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
class Base(DeclarativeBase, MappedAsDataclass):
  pass

db = SQLAlchemy(model_class=Base)

##### Configure the Extension #####
# The next step is to connect the extension to your Flask app. 
# The only required Flask app config is the SQLALCHEMY_DATABASE_URI key.

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(basedir, 'project.db')

# initialize the app with the extension
db.init_app(app)

##### Define Models ####
# Subclass db.Model to define a model class. 
# The model will generate a table name by converting the CamelCase class name to snake_case.
# Defining a model does not create it in the database. 
# Use create_all() to create the models and tables after defining them.
# https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/models/
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str]

##### Create the Tables #####
# After all models and tables are defined, call SQLAlchemy.create_all() to create the table schema in the database.
# This requires an application context. Since you’re not in a request at this point, create one manually.
# create_all does not update tables if they are already in the database.
with app.app_context():
    db.create_all()

##### Query the Data #####
# Within a Flask view or CLI command, you can use db.session to execute queries and modify model data.
# SQLAlchemy automatically defines an __init__ method for each model that assigns any keyword arguments to corresponding database columns and other attributes.

# db.session.add(obj) adds an object to the session, to be inserted.
# Modifying an object’s attributes updates the object.
# db.session.delete(obj) deletes an object.
# Remember to call db.session.commit() after modifying, adding, or deleting any data.
#####
# db.session.execute(db.select(...)) constructs a query to select data from the database.
# Building queries is the main feature of SQLAlchemy, so you’ll want to read the tutorial on select to learn all about it.
#                                                                   https://docs.sqlalchemy.org/tutorial/data_select.html
# You’ll usually use the Result.scalars() method to get a list of results, or 
# the Result.scalar() method to get a single result.

# Using Model.query is considered legacy in SQLAlchemy.
# Prefer using db.session.execute(db.select(...)) instead.

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/users")
def user_list():
    users = db.session.execute(db.select(User).order_by(User.username)).scalars()
    return render_template("user/list.html", users=users)


@app.route("/users/create", methods=["GET", "POST"])
def user_create():
    if request.method == "POST":
        user = User(
            # is should be automaticaly generated
            username=request.form["username"],
            email=request.form["email"],
        )
        
        print(f"####################### {user.id} ############################")
        
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("user_detail", id=user.id))

    return render_template("user/create.html")

@app.route("/user/detail/<int:id>")
def user_detail(id):
    user = db.get_or_404(User, id)
    return render_template("user/detail.html", user=user)



