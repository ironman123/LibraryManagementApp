from flask import Flask,render_template,redirect,request,url_for,session
from utility import IsEmailValid
from models import db,User
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)

app.config["SECRET_KEY"] = "yolo"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///models.db"

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/", methods = ["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
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
        elif not user or check_password_hash(user.password,password):
            passwordError = "Invalid user email or password!"
        
        if emailError or passwordError:
            return render_template("index.html", user = email,userError = emailError,passwordError = passwordError)
        else:
            session["user"] = email
            return str(email + password)

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
            if lastName == "":
                lastName = None
            user = User(firstname = firstName, 
                        lastname = lastName, 
                        email = email,
                        password = generate_password_hash(password),
                        type = "student")
            db.session.add(user)
            db.session.commit()

            return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug = True)