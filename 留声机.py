from re import escape, compile
from json import loads
from yunhu.openapi import Openapi
from yunhu.subscription import Subscription
from time import time
from requests import post
from .数据库 import db, 消息模型, 设置模型
from .配置 import 机器人令牌
from .AI import summary
from .日志 import 日志

接口 = Openapi(机器人令牌)
订阅 = Subscription()

@订阅.onMessageNormal
def 普通消息(事件):
    # 非群聊消息
    if 事件['chat']['chatType'] != 'group':
        return

    # 获取群聊设置
    聊天ID = 事件['chat']['chatId']
    设置 = 设置模型.query.get(聊天ID)
    if not 设置:
        设置 = 设置模型(聊天ID)
        db.session.add(设置)
        db.session.commit() 

    # 储存消息到数据库
    if 事件['message']['contentType'] == 'text' \
    or 设置.md and 事件['message']['contentType'] == 'markdown' \
    or 设置.html and 事件['message']['contentType'] == 'html':
        文本 = 事件['message']['content'].get('text')
        if 文本 and len(文本) <= 设置.最大长度 and 文本.count('\n') < 设置.最大行数:
            消息 = 消息模型(
                事件['message']['msgId'],
                事件['message']['sendTime'],
                聊天ID,
                文本,
                事件['sender']['senderId'],
                事件['sender']['senderNickname'],
            )
            db.session.add(消息)
            db.session.commit()

            # 设置看板
            消息记录 = 消息模型.query.filter_by(聊天ID=聊天ID).order_by(消息模型.发送时间.desc()).limit(设置.最大消息数).all()
            设置看板(聊天ID, 消息记录)

            # 删除旧消息
            消息模型.query.filter(消息模型.聊天ID==聊天ID, 消息模型.发送时间 < 消息记录[-1].发送时间).delete()
            db.session.commit()

@订阅.onMessageInstruction
def 指令消息(事件):
    if 事件['chat']['chatType'] != 'group':
        return
    聊天ID = 事件['chat']['chatId']

    # 清空留声机
    if 事件['message']['commandId'] == 2233:
        if 是管理员(事件):
            消息模型.query.filter_by(聊天ID=聊天ID).delete()
            db.session.commit()
            接口.DismissBotBoard(聊天ID, 'group', '')

    # AI总结
    elif 事件['message']['commandId'] == 2303:
        日志.info(f"AI总结：群{聊天ID}，{事件['message']['content']['text']}个小时。")
        消息记录 = 消息模型.query.filter(消息模型.聊天ID == 聊天ID, 消息模型.发送时间 > int( ( time() - 3600*字符串转小数(事件['message']['content']['text'],0) ) *1000 ) ).order_by(消息模型.发送时间.desc()).all()
        if not 消息记录:
            日志.warning('没有搜索到消息。')
            return
        日志.info(f'搜索到{len(消息记录)}条消息。')
        消息列表=[]
        for 消息 in 消息记录:
            消息列表.append(消息.发送者昵称+': '+消息.文本)
        summary('\n'.join(消息列表), 聊天ID)

    # 删除指定消息
    elif 事件['message']['commandId'] == 2305:
        # 管理员删除所有指定消息
        if 是管理员(事件):
            消息记录 = 消息模型.query.filter(消息模型.聊天ID == 聊天ID, 消息模型.text.like(f"%{事件['message']['content']['text']}%")).all()
        # 非管理员删除自己消息
        else:
            消息记录 = 消息模型.query.filter(消息模型.聊天ID == 聊天ID, 消息模型.sender_id == 事件['sender']['senderId'], 消息模型.text.like(f"%{事件['message']['content']['text']}%")).all()
        if not 消息记录:
            return          
        for 消息 in 消息记录:
            撤回(聊天ID, 消息.消息ID) 
            db.session.delete(消息)
        db.session.commit()
        消息记录 = 消息模型.query.filter_by(聊天ID=聊天ID).order_by(消息模型.发送时间.desc()).all()
        设置看板(聊天ID, 消息记录)

    # 删除指定用户消息
    elif 事件['message']['commandId'] == 2306:
        用户ID = 事件['message']['content'].get('at')
        if not 用户ID:
            用户ID = [ 事件['message']['content']['text'].strip() ]

        # 非管理员只能删除自己消息
        if not 是管理员(事件):
            if 事件['sender']['senderId'] in 用户ID:
                用户ID = [ 事件['sender']['senderId'] ]
            else:
                return

        消息记录 = 消息模型.query.filter(消息模型.聊天ID == 聊天ID, 消息模型.发送者ID.in_(用户ID)).all()
        if not 消息记录:
            return
        for 消息 in 消息记录:
            撤回(聊天ID, 消息.消息ID)
            db.session.delete(消息)
        db.session.commit()
        消息记录 = 消息模型.query.filter_by(聊天ID=聊天ID).order_by(消息模型.发送时间.desc()).all()
        设置看板(聊天ID, 消息记录)

@订阅.onBotSetting
def 机器人设置(事件):
    聊天ID = 事件['groupId']
    设置JSON = loads(事件['settingJson'])
    设置 = 设置模型(
        聊天ID,
        字符串转整数(设置JSON['ckdqox']['value'], 100),
        字符串转整数(设置JSON['qmkrjb']['value'], 1),
        设置JSON['xqlsnd']['value'],
        设置JSON['jyljsb']['value'],
        字符串转整数(设置JSON['tlyguo']['value'], 300)
    )
    db.session.merge(setting)
    db.session.commit()

# 转义Markdown字符
模式=compile(f'([{escape(r'!#()*+-.>[\]_`|~')}])')
def 设置看板(聊天ID, 消息记录):
    消息列表 = []
    for 消息 in 消息记录:
        消息列表.append(f'**{消息.发送者昵称}:** {模式.sub(r'\\\1', 消息.文本)}')
    接口.SetBotBoard(聊天ID, 'group', '', 'markdown', '\n'.join(消息列表), 0)

def 是管理员(事件):
    '''检测是否为管理员'''
    return 事件['sender']['senderUserLevel'] in ['owner', 'administrator']

def 撤回(聊天ID, 消息ID):
    '''撤回消息'''
    参数 = {
        'chatId': 聊天ID,
        'chatType': 'group',
        'msgId': 消息ID
    }
    post(f'https://chat-go.jwzhd.com/open-apis/v1/bot/recall?token={机器人令牌}', json=参数)

def 字符串转小数(字符串, 默认值):
    try:
        return float(字符串.strip())
    except ValueError:
        return 默认值

def 字符串转整数(字符串, 默认值):
    try:
        整数 = int(字符串.strip())
    except ValueError:
        整数 = 默认值
    if 整数 <= 0:
        整数 = 1
    elif 整数 > 1000:
        整数 = 1000
    return 整数
