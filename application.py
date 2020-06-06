import os

import json
import requests

from flask import Flask, render_template,request,redirect,g,url_for,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helper import *

app = Flask(__name__)
app.secret_key='PAS074BEL033'

# Check for environment variable
#if not ("postgres://svnvtjemvqnasi:0367c449c3f870110f30008d5500264e9ff39065cf04d3676e6794b44f41ba90@ec2-50-17-178-87.compute-1.amazonaws.com:5432/dfb6qsqakpdnee"):
 #   raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgres://syahiefttgcgvy:db851348c34b1236c173ba3e53c344b48f6b32f569c78dd10a24333ca00f9b1d@ec2-54-81-37-115.compute-1.amazonaws.com:5432/d1q9cltmus4bb3")
db = scoped_session(sessionmaker(bind=engine))


#index page
@app.route("/")
def index():
	return render_template("layout.html")
#login page
@app.route("/login",methods=["GET","POST"])
def login():
	#getting username and database
	if request.method=="POST":
		session.pop('user',None)
		username=request.form.get("name")
		password=request.form.get("password")
		logging=db.execute("SELECT username,password FROM  users WHERE username=:username AND password=:password",{"username":username,"password":password}).fetchone()
		if logging is None:
			error="Username or Password is wrong.Try again."
			return render_template("login.html",error=error)
			
		session['user']=username
		return redirect(url_for('search'))
	session.pop('user',None)
	return render_template("login.html")
#page for registration
@app.route("/signin",methods=["GET","POST"])
def signin():
	if request.method=="POST":
		#taking the information
		username=request.form.get("username")
		password=request.form.get("password")
		email=request.form.get("email")
		number=request.form.get("phone")
		#checking the information for unique identity
		registering=db.execute("SELECT username,email,phone FROM  users WHERE username=:username",{"username":username}).fetchone()
		if registering is not None:
			error="username taken"
			return render_template("signin.html",error=error)
		registering=db.execute("SELECT username,email,phone FROM  users WHERE email=:email",{"email":email}).fetchone()
		if  registering is not None:
			error="email already registerd"
			return render_template("signin.html",error=error)

		db.execute("INSERT INTO users(username,password,email,phone) VALUES (:username,:password,:email,:phone)",{"username":username,"password":password,"email":email,"phone":number})
		db.commit()
		return redirect(url_for('login'))
	return render_template("signin.html")

@app.route("/search", methods=["GET","POST"])

def search():
	username=session.get('user')
	if username is None:
		return render_template("login.html")	
	if request.method=="POST":
		booksearch=request.form.get("booksearch")
		allbooks=db.execute("SELECT * FROM books WHERE isbn iLIKE '%"+booksearch+"%' OR title iLIKE '%"+booksearch+"%' OR author LIKE '%"+booksearch+"%'").fetchall()
		if allbooks is None:
			error="There is no such book in our database."
			return render_template("allbooks.html", error=error)
		else:
			return render_template("allbooks.html",allbooks=allbooks)
	allbooks=db.execute("SELECT * FROM books").fetchall()
	return render_template("search.html",allbooks=allbooks)



@app.route("/book/<string:isbn>",methods=["GET","POST"])
def book(isbn):
	username=session.get('user')
	if username is None:
		return render_template("login.html")
	book=db.execute("SELECT * FROM books WHERE isbn=:isbn",{"isbn" : isbn}).fetchone()
	if book is None:
		error="No such book."
		return render_template("book.html", error=error)
	review=db.execute("SELECT * FROM reviews WHERE isbn=:isbn",{"isbn":isbn}).fetchall()
	if review is None:
		error="No reviews."
		return render_template("book.html",book=book, error=error)
	x =10 - len(isbn)
	isbn1 = isbn
	for i in range(x):
		isbn1 = "0" + isbn1	
	res = requests.get("https://www.goodreads.com/book/review_counts.json",params={"key": "l9Zjg0kQ4XBSgWzF4swoEw", "isbns":isbn1}).json()["books"][0]
	ratings_count = res["ratings_count"]
	average_rating = res["average_rating"]
	if request.method == "POST":
		comment = db.execute("SELECT * FROM reviews WHERE username= :username and isbn=:isbn",{"username":username,"isbn":isbn}).fetchone()
		if comment is None:
			review=request.form.get("review")
			rating=request.form.get("rating")
			db.execute("INSERT INTO reviews(review,rating,username,isbn) VALUES(:review,:rating,:username,:isbn)",{"review":review,"rating":rating,"username":username,"isbn":isbn})
			db.commit()
		else:
			review = db.execute("SELECT * FROM reviews WHERE isbn=:isbn",{"isbn":isbn}).fetchall()
			return render_template("book.html", book=book, review=review,error="Already Commented",ratings_count=ratings_count,average_rating=average_rating)
	review=db.execute("SELECT * FROM reviews WHERE isbn=:isbn",{"isbn":isbn}).fetchall()
	return render_template("book.html", book=book, review=review,ratings_count=ratings_count,average_rating=average_rating)

@app.route("/api/<string:isbn>")
def api(isbn):
    book=db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn":isbn}).fetchone()
    x =10 - len(isbn)
    isbn1 = isbn
    for i in range(x):
    	isbn1 = "0" + isbn1
    if book==None:
        return render_template('404.html')
    res = requests.get("https://www.goodreads.com/book/review_counts.json",params={"key": "l9Zjg0kQ4XBSgWzF4swoEw", "isbns":isbn1}).json()["books"][0]
    ratings_count = res["ratings_count"]
    average_rating = res["average_rating"]
    x = {
    "title": book.title,
    "author": book.author,
    "year": 1333,
    "isbn": isbn,
    "review_count": ratings_count,
    "average_score": average_rating
    }
    return jsonify(x)

@app.route("/logout")
def logout():
	session.pop('user',None)
	return redirect(url_for('login'))






if __name__ == '__main__':
 	main() 