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
        print("---------------------------------")
        print("in Student Dashboard")
        print("---------------------------------")
        user = User.query.filter_by(id = session["userID"]).first()
        books = Book.query.all()
        issueMsg = session.pop('issueMsg',None)
        deleteMsg = session.pop('deleteMsg',None)
        return render_template('student-dashboard.html', books=books,user = user,issueMsg=issueMsg,deleteMsg=deleteMsg)

@app.route("/user/librarian",methods = ["GET","POST"])
@login_required
@is_user("librarian")
def librarianDashboard():
    if request.method == "GET":
        user = User.query.filter_by(id = session["userID"]).first()
        books = Book.query.all()
        issueMsg = session.pop('issueMsg', None)
        deleteMsg = session.pop('deleteMsg', None)
        return render_template('librarian-dashboard.html',books=books, user = user,issueMsg=issueMsg,deleteMsg=deleteMsg,favourite=True)
    
@app.route("/add-book", methods=["GET","POST"])
@login_required
@is_user("librarian")
def addBook():
    user = User.query.filter_by(id = session["userID"]).first()
    if request.method == "GET":
        genresQuery = Genre.query.with_entities(Genre.name).all()
        allGenres = [name for (name,) in genresQuery]
        return render_template('addbook.html', user=user, genres=allGenres)
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
#@is_user("librarian")
def genreEdit():
    user = User.query.filter_by(id = session["userID"]).first()
    userType = session["userType"]
    if request.method == "GET":
        genresQuery = Genre.query.with_entities(Genre.name).all()
        allGenres = [name for (name,) in genresQuery]
        return render_template('genres.html', user=user, genres=allGenres,userType=userType)
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
                    genreError="Genre Already Exists!"

        elif(action == 'delete'):
            if(genreName == ""):
                genreError="Field Required!"
            else:
                genre = Genre.query.filter_by(name=genreName).first()
                if(not genre):
                    genreError="Genre Does Not Exists!"
                else:
                    books_genres = Book_Genre.query.filter_by(genre_id=genre.id).all()
                    genreSuccess=genreName+" deleted*"
                    db.session.delete(genre)
                    for book_genre in books_genres:
                        db.session.delete(book_genre)
                    db.session.commit()
            
        genresQuery = Genre.query.with_entities(Genre.name).all()
        allGenres = [name for (name,) in genresQuery]
        return render_template('genres.html', user=user, genreError=genreError,genreSuccess=genreSuccess,genres=allGenres,userType=userType)

@app.route("/author-editor",methods=["GET","POST"])
@login_required
#@is_user("librarian")
def authorEdit():
    user = User.query.filter_by(id = session["userID"]).first()
    userType = session["userType"]
    
    if request.method == "GET":
        authorQuery = Author.query.with_entities(Author.name).all()
        allAuthors = [name for (name,) in authorQuery]
        print(userType)
        return render_template('authors.html', user=user,authors=allAuthors, userType=userType)
    if request.method == "POST":
        authorError=""
        authorSuccess=""

        action = request.form.get("action")
        authorName = FixText(request.form.get("authorText")).title()
        if(action == "add"):
            if(authorName == ""):
                authorError="Field Required!"
            else:
                author = Author.query.filter_by(name=authorName).first()
                if(not author):
                    author = Author(name=authorName)
                    db.session.add(author)
                    db.session.commit()
                    authorSuccess=authorName+" added*"
                else:
                    authorError="Author Already Exists!"
        elif(action=="delete"):
            if(authorName==""):
                authorError="Field Required!"
            else:
                author = Author.query.filter_by(name=authorName).first()
                if(not author):
                    authorError = "Author Does Not Exists!"
                else:
                    books_authors = Book_Author.query.filter_by(author_id = author.id).all()
                    authorSuccess=authorName+" deleted*"
                    db.session.delete(author)
                    for book_author in books_authors:
                        db.session.delete(book_author)
                    db.session.commit()
        authorQuery = Author.query.with_entities(Author.name).all()
        allAuthors = [name for (name,) in authorQuery]
        return render_template('authors.html',user=user,authorError=authorError,authorSuccess=authorSuccess,authors=allAuthors, userType=userType)

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
    user = User.query.filter_by(id = session["userID"]).first()
    if request.method == "GET":
        book = Book.query.filter_by(id=bookID).first()
        authors = [author.name for author in Author.query.join(Book_Author).filter(Book_Author.book_id==book.id).all()]
        genres = [genre.name for genre in Genre.query.join(Book_Genre).filter(Book_Genre.book_id==book.id).all()]
        print(authors)
        print(genres)
        return render_template("book-page.html",user=user,userType=userType,authors=authors,genres=genres,book=book)

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
    if not genreEntry:
        session['deleteMsg'] = "Invalid Genre: "+ genre
        return redirect(url_for('librarianDashboard'))
    books_genres = Book_Genre.query.filter_by(genre_id=genreEntry.id).all()
    db.session.delete(genreEntry)
    for book_genre in books_genres:
        db.session.delete(book_genre)
    db.session.commit()
    return redirect(url_for('genreEdit'))

@app.route('/author-remove/<string:author>')
@login_required
@is_user("librarian")
def removeAuthor(author):
    authorEntry = Author.query.filter_by(name = author).first()
    if not authorEntry:
        session['deleteMsg'] = "Invalid Author: "+ author
        return redirect(url_for('librarianDashboard'))
    books_authors = Book_Author.query.filter_by(author_id=authorEntry.id).all()
    db.session.delete(authorEntry)
    for book_author in books_authors:
        db.session.delete(book_author)
    db.session.commit()
    return redirect(url_for('authorEdit'))

@app.route('/delete-book/<string:bookID>')
@login_required
@is_user("librarian")
def deleteBook(bookID):
    book = Book.query.filter_by(id=bookID).first()
    if not book:
        session['deleteMsg'] = "Invalid Book ID: "+ bookID
        return redirect(url_for('librarianDashboard'))
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
    book = Book.query.filter_by(id=bookID).first()
    if not book:
        session['deleteMsg'] = "Invalid Book ID: "+ bookID
        return redirect(url_for('librarianDashboard'))
    bookID = book.id
    userID = session["userID"]
    userType = session["userType"]
    issuePeriod = 7
    issue = Issue.query.filter(Issue.book_id==bookID,Issue.user_id==userID).order_by(desc(Issue.request_date)).first()
    #issue=None
    #if not(issues == []):
    #    issue = issues[-1]
    if userType == "librarian":
        if not issue:
            session['issueMsg'] = "Issued:-> " + book.name
            requestDate = db.func.datetime(db.func.current_timestamp(),'+5 Hours','+30 Minutes')
            issueDate = db.func.datetime(db.func.current_timestamp(),'+5 Hours','+30 Minutes')
            returnDate = db.func.datetime(db.func.current_timestamp(), '+7 Days','+5 Hours','+30 Minutes')
            issue = Issue(book_id=bookID,user_id=userID,request_date=requestDate,issue_date=issueDate,return_date=returnDate,issue_period=issuePeriod,status="issued")
            print("Issued")
            print(issue.book_id,issue.user_id,issue.request_date,issue.issue_date,issue.return_date,issue.issue_period,issue.status)
            db.session.add(issue)
            db.session.commit()
        else:
            session['deleteMsg'] = "Already Issued:-> " + book.name
        
        return redirect(url_for('librarianDashboard'))

    elif userType == "student":
        if not issue:
            session['issueMsg'] = "Requested:-> " + book.name
            requestDate = db.func.datetime(db.func.current_timestamp(),'+5 Hours','+30 Minutes')
            #issueDate = db.func.current_timestamp()
            #returnDate = db.func.datetime(db.func.current_timestamp(), '+7 Days')
            issue = Issue(book_id=bookID,user_id=userID,request_date=requestDate,issue_period=issuePeriod,status="requested")
            print("Requested")
            db.session.add(issue)
            db.session.commit()
        elif issue.status == "requested":
            session['issueMsg'] = "Already Requested:-> " + book.name
        else:
            session['deleteMsg'] = "Already Issued:-> " + book.name

        return redirect(url_for('studentDashboard'))
    #useless redirect should delete later
    return redirect(url_for('librarianDashboard'))

@app.route('/requests')
@login_required
#@is_user("librarian")
def requestsHandler():
    user = User.query.filter_by(id = session["userID"]).first()
    userType = session["userType"]
    if request.method == "GET":
        if userType == "librarian":
            issueRequests = Issue.query.all()
            allUsers = User.query.all()
            allBooks = Book.query.all()
            users = {}
            books = {}

            for user in allUsers:
                users[user.id] = user
            for book in allBooks:
                books[book.id] = book

            issueMsg = session.pop('issueMsg',None)
            deleteMsg = session.pop('deleteMsg',None)

            return render_template('issueHandler.html',user=user,issueRequests=issueRequests,users=users,books=books,issueMsg=issueMsg,deleteMsg=deleteMsg,userType=userType)
        elif userType == "student":
            issueRequests = Issue.query.filter_by(user_id=user.id).all()
            userBooks = Book.query.join(Issue,Book.id == Issue.book_id).filter(Issue.user_id==user.id).all()
            books = {}
            users = {}
            for book in userBooks:
                books[book.id] = book
            users[user.id] = user

            issueMsg = session.pop('issueMsg',None)
            deleteMsg = session.pop('deleteMsg',None)
            return render_template('issueHandler.html',user=user,issueRequests=issueRequests,users=users,books=books,issueMsg=issueMsg,deleteMsg=deleteMsg,userType=userType)


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
            return render_template('librarian-dashboard.html',books=books, user = user,issueMsg=issueMsg,deleteMsg=deleteMsg)
        else:
            return render_template('student-dashboard.html',books=books, user = user,issueMsg=issueMsg,deleteMsg=deleteMsg)

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
            return render_template('librarian-dashboard.html',books=books, user = user,issueMsg=issueMsg,deleteMsg=deleteMsg)
        else:
            return render_template('student-dashboard.html',books=books, user = user,issueMsg=issueMsg,deleteMsg=deleteMsg)

@app.route('/request-processor/<string:issueID>/<string:action>')
@login_required
#@is_user("librarian")
def requestProcessor(issueID,action):
    issue = Issue.query.filter_by(id=issueID).first()

    if not issue:
        session["deleteMsg"] = "Invalid issue ID!"
    else:
        if session["userType"] == "librarian":
            if issue.status == "requested":
                if action == "issue":
                    issueDate = db.func.datetime(db.func.current_timestamp(),'+5 Hours','+30 Minutes')
                    returnDate = db.func.datetime(db.func.current_timestamp(), '+7 Days','+5 Hours','+30 Minutes')
                    issue.issue_date = issueDate
                    issue.return_date= returnDate
                    issue.status = "issued"
                    db.session.commit()
                    session["issueMsg"] = "Successfully Issued*"
                elif action == "reject":
                    issue.status = "rejected"
                    db.session.commit()
                    session["issueMsg"] = "Rejected Request!"
                else:
                    session["deleteMsg"] = "Invalid Action for Requested!!!"
            elif issue.status == "issued":
                if action == "revoke":
                    issue.status = "revoked"
                    db.session.commit()
                    session["issueMsg"] = "Successfully Revoked Access*"
                elif action == "reissue":
                    issueDate = db.func.datetime(db.func.current_timestamp(),'+5 Hours','+30 Minutes')
                    returnDate = db.func.datetime(db.func.current_timestamp(), '+7 Days','+5 Hours','+30 Minutes')
                    issue.issue_date = issueDate
                    issue.return_date= returnDate
                    db.session.commit()
                    session["issueMsg"] = "Successfully Re-Issued*"
                else:
                    session["deleteMsg"] = "Invalid Action for Issued!!!"
            elif issue.status == "revoked":
                if action == "remove":
                    db.session.delete(issue)
                    db.session.commit()
                    session["deleteMsg"] = "Removed!!!"
                elif action == "reissue":
                    issueDate = db.func.datetime(db.func.current_timestamp(),'+5 Hours','+30 Minutes')
                    returnDate = db.func.datetime(db.func.current_timestamp(), '+7 Days','+5 Hours','+30 Minutes')
                    issue.issue_date = issueDate
                    issue.return_date= returnDate
                    issue.status = "issued"
                    db.session.commit()
                    session["issueMsg"] = "Successfully Re-Issued*"
                else:
                    session["deleteMsg"] = "Invalid Action for Revoked!!!"
            elif issue.status == "returned":
                if action == "reissue":
                    issueDate = db.func.datetime(db.func.current_timestamp(),'+5 Hours','+30 Minutes')
                    returnDate = db.func.datetime(db.func.current_timestamp(), '+7 Days','+5 Hours','+30 Minutes')
                    issue.issue_date = issueDate
                    issue.return_date= returnDate
                    issue.status = "issued"
                    print("reissued returned book")
                    db.session.commit()
                    session["issueMsg"] = "Successfully Re-Issued*"
                elif action == "remove":
                    db.session.delete(issue)
                    db.session.commit()
                    session["deleteMsg"] = "Removed!!!"
                else:
                    session["deleteMsg"] = "Invalid Action for Returned!!!"
            elif issue.status == "rejected":
                if action == "issue":
                    issueDate = db.func.datetime(db.func.current_timestamp(),'+5 Hours','+30 Minutes')
                    returnDate = db.func.datetime(db.func.current_timestamp(), '+7 Days','+5 Hours','+30 Minutes')
                    issue.issue_date = issueDate
                    issue.return_date= returnDate
                    issue.status = "issued"
                    print("reissued returned book")
                    db.session.commit()
                    session["issueMsg"] = "Successfully Re-Issued*"
                elif action == "remove":
                    db.session.delete(issue)
                    db.session.commit()
                    session["deleteMsg"] = "Removed!!!"
                else:
                    session["deleteMsg"] = "Invalid Action for Returned!!!"
        elif session["userType"] == "student":
            if issue.status == "requested":
                if action == "remove":
                    db.session.delete(issue)
                    db.session.commit()
                    session["deleteMsg"] = "Removed!!!"
                else:
                    session["deleteMsg"] = "Invalid Action for Returned!!!"
    return redirect(url_for('requestsHandler'))
    


if __name__ == "__main__":
    app.run(debug = True)


