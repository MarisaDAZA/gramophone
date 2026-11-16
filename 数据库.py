from ..db import db

class 消息模型(db.Model):
    __tablename__ = '消息'
    消息ID = db.Column(db.String(32), primary_key=True)
    发送时间 = db.Column(db.BigInteger)
    聊天ID = db.Column(db.String(9), db.ForeignKey('设置.聊天ID'))
    文本 = db.Column(db.Text)
    发送者ID = db.Column(db.String(7))
    发送者昵称 = db.Column(db.String(20))
    __table_args__ = (db.Index('消息索引', '聊天ID', '发送时间'),)

class 设置模型(db.Model):
    __tablename__ = '设置'
    聊天ID = db.Column(db.String(9),  primary_key=True)
    最大长度 = db.Column(db.Integer, default=100)
    最大行数 = db.Column(db.Integer, default=1)
    Markdown = db.Column(db.Boolean)
    HTML = db.Column(db.Boolean)
    最大消息数 = db.Column(db.Integer, default=300)
    黑名单 = db.Column(db.Text, default='')
    屏蔽词 = db.Column(db.Text, default='')
