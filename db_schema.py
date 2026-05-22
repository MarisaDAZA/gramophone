from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Messages(db.Model):
    __tablename__='messages'
    msg_id = db.Column(db.String(32), primary_key=True)
    parent_id = db.Column(db.String(32))
    send_time = db.Column(db.BigInteger)
    chat_id = db.Column(db.String(9), db.ForeignKey('message_settings.group_id'))
    content_type = db.Column(db.String(10))
    text = db.Column(db.Text)
    sender_id = db.Column(db.String(7))
    sender_user_level = db.Column(db.String(13))
    sender_nickname = db.Column(db.String(20))
    sender_avatar_url = db.Column(db.String(70))
    __table_args__=(db.Index('ix_messages_group_time', 'chat_id', 'send_time'),)

    def __init__(self, msgId, parentId, sendTime, chatId, contentType, text, senderId, senderUserLevel, senderNickname, senderAvatarUrl):
        self.msg_id = msgId
        self.parent_id = parentId
        self.send_time = sendTime
        self.chat_id = chatId
        self.content_type = contentType
        self.text = text
        self.sender_id = senderId
        self.sender_user_level = senderUserLevel
        self.sender_nickname = senderNickname
        self.sender_avatar_url = senderAvatarUrl

class MessageSettings(db.Model):
    __tablename__='message_settings'
    group_id = db.Column(db.String(9),  primary_key=True)
    max_length = db.Column(db.Integer)
    max_lines = db.Column(db.Integer)
    md = db.Column(db.Boolean)
    html = db.Column(db.Boolean)
    max_quantity = db.Column(db.Integer)

    def __init__(self, group_id, max_length=100, max_lines=1, md=False, html=False, max_quantity=300):
        self.group_id = group_id
        self.max_length = max_length
        self.max_lines = max_lines
        self.md = md
        self.html = html
        self.max_quantity = max_quantity
