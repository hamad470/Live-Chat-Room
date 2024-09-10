from flask import Flask,render_template,request,session,redirect,url_for
from flask_socketio import SocketIO,send,join_room,leave_room
import random
from string import ascii_uppercase
app = Flask(__name__)
app.config['SECRET_KEY']='mysecretkey'
socketio=SocketIO(app)
rooms = {}
def generate_random_code(code_length):
    while True:
        code = ""
        for _ in range(code_length):
            code += random.choice(ascii_uppercase)
        
        if code not in rooms:
            break
    
    return code
            


@app.route('/',methods = ['POST','GET'])
def home():
    if request.method == "POST":
        session.clear()
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join",False)
        create = request.form.get("create",False)
        room = code
        if not name and (code !=False or join !=False):
            return render_template('home.html',error = "enter your name first",code =code,name =name)

        if not code and join !=False:
            return render_template('home.html',error = "enter the code of room",code =code,name =name)
        if create !=False:
            room = generate_random_code(4)
            rooms[room]={"members":0,'messages':[]}
        elif code not in rooms:
              return render_template('home.html',error = "room with this code does not exists",code =code,name =name)

        session['name']=name
        session['room']=room
        return redirect(url_for('room'))

    return render_template('home.html')
@app.route('/room',methods = ['POST','GET'])
def room():
    room = session.get('room')
    if session.get('room')==None or session.get('name')==None or session.get('room') not in rooms:
        return redirect(url_for("home"))
    return render_template('room.html',code=room,messages = rooms[room]['messages'])
@socketio.on('connect')
def connect(auth):
    room = session.get('room')
    name = session.get('name')
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    join_room(room)
    
    send({"name":name,"message":"has entered room"},to=room)
    rooms[room]['members']+=1
    print(f"{name} has joined  room {room}")
@socketio.on("disconnect")
def disconnect():
    room = session.get('room')
    name = session.get('name')
    leave_room(room)
    if room in rooms:
        rooms[room]['members']-=1
        if rooms[room]['members']<=0:
            del rooms[room]
    send({"name":name,"message":"has left the room"},to=room)
    print(f"{name} has left the room {room}")
@socketio.on("message")
def message(data):
    room = session.get("room")
    name = session.get("name")
    if room not in rooms:
        return
    content = {"name":name,"message":data['data']}
    rooms[room]['messages'].append(content)
    send(content,to=room)
    print(f"name :{name} : {content}")

if __name__ == '__main__':
    socketio.run(app,debug=True)