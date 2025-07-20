from extension import db
from flask import jsonify
from sqlalchemy.orm import relationship, aliased
from sqlalchemy import or_, and_

########################################################数据库###################################################################################################
    

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nickname = db.Column(db.String(80), unique=True, nullable=False)  # 确保昵称唯一且非空
    create_time = db.Column(db.DateTime, default=db.func.now())
    
    # 关系定义 - 保持不变
    group_memberships = relationship('GroupMember', back_populates='user', cascade='all, delete-orphan')
    sent_group_messages = relationship('GroupMessage', back_populates='sender', cascade='all, delete-orphan')
    sent_private_messages = relationship('PrivateMessage', foreign_keys='PrivateMessage.sender_nickname', back_populates='sender')
    received_private_messages = relationship('PrivateMessage', foreign_keys='PrivateMessage.receiver_nickname', back_populates='receiver')

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "nickname": self.nickname,
            "create_time": self.create_time.isoformat() if self.create_time else None
        }

class Group(db.Model):
    __tablename__ = 'groups'
    
    group_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_name = db.Column(db.String(80), unique=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    # 关系定义
    members = relationship('GroupMember', back_populates='group', cascade='all, delete-orphan')
    messages = relationship('GroupMessage', back_populates='group', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "group_id": self.group_id,
            "room_name": self.room_name,
            'members': len(self.members),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class GroupMember(db.Model):
    __tablename__ = 'group_members'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_nickname = db.Column(db.String(80), db.ForeignKey('users.nickname', ondelete='CASCADE'), nullable=False)  
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id', ondelete='CASCADE'), nullable=False)
    is_host = db.Column(db.Enum('host', 'customer', name='member_type'), nullable=False)
    
    # 关系定义
    user = relationship('User', back_populates='group_memberships')
    group = relationship('Group', back_populates='members')

    def to_dict(self):
        return {
            "id": self.id,
            "user_nickname": self.user_nickname,
            "group_id": self.group_id,
            "is_host": self.is_host
        }

class GroupMessage(db.Model):
    __tablename__ = 'group_messages'
    
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id', ondelete='CASCADE'), nullable=False)
    sender_nickname = db.Column(db.String(80), db.ForeignKey('users.nickname', ondelete='CASCADE'), nullable=False)  # 改为昵称
    content = db.Column(db.Text, nullable=False)
    sent_time = db.Column(db.DateTime, default=db.func.now())
    
    # 关系定义
    sender = relationship('User', back_populates='sent_group_messages')
    group = relationship('Group', back_populates='messages')

    def to_dict(self):
        return {
            "message_id": self.message_id,
            "group_name": self.group.room_name,
            "sender_nickname": self.sender_nickname,
            "content": self.content,
            "sent_time": self.sent_time.isoformat() if self.sent_time else None
        }


class PrivateMessage(db.Model):
    __tablename__ = 'private_messages'
    
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_nickname = db.Column(db.String(80), db.ForeignKey('users.nickname', ondelete='CASCADE'), nullable=False)  # 改为昵称
    receiver_nickname = db.Column(db.String(80), db.ForeignKey('users.nickname', ondelete='CASCADE'), nullable=False)  # 改为昵称
    content = db.Column(db.Text, nullable=False)
    sent_time = db.Column(db.DateTime, default=db.func.now())
    
    # 关系定义
    sender = relationship('User', foreign_keys=[sender_nickname], back_populates='sent_private_messages')
    receiver = relationship('User', foreign_keys=[receiver_nickname], back_populates='received_private_messages')

    def to_dict(self):
        return {
            "message_id": self.message_id,
            "sender_nickname": self.sender_nickname,
            "receiver_nickname": self.receiver_nickname,
            "content": self.content,
            "sent_time": self.sent_time.isoformat() if self.sent_time else None
        }



########################################################数据库###################################################################################################


#########################################################方法函数############################################################################################
def get_room_id_group(room_name):
    '''
    参数 room_name
    
    返回room_id
    '''
    name = Group.query.filter_by(room_name=room_name).first()
    if not name:
        return
    return name.group_id



def get_user_id_by_nickname(nickname):
    """
    根据用户昵称获取用户ID
    
    参数:
        nickname (str): 用户昵称
        
    返回:
        int: 用户ID (如果用户存在)
        None: 如果用户不存在
    """
    user = User.query.filter_by(nickname=nickname).first()
    if user:
        return user.user_id
    return None


def get_user_groups(user_nickname):
    """
    获取用户参与的所有群聊
    :param user_nickname: 用户昵称
    :return: 群组JSON列表
    """
    groups = Group.query.join(GroupMember).filter(
        GroupMember.user_nickname == user_nickname
    ).all()
    
    return [group.to_dict() for group in groups]

def get_group_members(group_id):
    """
    获取群组的所有成员
    :param group_id: 群组ID
    :return: 用户JSON列表
    """
    members = GroupMember.query.filter_by(group_id=group_id).all()
    user_nicknames = [member.user_nickname for member in members]
    
    users = User.query.filter(User.nickname.in_(user_nicknames)).all()
    return [user.to_dict() for user in users]



def get_group_messages(group_id, limit=10):
    """
    获取群组的聊天消息
    :param group_id: 群组ID
    :param limit: 消息数量限制
    :return: 消息JSON列表
    """
    messages = GroupMessage.query.filter_by(
        group_id=group_id
    ).order_by(
        GroupMessage.sent_time.asc()
    ).limit(limit).all()
    
    return [msg.to_dict() for msg in messages]



def get_private_messages(user1_nickname, user2_nickname, limit=20):
    """
    获取两个用户之间的私聊消息
    :param user1_nickname: 第一个用户昵称
    :param user2_nickname: 第二个用户昵称
    :param limit: 消息数量限制
    :return: 消息JSON列表
    """
    messages = PrivateMessage.query.filter(
        or_(
            and_(
                PrivateMessage.sender_nickname == user1_nickname,
                PrivateMessage.receiver_nickname == user2_nickname
            ),
            and_(
                PrivateMessage.sender_nickname == user2_nickname,
                PrivateMessage.receiver_nickname == user1_nickname
            )
        )
    ).order_by(
        PrivateMessage.sent_time.asc()
    ).limit(limit).all()
    
    return [msg.to_dict() for msg in messages]


def is_user_in_group(user_nickname, room_name):
    """
    判断用户是否在指定群组中
    
    参数:
        user_nickname (str): 用户昵称
        room_name (str): 群组名称
        
    返回:
        bool: 如果用户在群组中返回True，否则返回False
    """
    group = Group.query.filter_by(room_name=room_name).first()
    
    if not group:
        return False
    membership = GroupMember.query.filter_by(
        user_nickname=user_nickname,
        group_id=group.group_id
    ).first()
    return membership is not None











#########################################################方法函数############################################################################################
