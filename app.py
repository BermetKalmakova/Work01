import requests, json
from flask import Flask, request, render_template, redirect, url_for, session
from os import urandom
from utils import database

app = Flask(__name__)
app.secret_key = urandom(32)

# LOGIN STUFF

#helper method
#return true if a user is logged in
def checkSession():
    return "userID" in session

@app.route("/", methods=["GET", "POST"])
def root():
    #if user is already logged in, redirect to welcome
    if checkSession():
        return redirect(url_for("welcome"))
    #otherwise return the template for login
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
	#if user is already logged in, redirect to welcome
    if checkSession():
        return redirect(url_for("welcome"))
    #otherwise return the template for register
    return render_template("register.html")

@app.route("/createAccount", methods=["GET", "POST"])
def createAccount():
    #if user is already logged in, redirect to Welcome
    if checkSession():
        return redirect(url_for("welcome"))
    #if username exits, flash message and redirect to Register
    postedUsername = request.form["username"]
    postedPassword = request.form["password"]
    if database.checkUsernames(postedUsername):
        flash("Username already taken.")
        return redirect(url_for("register"))
    if postedPassword == "":
    	flash("Password not entered.")
    	return redirect(url_for("register"))
    #othwerwise, create the account and redirect to Root
    database.updateUsers(postedUsername, postedPassword)
    flash("Account succesfully created. Please login again.")
    return redirect(url_for("root"))
            
@app.route("/authorize", methods=["GET", "POST"])
def authorize():
    #if user is already logged in, redirect to Welcome
    if checkSession():
        return redirect(url_for("welcome"))
    #check if the submitted login information is correct, and then store a session with the userId
    postedUsername = request.form["username"]
    postedPassword = request.form["password"]
    if database.checkUsernames(postedUsername):
        if database.authorize(postedUsername, postedPassword):
            session["userID"] = database.getUserID(postedUsername)
            session["username"] = postedUsername
            return redirect(url_for("welcome"))
    #if the submitted login information is not correct, redirect to Welcome, flash a message
    flash("Incorrect username-password combination.")
    return redirect(url_for("root"))

# END LOGIN STUFF

@app.route("/welcome", methods=["GET", "POST"])
def welcome():
	return render_template("welcome.html")

if __name__ == "__main__":
    app.debug = True
    app.run()