import os
from flask import Flask,render_template,redirect,request,url_for,session,send_from_directory
from utility import IsEmailValid,RegisterUser,key,login_required,is_user,FixText,BookAdder
from models import *
from werkzeug.security import check_password_hash

app = Flask(__name__)

uploadFolder = os.path.join(os.getcwd(), 'books')
app.config["SECRET_KEY"] = key
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///models.db"
app.config['UPLOAD_FOLDER'] = uploadFolder

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/user/student",methods = ["GET","POST"])
@login_required
@is_user("student")
def studentDashboard():
    if request.method == "GET":
        user = User.query.filter_by(id = session["userID"]).first()
        return render_template('student-dashboard.html', user = user.firstname)

@app.route("/user/librarian",methods = ["GET","POST"])
@login_required
@is_user("librarian")
def librarianDashboard():
    if request.method == "GET":
        user = User.query.filter_by(id = session["userID"]).first()
        books = Book.query.all()
        issueMsg = session.pop('issueMsg', None)
        deleteMsg = session.pop('deleteMsg', None)
        return render_template('librarian-dashboard.html',books=books, user = user.firstname,issueMsg=issueMsg,deleteMsg=deleteMsg)
    
@app.route("/add-book", methods=["GET","POST"])
@login_required
@is_user("librarian")
def addBook():
    user = User.query.filter_by(id = session["userID"]).first()
    if request.method == "GET":
        genresQuery = Genre.query.with_entities(Genre.name).all()
        allGenres = [name for (name,) in genresQuery]
        return render_template('addbook.html', user=user.firstname, genres=allGenres)
    elif request.method == "POST":
        
        title = request.form.get("title")
        
        authors = request.form.get("authors")
        
        genres = request.form.get("genres")

        desc = request.form.get("desc")

        file = None

        if 'file' in request.files:
            file = request.files['file']
        else:
            file = None
        
        return BookAdder(app,title,authors,genres,desc,file)

    
@app.route("/genre-editor", methods=["GET","POST"])
@login_required
@is_user("librarian")
def genreEdit():
    user = User.query.filter_by(id = session["userID"]).first()
    
    if request.method == "GET":
        genresQuery = Genre.query.with_entities(Genre.name).all()
        allGenres = [name for (name,) in genresQuery]
        return render_template('genres.html', user=user.firstname, genres=allGenres)
    if request.method == "POST":
        genreError=""
        genreSuccess=""

        action = request.form.get("action")
        genreName = FixText(request.form.get("genreText")).title()
        if(action == "add"):
            if(genreName == ""):
                genreError="Field Required!"
            else:
                genre = Genre.query.filter_by(name=genreName).first()
                if(not genre):
                    genre = Genre(name=genreName)
                    db.session.add(genre)
                    db.session.commit()
                    genreSuccess=genreName+" added*"
                else:
                    genreError="Genre Already Exist!"

        elif(action == 'delete'):
            if(genreName == ""):
                genreError="Field Required!"
            else:
                genre = Genre.query.filter_by(name=genreName).first()
                if(not genre):
                    genreError="Genre Does Not Exist!"
                else:
                    books_genres = Book_Genre.query.filter_by(genre_id=genre.id).all()
                    genreSuccess=genreName+" deleted*"
                    db.session.delete(genre)
                    for book_genre in books_genres:
                        db.session.delete(book_genre)
                    db.session.commit()
            
        genresQuery = Genre.query.with_entities(Genre.name).all()
        allGenres = [name for (name,) in genresQuery]
        return render_template('genres.html', user=user.firstname, genreError=genreError,genreSuccess=genreSuccess,genres=allGenres)



@app.route("/", methods = ["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":

        if "userID" in session:
            session.clear()

        email = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(email = email).first()

        emailError = ""
        passwordError = ""

        if email == "":
            emailError = "Username is Required!"
        elif not IsEmailValid(email):
            emailError = "Invalid user email!"
        elif password == "":
            passwordError = "Password required!"
        elif not user or not check_password_hash(user.password,password):
            passwordError = "Invalid user email or password!"
        
        if emailError or passwordError:
            return render_template("index.html", user = email,userError = emailError,passwordError = passwordError)
        else:
            session["userID"] = user.id
            session["userType"] = user.type
            if session["userType"] == "student":
                return redirect(url_for('studentDashboard'))
            else:
                return redirect(url_for('librarianDashboard'))

@app.route("/register", methods = ["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        firstName = request.form.get("firstname")
        lastName = request.form.get("lastname")
        email = request.form.get("email")
        password = request.form.get("password")
        repassword = request.form.get("repassword")
        type="student"

        duplicate=False
        user = User.query.filter_by(email = email).first()
        if user:
            duplicate = True

        return RegisterUser(firstName=firstName,lastName=lastName,email=email,password=password,repassword=repassword,securityKey=None,type = type,duplicateEmail=duplicate)

@app.route("/librarian/register", methods = ["GET","POST"])
def librarianRegister():
    if request.method == "GET":
        return render_template("librarian-register.html")
    elif request.method == "POST":
        firstName = request.form.get("firstname")
        lastName = request.form.get("lastname")
        email = request.form.get("email")
        password = request.form.get("password")
        repassword = request.form.get("repassword")
        securityKey = request.form.get("securitykey")
        type="librarian"

        duplicate=False
        user = User.query.filter_by(email = email).first()
        if user:
            duplicate = True

        return RegisterUser(firstName=firstName,lastName=lastName,email=email,password=password,repassword=repassword,securityKey=securityKey,type = type,duplicateEmail=duplicate)

@login_required
@app.route('/book/<string:bookID>')
def book(bookID):
    userType = session["userType"]
    if request.method == "GET":
        book = Book.query.filter_by(id=bookID).first()
        authors = [author.name for author in Author.query.join(Book_Author).filter(Book_Author.book_id==book.id).all()]
        genres = [genre.name for genre in Genre.query.join(Book_Genre).filter(Book_Genre.book_id==book.id).all()]
        print(authors)
        print(genres)
        return render_template("book-page.html",userType=userType,authors=authors,genres=genres,book=book)

@app.route('/signout')
@login_required
def signout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/genre-remove/<string:genre>')
@login_required
@is_user("librarian")
def removeGenre(genre):
    genreEntry = Genre.query.filter_by(name = genre).first()
    books_genres = Book_Genre.query.filter_by(genre_id=genreEntry.id).all()
    db.session.delete(genreEntry)
    for book_genre in books_genres:
        db.session.delete(book_genre)
    db.session.commit()
    return redirect(url_for('genreEdit'))

@app.route('/delete-book/<string:bookID>')
@login_required
@is_user("librarian")
def deleteBook(bookID):
    book = Book.query.filter_by(id=bookID).first()
    bookID = book.id
    db.session.delete(book)
    
    genres = Book_Genre.query.filter_by(book_id=bookID).all()
    for genre in genres:
        db.session.delete(genre)
    
    authors = Book_Author.query.filter_by(book_id=bookID).all()
    for author in authors:
        db.session.delete(author)
    
    db.session.commit()
    
    session['deleteMsg'] = "Deleted:-> " + book.name

    return redirect(url_for('librarianDashboard'))

@app.route('/issue-book/<string:bookID>')
@login_required
def issueBook(bookID):
    #userType = session["userType"]
    book = Book.query.filter_by(id=bookID).first()
    bookID = book.id

    session['issueMsg'] = "Issued:-> " + book.name
    return redirect(url_for('librarianDashboard'))

@app.route('/genre/<string:genreName>')
@login_required
def genrePage(genreName):
    if request.method == "GET":
        genre = genreName.title()
        user = User.query.filter_by(id = session["userID"]).first()
        fetched = Genre.query.filter_by(name = genre).first()
        if (not fetched):
            session['deleteMsg'] = "Invalid Genre:-> " + genre
            return redirect(url_for('librarianDashboard'))
        genreID = fetched.id
        
        books = Book.query.join(Book_Genre).filter(Book_Genre.genre_id==genreID).all()
        issueMsg = session.pop('issueMsg', None)
        deleteMsg = session.pop('deleteMsg', None)
        
        if session['userType'] == "librarian":
            return render_template('librarian-dashboard.html',books=books, user = user.firstname,issueMsg=issueMsg,deleteMsg=deleteMsg)
        else:
            return render_template('student-dashboard.html',books=books, user = user.firstname,issueMsg=issueMsg,deleteMsg=deleteMsg)

@app.route('/author/<string:authorName>')
@login_required
def authorPage(authorName):
    if request.method == "GET":
        author = FixText(authorName).title()
        user = User.query.filter_by(id = session["userID"]).first()
        fetched = Author.query.filter_by(name = author).first()

        if (not fetched):
            session['deleteMsg'] = "Invalid Author:-> " + author
            return redirect(url_for('librarianDashboard'))
        authorID = fetched.id

        books = Book.query.join(Book_Author).filter(Book_Author.author_id==authorID).all()
        issueMsg = session.pop('issueMsg', None)
        deleteMsg = session.pop('deleteMsg', None)
        
        if session['userType'] == "librarian":
            return render_template('librarian-dashboard.html',books=books, user = user.firstname,issueMsg=issueMsg,deleteMsg=deleteMsg)
        else:
            return render_template('student-dashboard.html',books=books, user = user.firstname,issueMsg=issueMsg,deleteMsg=deleteMsg)

if __name__ == "__main__":
    app.run(debug = True)


