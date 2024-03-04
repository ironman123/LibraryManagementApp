from flask import Flask,render_template,redirect,request,url_for,session
from utility import IsEmailValid,RegisterUser,key,login_required,is_user
from models import db,User
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)

app.config["SECRET_KEY"] = key
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///models.db"

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
        return render_template('librarian-dashboard.html', user = user.firstname)
    
#@app.route("/book-editor", methods=["GET","POST"])
#@login_required
#@is_user("librarian")
#def bookEditor():
#    if request.method == "GET":



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
    
@app.route('/signout')
@login_required
def signout():
    session.clear()
    return redirect(url_for('index'))
    


if __name__ == "__main__":
    app.run(debug = True)