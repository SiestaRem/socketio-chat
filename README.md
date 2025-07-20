# SocketIO-Chat 项目文档

## 部署指南

### 步骤 1：创建项目文件夹
```bash
mkdir socketio-chat
cd socketio-chat
```

### 步骤 2：添加项目文件
将提供的所有源代码文件复制到新创建的文件夹中

### 步骤 3：创建并激活虚拟环境
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### 步骤 4：安装依赖
```bash
pip install -r requirements.txt
```

### 步骤 5：运行应用
```bash
python app.py
```

应用启动后，在浏览器中访问：`http://localhost:5000`

## 项目结构

```
SOCKETIO-CHAT/
├── __pycache__/             # Python 编译缓存文件
├── instance/                # 应用实例文件夹 需要启动项目 会自动创建该文件
│   └── sqlite_database.db   # SQLite 数据库文件
├── static/                  # 静态资源文件夹
│   ├── index.js             #  /chat 主要JavaScript文件
│   └── style.css            #  /chat 主样式表
├── templates/               # HTML模板文件夹
│   ├── index.html           # 主聊天页面
│   └── login.html           # 登录页面
├── venv/                    # 虚拟环境目录 需自己创建
├── app.py                   # Flask 主应用
├── extension.py             # SocketIO扩展和事件处理
├── model.py                 # 数据库模型定义
├── README.md                # 项目说明文档
└── requirements.txt         # Python依赖列表
```

## 核心功能

### 1. 一对一实时聊天
- 用户间点对点即时消息传输
- 消息实时推送与接收
- 在线状态显示

### 2. 多人聊天室管理
- **房间创建**：用户可创建新的聊天室
- **加入房间**：通过房间ID加入现有聊天室
- **退出房间**：随时离开当前聊天室
- **多房间支持**：同时支持多个独立聊天室

### 3. 消息持久化存储
- 使用 **SQLite** 轻量级数据库
- 所有聊天消息永久保存
- 消息历史记录查询功能
- 用户认证信息安全存储

## 技术栈

- **后端**：Python Flask
- **实时通信**：Flask-SocketIO
- **前端**：HTML/CSS/JavaScript
- **数据库**：SQLite + SQLAlchemy ORM

## 使用说明

1. 访问登录页面创建账户或登录
2. 在主界面选择：
   - 与特定用户开始一对一聊天
   - 创建新聊天室或加入现有房间
3. 在聊天界面发送消息
4. 所有聊天记录会自动保存并可在后续会话中查看

# 注！ 
聊天登录页面请输入只有英文的名字，这里我没有完善好，在提交的时候忘记修改了

## 依赖说明

`requirements.txt` 包含以下主要依赖：
```
flask
flask-socketio
flask-sqlalchemy
flask-login
python-dotenv
```

项目使用轻量级SQLite数据库，无需额外数据库服务器配置，开箱即用。