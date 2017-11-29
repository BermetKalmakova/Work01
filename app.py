import urllib2, json
from flask import Flask, request, render_template, redirect, url_for, session, flash
from os import urandom
from utils import database
from random import shuffle

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
            session["username"] = postedUsername
            return redirect(url_for("welcome"))
    #if the submitted login information is not correct, redirect to Welcome, flash a message
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

diff = ''

@app.route("/makegame", methods=["GET", "POST"])
def makegame():
    cat = request.form["cat"]
    diff = request.form["diff"]
    url = "https://opentdb.com/api.php?amount=10&category=" + cat + "&difficulty=" + diff + "&type=multiple"
    u = urllib2.urlopen(url)
    contents = u.read()
    d = json.loads(contents)['results'] #questions and answers
    session["d"] = d
    session["number"] = 0
    session["diff"] = diff
    return redirect(url_for("question"))

@app.route("/question", methods=["GET","POST"])
def question():
    q = ''
    i_a = ['']
    all_a = []
    n = session["number"]
    d = session["d"]
    #try:
    #    request.form['answer']
    #except:
    #    pass
    #if request.form['answer'] == c_a:
    #    flash("Correct answer!")
    #if request.form['answer'] != c_a:
        #flash(wikimedia stuff)
    while (n < 10):
        q = d[n]['question']
        c_a = d[n]['correct_answer']
        session["correct"] = c_a
        print c_a
        i_a = d[n]['incorrect_answers']
        i_a.append(c_a)
        shuffle(i_a)
        a = i_a[0]
        b = i_a[1]
        c = i_a[2]
        d = i_a[3]
        print [a, b, c, d]
        session["number"] += 1
        return render_template("question.html", question = q, a = a,b=b,c=c,d=d)
    return redirect(url_for("root"))

@app.route("/answered", methods=["GET","POST"])
def answered():
    wiki_search_url = 'https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch=' + session["correct"].replace(' ', '%20')
    wiki_u = urllib2.urlopen(wiki_search_url)
    wiki_contents = wiki_u.read()
    title = json.loads(wiki_contents)['query']['search'][0]['title'] #retrieves first title for use in next part
    pageid = json.loads(wiki_contents)['query']['search'][0]['pageid'] #retrieves pageid for use in next part
    new_wiki_search_url = 'https://en.wikipedia.org/w/api.php?action=query&prop=extracts&format=json&exintro=&titles=' + title.replace(' ', '%20')
    new_wiki_u = urllib2.urlopen(new_wiki_search_url)
    new_wiki_contents = new_wiki_u.read()
    extract = json.loads(new_wiki_contents)['query']['pages'][str(pageid)]['extract']
    m = extract
    print request.form['answer']
    if request.form['answer'] == session["correct"]:
        m = "Correct answer!"
        if session["diff"] == "easy":
            database.setScore(session["username"], database.getScore(session["username"])[0] + 1)
        elif session["diff"] == "medium":
            database.setScore(session["username"], database.getScore(session["username"])[0] + 3)
        else:
            database.setScore(session["username"], database.getScore(session["username"])[0] + 5)
    flash(m)
    return redirect(url_for("question"))

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
