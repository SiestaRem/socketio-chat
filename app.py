from flask import Flask, render_template,request,redirect,session,jsonify
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from extension import db
from datetime import datetime

##init
app = Flask('__main__', static_folder="static",template_folder="templates")
socketio = SocketIO(app)
app.config['SECRET_KEY'] = "RemSiesta"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app=app)
from model import *

with app.app_context():
    db.create_all()


###########登录###########

usercount = 0
online_users = []
##登录
@app.route("/" )
def login():
    if 'user_nickname' in session:
        return redirect('/chat')
    return render_template("login.html")

@app.route("/set-nickname",methods=['Post'] )
def submit_nickname():
    nickname = request.form.get('nickname')
    # 验证
    existing_user = User.query.filter_by(nickname=nickname).first()
    if existing_user:
        session['user_nickname']=nickname
     
        return redirect('/chat')
    else:
        user = User(nickname=nickname)
        db.session.add(user)
        db.session.commit()

        session['user_nickname']=nickname
       
        return redirect('/chat')

@app.route('/chat',methods=['POST','GET'])
def main():
    nickname = session.get('user_nickname')

    if not nickname:
        session.pop('user_nickname',None)
        return redirect('/')
    
    user = User.query.filter_by(nickname=nickname).first()
    if not user:
        session.pop('user_nickname', None)
        return redirect('/')
    
    return render_template('index.html',name=nickname)

###########登录###########


###########上下线########
#全局消息广播 初始化群聊 传入user信息
@socketio.on('connect')
def userconnect(sid):
    global usercount
    online_users.append(session['user_nickname'])

    usercount += 1
    emit('user_joined', {
        'nickname': session['user_nickname'],
        'users':online_users,
        'count': usercount
    }, broadcast=True)
    
@socketio.on('disconnect')
def userleft():
   global usercount
   online_users.remove(session['user_nickname'])
   usercount -= 1

   emit('user_left', {
        'nickname': session['user_nickname'],
        'users' : online_users,
        'count': usercount
    }, broadcast=True)
###########上下线########



###########群聊##########




@socketio.on('show_groups')
def handle_show_groups(user):
    groups = get_user_groups(user_nickname=user)
  

    emit('loadGroups',groups,room = request.sid)



@socketio.on('start_group_chat')
def handle_start_group_chat(target_group):
    '''
    第一次点击群组显示历史消息并加入房间，方便后续实时显示消息
    '''
    room_id = get_room_id_group(target_group)
    join_room(room_id)
    data = get_group_messages(group_id=room_id)
    print(data)

    emit('loadGroupHistory',data,room=request.sid)

@socketio.on('create_group')
def handle_create_group(data):
    
    group_name = data['group_name']
    exit = Group.query.filter_by(room_name = group_name).first()
  
    if not exit:
        group = Group(room_name=group_name)
        db.session.add(group)
        db.session.commit()
        group_id = group.group_id
        nickname = data['user']

        groupmember = GroupMember(user_nickname=nickname,group_id=group_id,is_host='host')
        db.session.add(groupmember)
        db.session.commit()

        emit('group_created_success', {
            'group_name': group_name,
            'user' : nickname,
            'type': 'host'
        },room=request.sid)

    else:
        emit('group_created_repeat', {
                'group_name': group_name
            },room=request.sid)



@socketio.on('join_group')
def handle_join_group(data):
    user = data['user']
    group_name = data['group_name']
    exit = Group.query.filter_by(room_name = group_name).first()
    if exit:
        boo = is_user_in_group(user_nickname=user,room_name=group_name)
        
        if not boo:
          
            roomid = get_room_id_group(room_name=group_name)
            groupmember = GroupMember(user_nickname=user,group_id=roomid,is_host='customer')
            db.session.add(groupmember)
            db.session.commit()

            emit('group_joined_success', {
                'group_name': group_name,
                'user':user,
                'type':'customer'
            },room=request.sid)

        else:
           
            emit('user_had_in',{
                'group_name': group_name,
                'user':user
            },room=request.sid)
    else:
        emit('group_not_exit',{
            'group_name': group_name,
            'user':user
        },room=request.sid)



@socketio.on('leave_group')
def handle_leave_group(data):
    user = data['user']
    group_name = data['group_name']
    exit = Group.query.filter_by(room_name = group_name).first()
    if exit:
        boo = is_user_in_group(user_nickname=user,room_name=group_name)
        
        if not boo:
            
            emit('group_not_in', {
                'group_name': group_name,
                'user':user,
                'type':'customer'
            },room=request.sid)

        else:
            ##是否为最后一人
            groupid = get_room_id_group(room_name=group_name)
            members = GroupMember.query.filter_by(group_id=groupid).count()
            if members == 1:
                group = Group.query.filter_by(room_name=group_name).first()
                db.session.delete(group)
                db.session.commit()
                emit('group_had_leave_last',{
                    'group_name': group_name,
                    'user':user
                },room=request.sid)

            else:
                member = GroupMember.query.filter_by(user_nickname=user,
                                                     group_id=groupid).first()
                db.session.delete(member)
                db.session.commit()

                emit('group_had_leave',{
                    'group_name': group_name,
                    'user':user
                },room=request.sid)

    else:
        emit('group_not_exit',{
            'group_name': group_name,
            'user':user
        },room=request.sid)


@socketio.on('group_message')
def Send_Group_Msg(data):
    print(data)
    room_id = get_room_id_group(room_name=data['group_name'])
    groupmessage = GroupMessage(group_id=room_id,
                                sender_nickname=data['sender'],
                                content=data['msg'])
    db.session.add(groupmessage)
    db.session.commit()

    emit('Sendtogroup',{'room_name':data['group_name'],
                        'sender':data['sender'],
                        'content':data['msg']},
                        room=room_id)
    
    print(f'py send group message roomid:{room_id}')


###########群聊##########



###########私聊###########



def get_room_id(nickname1, nickname2):
    id1,id2 = get_user_id_by_nickname(nickname=nickname1),get_user_id_by_nickname(nickname=nickname2)
    min_val, max_val = sorted([id1, id2])
    
    return min_val * 1000 + max_val


@socketio.on('start_private_chat')
def handle_start_private_chat(target_user):
    current_user = session['user_nickname']
    room_id = get_room_id(current_user, target_user)
    
    join_room(room_id)
    
    data =  get_private_messages(user1_nickname=current_user,user2_nickname=target_user)


    emit('loadHistoryMessages',data,room=request.sid)


@socketio.on('person_message')
def Send_Person_Msg(data):

    user1,user2 = data['user'],data['receiver']
    room_id = get_room_id(nickname1=user1,nickname2=user2)


    privatemessage = PrivateMessage(sender_nickname=user1,receiver_nickname=user2,content=data['msg'])
    db.session.add(privatemessage)
    db.session.commit()

    emit('SendtoPerson',{'content':data['msg'], 'sender':data['user'], 'receiver':data['receiver']}, room = room_id)
    

###########私聊###########

@socketio.on('try_git')
def try_(content):
    print(f'try success  {content}')

def try_git(a):
    print(f'try success  {a}')
if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
