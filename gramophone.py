from config import MESSAGE_BOARD_TOKEN
from re import escape, compile
from json import loads
from yunhu.openapi import Openapi
from yunhu.subscription import Subscription
from db_schema import db, Messages, MessageSettings
from ai import summary, logger
from time import time, ctime
from requests import post

token = MESSAGE_BOARD_TOKEN
openapi = Openapi(token)
sub = Subscription()

@sub.onMessageNormal
def onMessageNormalHander(event):
    if event['chat']['chatType'] != 'group':
        return

    # 获取群聊设置
    chatId = event['chat']['chatId']
    setting = MessageSettings.query.get(chatId)
    if not setting:
        setting = MessageSettings(chatId)
        db.session.add(setting)
        db.session.commit() 

    # 储存消息到数据库
    if event['message']['contentType'] == 'text' \
    or setting.md and event['message']['contentType'] == 'markdown' \
    or setting.html and event['message']['contentType'] == 'html':
        text = event['message']['content'].get('text')
        if text and len(text) <= setting.max_length and text.count('\n') < setting.max_lines:
            message = Messages(
                event['message']['msgId'],
                event['message']['parentId'],
                event['message']['sendTime'],
                chatId,
                event['message']['contentType'],
                text,
                event['sender']['senderId'],
                event['sender']['senderUserLevel'],
                event['sender']['senderNickname'],
                event['sender']['senderAvatarUrl']
            )
            db.session.add(message)
            db.session.commit()

            # 设置看板
            messages = Messages.query.filter_by(chat_id=chatId).order_by(Messages.send_time.desc()).limit(setting.max_quantity).all()
            board(chatId, messages)

            # 删除旧消息
            Messages.query.filter(Messages.chat_id==chatId, Messages.send_time < messages[-1].send_time).delete()
            db.session.commit()

# 转义Markdown字符
md_chars=r'!#()*+-.>[\]_`|~'
md_pattern=compile(f'([{ escape(md_chars) }])')

def board(chatId, messages):
    '''设置看板'''
    texts=''
    for message in messages:
        texts+='**'+message.sender_nickname+':** '+md_pattern.sub(r'\\\1', message.text)+'\n'
    openapi.SetBotBoard(chatId, 'group', '', 'markdown', texts[:-1], 0)

def admin(event):
    '''检测是否为管理员'''
    return event['sender']['senderUserLevel'] in ['owner', 'administrator']

def recall(msgId, chatId):
    '''撤回消息'''
    params = {
        'msgId': msgId,
        'chatId': chatId,
        'chatType': 'group'
    }
    post('https://chat-go.jwzhd.com/open-apis/v1/bot/recall?token='+token, json=params)

@sub.onMessageInstruction
def onMessageInstructionHander(event):
    if event['chat']['chatType'] != 'group':
        return
    group_id = event['chat']['chatId']

    # 清空留声机
    if event['message']['commandId'] == 2233:
        if admin(event):
            Messages.query.filter_by(chat_id=group_id).delete()
            db.session.commit()
            openapi.DismissBotBoard(group_id, 'group', '')

    # AI总结
    elif event['message']['commandId'] == 2303:
        logger.info(f"[{ctime()}] AI总结：群({group_id})，{event['message']['content']['text']}个小时。")
        messages = Messages.query.filter(Messages.chat_id == group_id, Messages.send_time > int( ( time() - 3600*str2float(event['message']['content']['text'],0) ) *1000 ) ).order_by(Messages.send_time.desc()).all()
        if not messages:
            logger.warning('没有搜索到消息。')
            return
        logger.info(f'{len(messages)}条消息。')
        texts=''
        for message in messages:
            texts=message.sender_nickname+': '+message.text+'\n'+texts
        summary(texts, group_id)

    # 删除指定消息
    elif event['message']['commandId'] == 2305:
        # 管理员删除所有指定消息
        if admin(event):
            messages = Messages.query.filter(Messages.chat_id == group_id, Messages.text.like(f"%{event['message']['content']['text']}%")).all()
        # 非管理员删除自己消息
        else:
            messages = Messages.query.filter(Messages.chat_id == group_id, Messages.sender_id == event['sender']['senderId'], Messages.text.like(f"%{event['message']['content']['text']}%")).all()
        if not messages:
            return          
        for message in messages:
            recall(message.msg_id, group_id) 
            db.session.delete(message)
        db.session.commit()
        messages = Messages.query.filter_by(chat_id=group_id).order_by(Messages.send_time.desc()).all()
        board(group_id, messages)

    # 删除制定用户消息
    elif event['message']['commandId'] == 2306:
        users = event['message']['content'].get('at')
        if not users:
            users = [ event['message']['content']['text'].strip() ]

        # 非管理员只能删除自己消息
        if not admin(event):
            if event['sender']['senderId'] in users:
                users = [ event['sender']['senderId'] ]
            else:
                return

        messages = Messages.query.filter(Messages.chat_id == group_id, Messages.sender_id.in_(users)).all()
        if not messages:
            return
        for message in messages:
            recall(message.msg_id, group_id)
            db.session.delete(message)
        db.session.commit()
        messages = Messages.query.filter_by(chat_id=group_id).order_by(Messages.send_time.desc()).all()
        board(group_id, messages)

def str2float(string, default):
    try:
        return float(string.strip())
    except ValueError:
        return default

def str2int(string, default):
    try:
        integer = int(string.strip())
    except ValueError:
        integer = default
    if integer <= 0:
        integer = 1
    elif integer > 1000:
        integer = 1000
    return integer

@sub.onBotSetting
def onBotSettingHander(event):
    group_id = event['groupId']
    settingJson = loads(event['settingJson'])
    setting = MessageSettings(
        group_id,
        str2int(settingJson['ckdqox']['value'], 100),
        str2int(settingJson['qmkrjb']['value'], 1),
        settingJson['xqlsnd']['value'],
        settingJson['jyljsb']['value'],
        str2int(settingJson['tlyguo']['value'], 300)
    )
    db.session.merge(setting)
    db.session.commit()
