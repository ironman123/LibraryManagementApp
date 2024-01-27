import re
from flask import render_template,redirect,url_for
from models import db,User
from werkzeug.security import generate_password_hash

key = "yolo"

def IsEmailValid(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    match = re.match(pattern,email)
    return match is not None

def RegisterUser(firstName, lastName, email, password, repassword, securityKey, type):
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
