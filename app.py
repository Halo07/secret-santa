import random
import sqlite3
import string
from flask import Flask, render_template, request, url_for, redirect
from manage import createRoom, draw, stateOfRoom, sendTo

app = Flask(__name__)
app.secret_key = 'secretdiscretneiubimcumvezinumaiinfilme'
hostname = "http://localhost:5000"

# --host=0.0.0.0 --port=80

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form['action'] == "1":
            newroomid = createRoom()
            if newroomid == "Can\'t make a room id":
                return render_template('index.html', error="Can\'t make a room id")
            else:
                return redirect(url_for('room', id=newroomid))
        elif request.form['action'] == "2":
            if request.form['action'] == "":
                return render_template('index.html', error="Room id can\'t be empty")
            else:
                goid = request.form['goid']
                return redirect(url_for('room', id=goid))
    return render_template('index.html')


@app.route('/room', methods=['GET', 'POST'])
def room():
    try:
        roomid = int(request.args.get('id'))
    except:
        return "Invalid room id"
    namelist = []
    drawstate = ""
    conn = sqlite3.connect('data')
    c = conn.cursor()


    sqlquerry = f'SELECT name FROM t{roomid}'
    c.execute(sqlquerry)
    for row in c.fetchall():
        namelist.append([row[0]])

    sqlquerry = f'SELECT roomdraw FROM managerdb WHERE roomid = "t{roomid}"'
    c.execute(sqlquerry)
    for row in c.fetchall():
        drawstate = row[0]

    StateOfDraw, AttributeDraw, AttributeAdd, DrawError = stateOfRoom(len(namelist), drawstate)

    if request.method == 'POST':
        if request.form['action'] == '1':
            name = request.form['name']
            email = request.form['email']
            if name == "":
                return render_template('room.html', useradderror="Enter your name! EX: Barack Obama", type="text-danger",
                                       datatable=namelist, stateofdraw=StateOfDraw, drawerror=DrawError, attributedraw=AttributeDraw,
                                       attributeadd = AttributeAdd)
            else:
                if '@' not in email:
                    return render_template('room.html', useradderror="Bad email adress! EX: obama@gmail.com", type="text-danger",
                                           datatable=namelist, stateofdraw=StateOfDraw, drawerror=DrawError, attributedraw=AttributeDraw,
                                           attributeadd = AttributeAdd)
                else:
                    emailexist = ""
                    nameexist = ""
                    sqlquerry = f'SELECT * FROM t{roomid} WHERE email = "{email}" OR name = "{name}"'
                    c.execute(sqlquerry)
                    for row in c.fetchall():
                        nameexist = row[0]
                        emailexist = row[1]
                    if emailexist != "" and nameexist != "":
                        return render_template('room.html', useradderror="This name/email is already on the list!", type="text-danger",
                                               datatable=namelist, stateofdraw=StateOfDraw, drawerror=DrawError, attributedraw=AttributeDraw,
                                               attributeadd = AttributeAdd)
                    else:
                        useruniqueid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=25))
                        sqlquerry = f'INSERT INTO t{roomid} VALUES ("{name}","{email}", "{useruniqueid}", "")'
                        sendTo("wishlist", useruniqueid, str(roomid), email)
                        c.execute(sqlquerry)
                        conn.commit()
                        namelist.append([name])
                        StateOfDraw, AttributeDraw, AttributeAdd, DrawError = stateOfRoom(len(namelist), drawstate)

                        return render_template('room.html',
                                               useradderror=f"You are done, {name}! Check your email to edit your wishlist (Unless you want a cup)",
                                               type="text-success", datatable=namelist, stateofdraw=StateOfDraw, drawerror=DrawError,
                                               attributedraw=AttributeDraw, attributeadd = AttributeAdd)

        elif request.form['action'] == '2':
            draw(roomid)
            sqlquerry = f'UPDATE managerdb SET roomdraw = "true" WHERE roomid = "t{roomid}"'
            c.execute(sqlquerry)
            conn.commit()
            drawstate = "true"
            StateOfDraw, AttributeDraw, AttributeAdd, DrawError = stateOfRoom(len(namelist), drawstate)
            return render_template('room.html', useradderror="", datatable=namelist, stateofdraw=StateOfDraw, drawerror=DrawError,
                                   attributedraw=AttributeDraw, attributeadd = AttributeAdd)

    return render_template('room.html', useradderror="", datatable=namelist, stateofdraw=StateOfDraw, drawerror=DrawError,
                           attributedraw=AttributeDraw, attributeadd = AttributeAdd)


@app.route('/wishlist', methods=['GET', 'POST'])
def wishlist():
    conn = sqlite3.connect('data')
    c = conn.cursor()
    wishlisfromdb = ""

    try:
        roomid = int(request.args.get('id'))
        userid = str(request.args.get('identificator'))
        nameid = str(request.args.get('name'))
        namecheck = ""
        indentificationcheck = ""

        sqlquerry = f'SELECT name FROM t{roomid} WHERE useridentificator = "{userid}"'
        c.execute(sqlquerry)
        for row in c.fetchall():
            indentificationcheck = row[0]

        sqlquerry = f'SELECT name FROM t{roomid} WHERE name = "{nameid}"'
        c.execute(sqlquerry)
        for row in c.fetchall():
            namecheck = row[0]

        if namecheck == "" and indentificationcheck == "":
            return "Invalid args"
        elif indentificationcheck != "" and namecheck == "":
            editstate = ""
            wishlistname = indentificationcheck
        elif indentificationcheck == "" and namecheck != "":
            editstate = "disabled"
            wishlistname = namecheck
        else:
            return "Invalid args"
    except:
        return "Invalid args"


    sqlquerry = f'SELECT wishlist FROM t{roomid} WHERE name = "{wishlistname}"'
    c.execute(sqlquerry)
    for row in c.fetchall():
        wishlisfromdb = row[0]

    if request.method == 'POST' and indentificationcheck != "":
        if request.form['action'] == '1':
            wishlistList = request.form['wishlisttext']
            sqlquerry = f'UPDATE t{roomid} SET wishlist = "{wishlistList}" WHERE useridentificator = "{userid}"'
            c.execute(sqlquerry)
            conn.commit()
            return render_template('wishlist.html',name=wishlistname, editstate=editstate, wishlisfromdb=wishlistList)
    return render_template('wishlist.html', name=wishlistname, editstate=editstate, wishlisfromdb=wishlisfromdb)


if __name__ == '__main__':
    app.run()
