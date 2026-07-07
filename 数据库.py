from db import db

class 消息模型(db.Model):
    __tablename__='消息'
    消息ID = db.Column(db.String(32), primary_key=True)
    发送时间 = db.Column(db.BigInteger)
    聊天ID = db.Column(db.String(9), db.ForeignKey('设置.聊天ID'))
    文本 = db.Column(db.Text)
    发送者ID = db.Column(db.String(7))
    发送者昵称 = db.Column(db.String(20))
    __table_args__=(db.Index('消息索引', '聊天ID', '发送时间'),)

    def __init__(self, 消息ID, 发送时间, 聊天ID, 文本, 发送者ID, 发送者昵称):
        self.消息ID = 消息ID
        self.发送时间 = 发送时间
        self.聊天ID = 聊天ID
        self.文本 = 文本
        self.发送者ID = 发送者ID
        self.发送者昵称 = 发送者昵称

class 设置模型(db.Model):
    __tablename__='设置'
    聊天ID = db.Column(db.String(9),  primary_key=True)
    最大长度 = db.Column(db.Integer)
    最大行数 = db.Column(db.Integer)
    Markdown = db.Column(db.Boolean)
    HTML = db.Column(db.Boolean)
    最大消息数 = db.Column(db.Integer)

    def __init__(self, 聊天ID, 最大长度=100, 最大行数=1, Markdown=False, HTML=False, 最大消息数=300):
        self.聊天ID = 聊天ID
        self.最大长度 = 最大长度
        self.最大行数 = 最大行数
        self.Markdown = Markdown
        self.HTML = HTML
        self.最大消息数 = 最大消息数
