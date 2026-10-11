from sqlalchemy import Column, Integer, BigInteger, String, Text, Boolean, ForeignKey, Index, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

声明式基类 = declarative_base()

class 消息模型(声明式基类):
    __tablename__ = '消息'
    消息ID = Column(String(32), primary_key=True)
    发送时间 = Column(BigInteger)
    聊天ID = Column(String(9), ForeignKey('设置.聊天ID'))
    文本 = Column(Text)
    发送者ID = Column(String(7))
    发送者昵称 = Column(String(20))
    __table_args__ = (Index('消息索引', '聊天ID', '发送时间'),)

class 设置模型(声明式基类):
    __tablename__='设置'
    聊天ID = Column(String(9),  primary_key=True)
    最大长度 = Column(Integer)
    最大行数 = Column(Integer)
    Markdown = Column(Boolean)
    HTML = Column(Boolean)
    最大消息数 = Column(Integer)

# 引擎 = create_engine(数据库地址)
# 声明式基类.metadata.create_all(引擎)
# 会话 = sessionmaker(bind=引擎)
