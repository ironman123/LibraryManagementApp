from flask import Flask,render_template,redirect,request,url_for,session
from utility import IsEmailValid

app = Flask(__name__)

app.config["SECRET_KEY"] = "yolo"

@app.route("/", methods = ["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        user = request.form
        session["user"] = user
        return user

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

        fNameError = ""
        emailError = ""
        passwordError = ""
        rePasswordError = ""

        if firstName == "":
            fNameError = "First Name is Required!"
        if email == "":
            emailError = "Email is Required!"
        elif not IsEmailValid(email):
            emailError = "Enter a valid email!"
        if password == "":
            passwordError = "Password is required!"
        if repassword != password:
            rePasswordError = "Password doesn't match!"

        if fNameError or emailError or passwordError or rePasswordError:
            return render_template("Register.html", 
                                   firstname = firstName,
                                   lastname = lastName,
                                   email = email,
                                   password = password,
                                   repassword = repassword,
                                   fNameError = fNameError,
                                   emailError = emailError,
                                   passwordError = passwordError,
                                   rePasswordError = rePasswordError)
        else:
            return request.form

if __name__ == "__main__":
    app.run(debug = True)