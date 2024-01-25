from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Favorite(db.Model):
    __tablename__ = "favorite"
    id = db.Column(db.Integer(),primary_key= True)
    book_id = db.Column(db.Integer(),db.ForeignKey('book.id'),nullable=False)
    user_id = db.Column(db.Integer(),db.ForeignKey('user.id'),nullable=False)

class Book_Author(db.Model):
    __tablename__ = "book_author"
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

    favorites = db.relationship('Book',secondary='favorite',backref='likers')

    issues = db.relationship('Book',secondary='issue',backref='issued_by')

class Book(db.Model):
    __tablename__="book"
    id = db.Column(db.Integer(),primary_key = True)
    name = db.Column(db.String(),nullable = False)
    content = db.Column(db.String())

    #authors = db.relationship('Author',secondary = 'book_author_rel',backref = 'books')

    #likers = db.relationship('User',secondary='favorite',backref='favourites')

    #issued_by = db.relationship('User',secondary='issue',backref='issues')



class Author(db.Model):
    __tablename__="author"
    id = db.Column(db.Integer(),primary_key = True)
    name = db.Column(db.String(),nullable = False)
    
    books = db.relationship('Book',secondary = 'book_author_rel',backref = 'authors')

class Issue(db.Model):
    __tablname__="issue"
    id = db.Column(db.Integer(),primary_key = True)
    book_id = db.Column(db.Integer(),db.ForeignKey('book.id'),nullable=False)
    user_id = db.Column(db.Integer(),db.ForeignKey('user.id'),nullable=False)
    request_date = db.Column(db.DateTime(),nullable = False, default = db.func.current_timestamp())
    issue_date = db.Column(db.DateTime(),nullable = True)
    return_date = db.Column(db.DateTime(),nullable = True)
    issue_period = db.Column(db.Integer(),nullable = True)
    status = db.Column(db.String(),nullable = False,default = 'requested')

