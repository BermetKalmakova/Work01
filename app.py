import urllib2, json
from flask import Flask, request, render_template, redirect, url_for, session, flash
from os import urandom
from utils import database

app = Flask(__name__)
app.secret_key = urandom(32)

# LOGIN/LOGOUT STUFF

#helper method
#return true if a user is logged in
def checkSession():
    return "username" in session

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
    #if user is already logged in, redirect to welcome
    if checkSession():
        return redirect(url_for("welcome"))
    #if username exits, flash message and redirect to register
    postedUsername = request.form["username"]
    postedPassword = request.form["password"]
    if database.checkUsernames(postedUsername):
        flash("Username already taken.")
        return redirect(url_for("register"))
    if postedPassword == "":
    	flash("Password not entered.")
    	return redirect(url_for("register"))
    #othwerwise, create the account and redirect to root
    database.updateUsers(postedUsername, postedPassword)
    flash("Account succesfully created. Please login again.")
    return redirect(url_for("root"))
            
@app.route("/authorize", methods=["GET", "POST"])
def authorize():
    #if user is already logged in, redirect to welcome
    if checkSession():
        return redirect(url_for("welcome"))
    #check if the submitted login information is correct, and then store a session with the userId
    postedUsername = request.form["username"]
    postedPassword = request.form["password"]
    if database.checkUsernames(postedUsername):
        if database.authorize(postedUsername, postedPassword):
            session["username"] = postedUsername
            return redirect(url_for("welcome"))
    #if the submitted login information is not correct, redirect to welcome, flash a message
    flash("Incorrect username-password combination.")
    return redirect(url_for("root"))

@app.route("/logout", methods=["GET", "POST"])
def logout():
	#logs out user by popping username from session
	x = session["username"]
	session.pop("username")
	flash(x + " is now logged out.")
	return redirect(url_for("root"))

# END LOGIN/LOGOUT STUFF

@app.route("/welcome", methods=["GET", "POST"])
def welcome():
    return render_template("welcome.html", name=session["username"], score=database.getScore(session["username"])[0], place=getStringEnding(database.getPlacement(session["username"])))

def getStringEnding(place):
	place = place[0]
	end = place % 10
	if end == 1:
		return str(place) + "st"
	elif end == 2:
		return str(place) + "nd"
	elif end == 3:
		return str(place) + "rd"
	else:
		return str(place) + "th"

@app.route("/makegame", methods=["GET", "POST"])
def makegame():
    cat=request.form["cat"]
    diff=request.form["diff"]
    url = "https://opentdb.com/api.php?amount=10&category=" + cat + "&difficulty=" + diff + "&type=multiple"
    u = urllib2.urlopen(url)
    contents = u.read()
    d = json.loads(contents)
    return render_template("question.html")

''' WE NEED TO MAKE A QUESTION ROUTE ONCE API STUFF IS UP AND RUNNING!!! '''

@app.route("/leaderboard", methods=["GET", "POST"])
def leaderboard():
	listOfPeeps = database.getEverything()
	final = []
	boolean = True
	booli = False
	counter = 1
	while boolean:
		for i in listOfPeeps:
			if i[2] == counter:
				final.append(i)
				booli = True
		if not booli:
			boolean = False
		booli = False
		counter += 1
	return render_template("leaderboard.html", listy=final)

if __name__ == "__main__":
    app.debug = True
    app.run()
