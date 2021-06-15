from flask import Flask, render_template, request, url_for, redirect, session
import pymongo
import bcrypt


app=Flask(__name__)
app.secret_key='testing'

client = pymongo.MongoClient("mongodb+srv://user:user@cluster0.e09md.mongodb.net/prafullaproject?retryWrites=true&w=majority")
if client:
    print("connected")

else: 
    print("not connected")
db = client.get_database('prafullaproject')

newscollection = db.newscollection
records = db.records

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/contactus')
def contactus():
    return render_template('contactus.html')

@app.route('/news', methods=["GET","POST"])
def news():
    return render_template('news.html',classes=list(newscollection.find()))

@app.route('/login', methods=["POST", "GET"])
def login():
    message = 'Please login to your account'


    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")


        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']

            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                session["usertype"] = email_found['usertype']
                return redirect(url_for('logged_in'))
            else:

                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)

@app.route('/logged_in')
def logged_in():
    if "email" in session:
        email = session["email"]
        usertype=session['usertype']
        return render_template('logged_in.html', email=email,usertype=usertype)
    else:
        return redirect(url_for("login"))

@app.route('/logout')
def logout():
    if "email" in session:
        session.clear()
        return render_template("signout.html")
    else:
        return render_template('home.html')

@app.route('/register', methods=['post', 'get'])
def register():
    message = ''
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        usertype=request.form.get("usertype")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('index.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('index.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('index.html', message=message)
        else:

            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())

            user_input = {'name': user, 'email': email, 'password': hashed, 'usertype':usertype}

            records.insert_one(user_input)
            

            user_data = records.find_one({"email": email})
            new_email = user_data['email']

            return render_template('registered.html', email=new_email)
    return render_template('register.html')

@app.route('/addnews', methods=["POST", "GET"])
def addnews():
    message = ''
    if request.method == "POST":
        headline = request.form.get("headline")
        Description = request.form.get("Description")
        Authorname=request.form.get("Authorname")
        newscategory = request.form.get("newscategory")

        user_input = {'headline': headline, 'Description': Description, 'Authorname': Authorname, 'newscategory':newscategory}
        newscollection.insert_one(user_input)
        message='news entered succesfully'
        return render_template('addnews.html', message=message)
    return render_template('addnews.html')
