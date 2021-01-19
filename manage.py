import sqlite3
from random import choice
import random
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading

hostname = "http://localhost:5000"

def createRoom():
    conn = sqlite3.connect('data')
    c = conn.cursor()
    tablelist = []
    sqlquerry = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for name in sqlquerry:
        if name[0] != "managerdb":
            tablelist.append(int(name[0][1:]))

    newid = choice([i for i in range(1000, 9999) if i not in tablelist])

    try:
        sqlquerry = f'CREATE TABLE t{str(newid)} (name, email, useridentificator, wishlist)'
        c.execute(sqlquerry)
        sqlquerry = f'INSERT INTO managerdb VALUES ("t{str(newid)}", "false")'
        c.execute(sqlquerry)
        conn.commit()
        return newid
    except:
        return "Can't make a room id"

def draw(roomid):
    conn = sqlite3.connect('data')
    c = conn.cursor()

    sqlquerry = f'SELECT * FROM t{roomid}'
    c.execute(sqlquerry)

    namelist = []
    emailslist = []

    for row in c.fetchall():
        namelist.append(row[0])
        emailslist.append(row[1])

    zippedlist=list(zip(namelist,emailslist))
    random.shuffle(zippedlist)
    shuffled_namelist,shuffled_emaillist =zip(*zippedlist)
    shuffled_emaillist_reversed=tuple(reversed(shuffled_emaillist))

    for idd, name in enumerate(namelist):
        sendTo("draw", name, str(roomid), shuffled_emaillist_reversed[idd])


def stateOfRoom(namelistlen, drawstate):
    if namelistlen % 2 != 0:
        StateOfDraw = "disabled"
        AttributeDraw = "disabled"
        AttributeAdd = ""
        DrawError = "You need to be an even number of participants"
    elif namelistlen == 0:
        StateOfDraw = "disabled"
        AttributeDraw = "disabled"
        AttributeAdd = ""
        DrawError = "You can't draw with 0 participants"
    elif drawstate == "true":
        StateOfDraw = "disabled"
        AttributeDraw = "disabled"
        AttributeAdd = "disabled"
        DrawError = "You can't draw again. The gifts were sent."
    else:
        StateOfDraw = ""
        AttributeDraw = ""
        AttributeAdd = ""
        DrawError = ""
    return StateOfDraw, AttributeDraw, AttributeAdd, DrawError

def sendTo(email_type, email_var1, email_var2, receiver_email):
    thread = threading.Thread(target=sendToThread, args=(email_type, email_var1, email_var2, receiver_email))
    thread.start()
    return

def sendToThread(email_type, email_var1, email_var2, receiver_email):
    credentials = [line.rstrip('\n') for line in open("credentials.dat")]
    sender_email = credentials[0]
    password = credentials[1]

    message = MIMEMultipart("alternative")

    if email_type == "wishlist":
        message["Subject"] = "Don't you want a cup for secret santa?"
        linkemail_var1 = f'<a target="_blank" href="{hostname}/wishlist?id={email_var2}&identificator={email_var1}" style>HERE!</a>'
        html_email = buildEmail("Edit your wishlist", linkemail_var1, "Room id is: ", email_var2)
    elif email_type == "draw":
        message["Subject"] = "OMG! Who is the lucky one?"
        linkemail_var2 = f'<a target="_blank" href="{hostname}/wishlist?id={email_var2}&name={email_var1}" style>Click to see what {email_var1} wants</a>'
        html_email = buildEmail("You will give your gift to: ", email_var1, "", linkemail_var2)
    else:
        return

    message["From"] = sender_email
    message["To"] = receiver_email

    part2 = MIMEText(html_email, "html")
    message.attach(part2)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )

def buildEmail(email_insidetext1, email_var1, email_insidetext2, email_var2):
    file = open('templates/emailTemplate.html', mode='r')
    html = file.read()\
        .replace("emailvariable1", email_var1)\
        .replace("emailinsidetext1", email_insidetext1)\
        .replace("emailvariable2", email_var2)\
        .replace("emailinsidetext2", email_insidetext2)
    file.close()
    return html

