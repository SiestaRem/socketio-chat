document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素

    const userAvatar = document.getElementById('userAvatar');
    const usernameElement = document.getElementById('username');
    const userList = document.getElementById('userList');
    const groupList = document.getElementById('groupList');
    const messagesContainer = document.getElementById('messagesContainer');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const currentChatTitle = document.getElementById('currentChatTitle');
    const memberCount = document.getElementById('memberCount');
    const onlineCount = document.getElementById('onlineCount');
    const createGroupBtn = document.getElementById('createGroupBtn');
    const joinGroupBtn = document.getElementById('joinGroupBtn');
    const leaveGroupBtn = document.getElementById('leaveGroupBtn');
    const newGroupName = document.getElementById('newGroupName');
    const joinGroupName = document.getElementById('joinGroupName');
    const leaveGroupName = document.getElementById('leaveGroupName');
    const notificationContainer = document.getElementById('notificationContainer');
    
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///初始化显示///


    // 获取当前用户信息（在真实应用中应从服务器获取）
    let currentUser = usernameElement.textContent.trim()
    usernameElement.textContent = currentUser;
    userAvatar.textContent = currentUser.charAt(0);


    // 初始化Socket.io连接
    const socket = io();
    

///////////////////////////////////////////////////////////////////////////////
///////方法函数////////

    // 显示通知
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <h4>${type === 'success' ? '成功' : type === 'danger' ? '错误' : '通知'}</h4>
            <p>${message}</p>
        `;
        
        notificationContainer.appendChild(notification);
        
        // 显示通知
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // 3秒后移除通知
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }
    
    // 添加消息到聊天窗口 sender,message,
    function addMessage(sender, message, isSent = false, time = new Date()) {

    
        const messageElement = document.createElement('div');
        messageElement.className = `message ${isSent ? 'sent' : 'received'}`;
        
        const timeString = time.toLocaleString([], { 
            year: 'numeric', 
            month: '2-digit', 
            day: '2-digit', 
            hour: '2-digit', 
            minute: '2-digit'
        });

        messageElement.innerHTML = `
            <div class="avatar">${isSent ? '我' : sender.charAt(0)}</div>
            <div class="message-content">
                <div class="sender">${isSent ? '我' : sender}</div>
                <div class="text">${message}</div>
                <div class="time">${timeString}</div>
            </div>
        `;
        
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // 更新在线用户列表
    function updateUserList(users) {
        userList.innerHTML = '';
        users.forEach(user => {
            if (user === currentUser) 
                return; // 不显示自己
            
            const userElement = document.createElement('div');
            userElement.className = 'list-item';
            userElement.innerHTML = `
                <div class="badge"></div>
                <div class="name">${user}</div>
                <div class="action">私聊</div>
            `;
            
            //点击用户
            userElement.addEventListener('click', () => {
                currentChatTitle.textContent = `与 ${user} 的私聊`;
                memberCount.textContent = '私聊';
                messagesContainer.innerHTML = '';
                addMessage('系统', `你已开始与 ${user} 的私聊`, false, new Date());

                socket.emit('start_private_chat', target_user = user)

            });
            
            userList.appendChild(userElement);
        });
    }
    

    function showgroups(user){
        socket.emit('show_groups',user)


    }


    // 更新群组列表  
    function updateGroupList(groups) {
        groupList.innerHTML = '';
        groups.forEach(group => {
            const groupElement = document.createElement('div');
            groupElement.className = 'list-item';
            groupElement.innerHTML = `
                <div class="badge"></div>
                <div class="name">${group.room_name}</div>
            `;
    
            
            //点击群聊
            groupElement.addEventListener('click', () => {
                currentChatTitle.textContent = group.room_name;
                memberCount.textContent = `${group.members} 位成员`;
                messagesContainer.innerHTML = '';
                addMessage('系统', `你已在 ${group.room_name} 群组`, false, new Date());
                
                socket.emit('start_group_chat', target_group = group.room_name)
                
            });
            
            groupList.appendChild(groupElement);
        });
    }

    
    // 发送消息  私人和群聊
    function sendMessage() {
        const message = messageInput.value.trim();
        if (message) {

            // 添加到本地聊天窗口
            addMessage(currentUser, message, true, new Date());
            // 通过Socket.io发送消息

            const currentChat = currentChatTitle.textContent;
            
            if (currentChat.includes('的私聊')) {
                // 私聊消息
                const receiver = currentChat.split(' ')[1];
                socket.emit('person_message', {
                    user: currentUser,
                    receiver: receiver,
                    msg: message
                });
            } else {
                // 默认发送到公共聊天室
                socket.emit('group_message', {
                    'group_name':currentChat ,
                    'msg': message,
                    'sender':currentUser
                });
                try_git('js send groupmessage')

            }
            
            messageInput.value = '';
        }
    }
    
    function try_git(content){
        socket.emit('try_git',content)
    }

    

    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    
    // 事件监听
    sendButton.addEventListener('click', sendMessage);
    
    // 按Enter发送消息
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
            
        }
    });
    
    // 创建群组
    createGroupBtn.addEventListener('click', () => {
        const groupName = newGroupName.value.trim();
        if (groupName) {
            socket.emit('create_group', {
                'group_name': groupName,
                'user': currentUser
            });
            // showNotification(`群组 "${groupName}" 创建成功`, 'success');
            newGroupName.value = '';
        } else {
            showNotification('请输入群组名称', 'danger');
        }
    });
    
    // 加入群组
    joinGroupBtn.addEventListener('click', () => {
        const groupName = joinGroupName.value.trim();
        if (groupName) {
            socket.emit('join_group', {
                'group_name': groupName,
                'user': currentUser
            });
            joinGroupName.value = '';
        } else {
            showNotification('请输入群组名称', 'danger');
        }
    });
    
    // 离开群组
    leaveGroupBtn.addEventListener('click', () => {
        const groupName = leaveGroupName.value.trim();
        if (groupName) {
            socket.emit('leave_group', {
                "group_name": groupName,
                "user": currentUser
            });
            leaveGroupName.value = '';
        } else {
            showNotification('请输入群组名称', 'danger');
        }
    });
    
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    
    // Socket.io 具体处理
    socket.on('connect', () => {
        showNotification('已连接到聊天服务器', 'success');
        showgroups(currentUser)
       
    });
    
    socket.on('user_joined', (data) => {
        showNotification(`${data.nickname} 加入了聊天`, 'info');
        onlineCount.textContent = `${data.count} 人在线`;
        updateUserList(data.users);
    });
    
    socket.on('user_left', (data) => {
        showNotification(`${data.nickname} 离开了聊天`, 'warning');
        onlineCount.textContent = `${data.count} 人在线`;
    });
    
    socket.on('loadGroups',(groups) => {
        updateGroupList(groups)
       
    })

    socket.on('loadGroupHistory', (data) => {
        const currentGroup = currentChatTitle.textContent;
        
        data.forEach((message) => {
            // 检查是否是当前群组的消息
            if (message.group_name === currentGroup) {
                const isSent = currentUser === message.sender_nickname;
                addMessage(
                    message.sender_nickname, 
                    message.content, 
                    isSent, 
                    new Date(message.sent_time)
                );
            }
        });
    });


    socket.on('Sendtogroup', (data) => {
        if (data.sender === currentUser) {
         return;
        }
        if (currentChatTitle.textContent === data.room_name) {
            addMessage(data.sender, data.content, false, new Date());

            try_git('js sendtogroup')
        }
    });
    


    socket.on('loadHistoryMessages', (data) => {
        const chatTitle = currentChatTitle.textContent;
        const privateWith = chatTitle.replace("与 ", "").replace(" 的私聊", "").trim();
        
        data.forEach((message) => {
            // 检查是否是当前私聊的双方
            const isCurrentChat = (
                (message.sender_nickname === currentUser && message.receiver_nickname === privateWith) ||
                (message.sender_nickname === privateWith && message.receiver_nickname === currentUser)
            );
            
            if (isCurrentChat) {
                const isSent = currentUser === message.sender_nickname;
                addMessage(
                    message.sender_nickname, 
                    message.content, 
                    isSent, 
                    new Date(message.sent_time)
                );
            }
        });
    });


    socket.on('SendtoPerson', (data) => {
        if (data.sender === currentUser) {
         return;
        }
        if (currentChatTitle.textContent === `与 ${data.sender} 的私聊` || 
            currentChatTitle.textContent === `与 ${data.receiver} 的私聊`) {
            addMessage(data.sender, data.content, false, new Date());
        }
    });
    
    socket.on('group_joined_success', (data) => {
        showNotification(`群组 "${data.group_name}" 加入成功`, 'success');
        showgroups(currentUser)
    });
    
    socket.on('user_had_in', (data) => {
        showNotification(`群组 "${data.group_name}" 已经在里面了`, 'success');
    });


    socket.on('group_created_success', (data) => {
        showNotification(`群组 "${data.group_name}" 创建成功`, 'success');
        showgroups(currentUser)
    });
    
    socket.on('group_created_repeat', (data) => {
        showNotification(`群组 "${data.group_name}" 已经存在`, 'repeat');
    });

    socket.on('group_not_exit', (data) => {
        showNotification(`群组 "${data.group_name}" 不存在`, 'not exit');
    });

    socket.on('group_not_in', (data) => {
        showNotification(`群组 "${data.group_name}" 你不在里面`, 'not exit');
    });

    socket.on('group_had_leave', (data) => {
        showNotification(`群组 "${data.group_name}" 成功退出`, 'success');
        showgroups(currentUser)
    });

    socket.on('group_had_leave_last', (data) => {
        showNotification(`群组 "${data.group_name}" 成功退出并且删除(无成员)`, 'success');
        showgroups(currentUser)
    });
    
    // 初始模拟消息
    setTimeout(() => {
        addMessage('系统', '欢迎使用 RemSiesta 聊天应用!', false, new Date());
        addMessage('系统', '您可以创建群组或加入现有群组开始聊天或者与在线的人私聊', false, new Date());
    }, 1000);
});