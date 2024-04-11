import re,os
from flask import render_template,redirect,url_for,session
from models import *
from werkzeug.security import generate_password_hash
from functools import wraps
import fitz

key = "yolo"

def login_required(f):
    @wraps(f)
    def wrapper(*args,**kwargs):
        if "userID" in session:
            return f(*args,**kwargs)
        else:
            return redirect(url_for('index'))
    return wrapper

def is_user(expectedType):
    def decorator(f):
        @wraps(f)
        def wrapper(*args,**kwargs):
            if "userID" in session:
                if session["userType"] == expectedType:
                    return f(*args,**kwargs)
            return redirect(url_for('index'))
        return wrapper
    return decorator

def return_books():
    userID = session.get("userID")
    if userID:
        issues = Issue.query.filter_by(user_id=userID).all()
        current_time = datetime.now() + timedelta(hours=5, minutes=30)
        for issue in issues:
            if issue.return_date == None:
                continue
            if issue.return_date < current_time:
                issue.status = "returned"
        db.session.commit()

def FixText(str):
    if str == "":
        return ""
    return re.sub(' +',' ',str)

def IsEmailValid(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    match = re.match(pattern,email)
    return match is not None

def RegisterUser(firstName, lastName, email, password, repassword, securityKey, type, duplicateEmail):
    fNameError = ""
    emailError = ""
    passwordError = ""
    rePasswordError = ""
    securityKeyError = ""


    if firstName == "":
        fNameError = "First Name is required!"
    if email == "":
        emailError = "Email is Required!"
    elif not IsEmailValid(email):
        emailError = "Enter a valid email!"
    elif duplicateEmail:
        emailError = "Username not available!"
    if password == "":
        passwordError = "Password is required!"
    if repassword != password:
        rePasswordError = "Password doesn't match!"
    if type == "librarian":
        if securityKey == "":
            securityKeyError = "Security Key required!"
        elif securityKey != key:
            securityKeyError = "Invalid Security Key!"

    if fNameError or emailError or passwordError or rePasswordError or securityKeyError:
        if type == "student":
            return render_template("register.html", 
                                firstname=firstName,
                                lastname=lastName,
                                email=email,
                                password=password,
                                repassword=repassword,
                                fNameError=fNameError,
                                emailError=emailError,
                                passwordError=passwordError,
                                rePasswordError=rePasswordError)
        elif type == "librarian":
            return render_template("librarian-register.html",
                                    userType = type,
                                    firstname=firstName,
                                    lastname=lastName,
                                    email=email,
                                    password=password,
                                    repassword=repassword,
                                    fNameError=fNameError,
                                    emailError=emailError,
                                    passwordError=passwordError,
                                    rePasswordError=rePasswordError,
                                    securityKeyError=securityKeyError)

    if lastName == "":
        lastName = None
    user = User(firstname=firstName, 
                lastname=lastName, 
                email=email,
                password=generate_password_hash(password),
                type=type)
    
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('index'))


def BookAdder(app,title,authors,genres,desc,file):
    genresQuery = Genre.query.with_entities(Genre.name).all()
    allGenres = [name for (name,) in genresQuery]
    authorsQuery = Author.query.with_entities(Author.name).all()
    allAuthors = [name for (name,) in authorsQuery]
    
    titleError=""
    authorsError=""
    fileError=""
    genreError=""
    descError=""

    if(title == ""):
            titleError="Title can not be empty!"
    else:
        title = FixText(title).title()
        book = Book.query.filter_by(name=title).first()
        if book:
            titleError="Title already exists!"



    if(authors == ""):
            authorsError="Authors field can not be empty!"
    else:
        authors = [author.strip() for author in FixText(authors).title().split(sep=",")]
        
        if titleError == "Title already exists!":
            bookID = (Book.query.filter_by(name=title).first()).id
            bookAuthors = [author.name for author in Author.query.join(Book_Author).filter(Book_Author.book_id==bookID).all()]
            newAuthors = [author for author in authors if author not in bookAuthors]
            print(newAuthors)
            print(bookAuthors)
            if not newAuthors:
                authorsError="No new Authors to add!"
                print(authorsError)
            else:
                addAuthors = [author for author in newAuthors if author not in allAuthors]
                print(addAuthors)
                if not (addAuthors==[]):
                    print("Adding new authors to DB")
                    
                    for author in addAuthors:
                        a = Author(name=author.strip())
                        db.session.add(a)
                    db.session.commit()
                newAuths=[]
                for author in newAuthors:
                    authorID = Author.query.filter_by(name=author).first().id
                    print(bookID)
                    print(authorID)
                    newAuths.append(author)
                    entry = Book_Author(book_id=bookID,author_id=authorID)
                    db.session.add(entry)
                db.session.commit()
                authorsError=', '.join(newAuths)
                authorsError+= " added for this book!"
        else:
            addAuthors = [author for author in authors if author not in allAuthors]
            if not (addAuthors == []):
                for author in addAuthors:
                    a = Author(name=author)
                    db.session.add(a)
                db.session.commit()
            
            #for author in authors:
            #    a = Book_Author(bookID,Author.query.filter_by(name=a).first().id)
            #    db.session.add(a)
            #db.session.commit()
                

    
    if genres == "":
            genreError="This field can not be empty!"
    else:
        genres = [genre.strip() for genre in genres.split(sep=",")]
        for g in genres:
            if g not in allGenres:
                genreError += g + " not a valid genre! "
    

    if desc == "":
        descError = "A small description is required!"


    if file.filename == "":
        fileError="No file Selected!"
    
    if not(fileError or descError or authorsError or genreError or titleError):
        extension='.pdf'
        filePath=os.path.join(app.config['UPLOAD_FOLDER'], title)
        file.save(filePath+extension)
        
        book = fitz.open(filePath+extension)
        cover = fitz.Pixmap(book, book[0].get_images()[0][0])

        if cover.n - cover.alpha > 3:
            cover = fitz.Pixmap(fitz.csRGB,cover)

        #coverPath = os.path.splitext(filePath+extension)[0] + '.png'
        coverPath = os.path.join(app.static_folder,'cover-images', os.path.basename(filePath)+'.png')
        print(coverPath)
        cover._writeIMG(coverPath,format_="png",jpg_quality=None)
        
        cover=None
        book.close()
        
        print("READ FILE!!!")

        book=Book(name=title,content="",description=desc)
        db.session.add(book)
        db.session.commit()
        bookID = Book.query.filter_by(name=title).first().id

        for author in authors:
            authorID = Author.query.filter_by(name=author).first().id
            db.session.add(Book_Author(book_id=bookID,author_id=authorID))
        db.session.commit()
        for genre in genres:
            g = Book_Genre(book_id=bookID,genre_id=Genre.query.filter_by(name=genre).first().id)
            db.session.add(g)
        db.session.commit()
        return redirect(url_for('librarianDashboard'))

    user = User.query.filter_by(id = session['userID'])
    return render_template('addbook.html',title=title,authors=', '.join(authors),genres=allGenres,activeGenres=genres,genreText=', '.join(genres),desc=desc,titleError=titleError,authorsError=authorsError,fileError=fileError,genreError=genreError,descError=descError,user=user)