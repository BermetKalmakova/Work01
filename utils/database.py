import sqlite3   #enable control of an sqlite database

def openDatabase():
    f="data/users.db"
    db = sqlite3.connect(f) #open if f exists, otherwise create
    return db, db.cursor()    #facilitate db ops

def closeDatabase(db):
    db.commit() #save changes
    db.close()  #close database

# LOGIN FUNCTIONS!!!

def checkUsernames(username):
    #checks if username is taken
    #called when user registers onto our site
    #returns True if username is taken, returns False if username is not taken
    db, c = openDatabase()
    cm = "SELECT username FROM peeps;"
    for i in c.execute(cm):
        if username == i[0].encode("ascii"):
            closeDatabase(db)
            return True
    closeDatabase(db)
    return False

def updateUsers(username, password): 
    #adds a new record in the userInfo table with the username, password, and a userID (found in function)
    #called when user registers onto our site
    db, c = openDatabase()
    cm = "SELECT COUNT(*) FROM peeps;"
    for i in c.execute(cm):
        placement = i[0]
    cm = 'INSERT INTO peeps VALUES("%s", "%s", %d, %d);' %(username, password, 0, placement + 1)
    c.execute(cm)
    closeDatabase(db)

def authorize(username, password):
    #checks whether a person's password matches their username
    #called by authorize() in app.py
    db, c = openDatabase()
    cm = 'SELECT password FROM peeps WHERE username = "%s";' %username
    x = c.execute(cm)
    for i in x:
        true_pass = i
    closeDatabase(db)
    return password == true_pass[0].encode("ascii")

# END LOGIN FUNCTIONS



# START ALL OUR GET FUNCTIONS

def getScore(username):
    db, c = openDatabase()
    cm = 'SELECT score FROM peeps WHERE username = "%s";' %username
    x = c.execute(cm)
    for i in x:
        score = i
    closeDatabase(db)
    return score

def getPlacement(username):
    db, c = openDatabase()
    cm = 'SELECT placement FROM peeps WHERE username = "%s";' %username
    x = c.execute(cm)
    for i in x:
        place = i
    closeDatabase(db)
    return place

def getEverything():
    db, c = openDatabase()
    cm = 'SELECT username, score, placement FROM peeps;'
    final = []
    x = c.execute(cm)
    for i in x:
        final.append(i)
    closeDatabase(db)
    return final

# END ALL OUR GET FUNCTIONS



# START ALL OUR SET FUNCTIONS

def setScore(user, score):
    db, c = openDatabase()
    cm = 'UPDATE peeps SET score = %d WHERE username = "%s";' %(score, user)
    c.execute(cm)
    closeDatabase(db)

def changePlacements():
    db, c = openDatabase()
    cm = 'SELECT score FROM peeps;'
    x = c.execute(cm)
    scores = []
    for i in x:
        scores.append(i)
    scores.sort()
    place = 1
    cm = "SELECT COUNT(*) FROM peeps;"
    for i in c.execute(cm):
        total = i[0]
    while place <= total:
        cm = 'UPDATE peeps SET placement = %d WHERE score = %d' %(place, score)
        place += 1
    closeDatabase(db)

# END ALL OUR SET FUNCTIONS