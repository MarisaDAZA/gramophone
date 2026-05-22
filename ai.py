from openai import OpenAI
from config import API_KEY, MESSAGE_BOARD_TOKEN
from requests import post
from logging import getLogger, FileHandler, INFO

logger = getLogger(__name__)
logger.setLevel(INFO)
handler = FileHandler('ai.log')
handler.setLevel(INFO)
logger.addHandler(handler)
logger.info('日志已激活!')

client = OpenAI(
    api_key=API_KEY,
    base_url='https://generativelanguage.googleapis.com/v1beta/openai/',
)

def generator(stream):
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield(chunk.choices[0].delta.content.encode('utf-8'))
        else:
            logger.warning('没有回答。')
            logger.warning(chunk)

def chat(texts):
    return client.chat.completions.create(
        messages=[
            {
                'role': 'system',
                'content': '你是一个擅长消息提炼的助手，你的任务是总结用户提供的群聊天消息（聊天消息包含用户名），生成一份简洁明了的摘要。避免逐条复述，而是梳理脉络，提炼实质性信息。'
            },        
            {
                'role': 'user',
                'content': texts
            },
        ],
        model='gemini-3-flash-preview',
        stream=True,
    )
 
def summary(texts, group_id):
   stream = chat(texts)
   data = generator(stream)
   post(f'https://chat-go.jwzhd.com/open-apis/v1/bot/send-stream?token={MESSAGE_BOARD_TOKEN}&recvId={group_id}&recvType=group&contentType=markdown',data=data,stream=True)

