import os
import csv
import datetime
import psycopg2
#conn = psycopg2.connect("postgres://wpmhkfqhgmtkjh:24b1f12e9f359efb6ce64b162e0557a39ed574c4584f1c3633cf8a3e268c8285@ec2-50-17-90-177.compute-1.amazonaws.com:5432/d4rbrraqb0rupu",sslmode='require')

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session , sessionmaker

engine = create_engine("postgres://syahiefttgcgvy:db851348c34b1236c173ba3e53c344b48f6b32f569c78dd10a24333ca00f9b1d@ec2-54-81-37-115.compute-1.amazonaws.com:5432/d1q9cltmus4bb3")
db = scoped_session(sessionmaker(bind = engine))

def main():
	#creating database for users
	db.execute("CREATE TABLE users(id SERIAL PRIMARY KEY, username VARCHAR NOT NULL, password VARCHAR NOT NULL,email VARCHAR NOT NULL,phone VARCHAR NOT NULL)")
	# database for review  to be taken
	db.execute("CREATE TABLE reviews(id SERIAL PRIMARY KEY, review VARCHAR NOT NULL, rating INTEGER NOT NULL, username VARCHAR NOT NULL,isbn VARCHAR NOT NULL)")
	#database for books and adding from books.csv
	db.execute("CREATE TABLE books(id SERIAL PRIMARY KEY, isbn VARCHAR NOT NULL,title VARCHAR NOT NULL,author VARCHAR NOT NULL, year INTEGER NOT NULL)")

	f= open("books.csv")
	reader=csv.reader(f)
	for i, t, a, y in reader:
		if y=='year':
			print("Table columns added.")
		else:
			db.execute("INSERT INTO books (isbn,title,author,year) VALUES (:isbn,:title,:author,:year)",{"isbn":i,"title":t,"author":a,"year":y})
			print(f"Added book: {t} by {a} in {y}")
	print("All books added.")
	db.commit()

if __name__ == '__main__':
	main()