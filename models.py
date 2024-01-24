from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Favorite(db.Model):
    __tablename__ = "favorite"
    book_id = db.Column(db.Integer(),db.ForeignKey('book.id'),primary_key=True)
    user_id = db.Column(db.Integer(),db.ForeignKey('user.id'),primary_key=True)

class Book_Author(db.Model):
    __tablename__ = "book_author_rel"
    book_id = db.Column(db.Integer(),db.ForeignKey('book.id'),primary_key=True)
    author_id = db.Column(db.Integer(),db.ForeignKey('author.id'),primary_key=True)

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer(),primary_key = True)
    firstname = db.Column(db.String(),nullable = False)
    lastname = db.Column(db.String())
    email = db.Column(db.String(),nullable = False, unique = True)
    password = db.Column(db.String(),nullable = False)
    type = db.Column(db.String(),nullable = False)

    favorites = db.relationship('Book',secondary='favorite',back_populate='user')

class Book(db.Model):
    __tablename__="book"
    id = db.Column(db.Integer(),primary_key = True)
    name = db.Column(db.String(),nullable = False)
    content = db.Column(db.String())

    authors = db.relationship('Author',secondary = 'book_author_rel',back_populate = 'book')

    likes = db.relationship('User',secondary='favorite',back_populate='book')

class Author(db.Model):
    __tablename__="author"
    id = db.Column(db.Integer(),primary_key = True)
    name = db.Column(db.String(),nullable = False)
    
    books = db.relationship('Book',secondary = 'book_author_rel',back_populate = 'author')

