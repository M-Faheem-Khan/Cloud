import os
import json
from werkzeug import secure_filename # makes sure that all filenames are safe to use
from db_helper import DatabaseHelper # for database related functions
from flask import Flask, render_template, request, jsonify, redirect, make_response # server and other server related functions

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.getcwd() + "\\uploads\\"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# show the default login page
@app.route("/", methods=["GET"])
def login():
    # checking if the user has a token
    token = request.cookies.get("token")
    # if the token is not empty
    if token != None:
        # validate token
        if DatabaseHelper().validateToken(token):
            # if valid redirect to dashboard
            return make_response(redirect("http://localhost:5000/dashboard"))
        else:
            # show login page
            return render_template("login.html")        
    else:
        # show login page
        return render_template("login.html")

# validates users login credentials
@app.route("/login", methods=["POST", "GET"])
def validiate():
    # if the requset is POST
    if request.method == "POST":
        # getting email and password
        email = request.form["email"]
        password = request.form["password"]
        # if valid credentials return new token
        token = DatabaseHelper().validateCredentials(email, password)
        # if the token is issued
        if token:
            # redirect to dashboard
            resp = make_response(redirect("http://localhost:5000/dashboard"))
            resp.set_cookie('token', token)
            return resp
        elif token == None:
            # if no token is issed likely invalid credentials
            return make_response(redirect("http://localhost:5000/"))
    # if the method is not post redirect the user to home page
    else:
        return make_response(redirect("http://localhost:5000/"))

# Shows upload page
@app.route("/upload", methods=["GET"])
def uploadPage():
    # showing the upload page
    token = request.cookies.get("token")
    # add token / identity check
    if DatabaseHelper().validateToken(token):
        return render_template("upload.html")
    else:
        return make_response(redirect("http://localhost:5000/"))

@app.route('/file', methods = ['GET', 'POST'])
def upload_file():
    token = request.cookies.get("token")
    if request.method == 'POST':
        f = request.files['file']
        fname = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
        # adding filename to the list
        DatabaseHelper().addFileToList(fname, token)
        return 'file uploaded successfully'

# showing the dashboard page page
@app.route("/dashboard", methods=["GET"])
def dashboard():
    token = request.cookies.get("token")
    # add token / identity check
    if DatabaseHelper().validateToken(token):
        return render_template("dashboard.html")
    else:
        return make_response(redirect("http://localhost:5000/"))

# Logout the user by deleting the token
@app.route("/logout")
def logout():
    token = request.cookies.get("token")
    # token check
    if DatabaseHelper().validateToken(token):
        # if the users token is in the database then delete the user remove the user token from cookies and db
        DatabaseHelper().removeToken(token)
        resp = make_response(redirect("http://localhost:5000/"))
        resp.set_cookie('token', '', expires=0)
        return resp
    else:
        return make_response(redirect("http://localhost:5000/"))

# gets all the files for a given user
@app.route("/fetchFiles/<token>")
def token(token):
    # token check
    if DatabaseHelper().validateToken(token):
        data = json.loads(DatabaseHelper().fetchAllFiles(token))
    else:
        return ""

# show insights page
@app.route("/insights")
def insights():
    token = request.cookies.get("token")
    # token check
    if DatabaseHelper().validateToken(token):
        return render_template("insights.html")
    else:
        return make_response(redirect("http://localhost:5000/"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", debug=True)