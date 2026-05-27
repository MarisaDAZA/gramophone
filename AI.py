from openai import OpenAI
from requests import post
from .配置 import API密钥, 机器人令牌
from .日志 import 日志

客户端 = OpenAI(
    api_key = API密钥,
    base_url = 'https://generativelanguage.googleapis.com/v1beta/openai/',
)

def 生成器(消息流):
    for 消息块 in 消息流:
        if 消息块.choices and 消息块.choices[0].delta.content:
            yield(消息块.choices[0].delta.content.encode('utf-8'))

def 获取AI回复(聊天消息):
    return 客户端.chat.completions.create(
        messages=[
            {
                'role': 'system',
                'content': '你是一个擅长消息提炼的助手，你的任务是总结用户提供的群聊天消息（聊天消息包含用户名），生成一份简洁明了的摘要。避免逐条复述，而是梳理脉络，提炼实质性信息。'
            },        
            {
                'role': 'user',
                'content': 聊天消息
            },
        ],
        model='gemini-3-flash-preview',
        stream=True,
    )
 
def 发送AI总结(聊天消息, group_id):
    消息流 = 获取AI回复(聊天消息)
    # 发送流式消息到云湖服务器，而不是通过CloudFlare代理
    post(f'https://192.144.130.26/open-apis/v1/bot/send-stream?token={机器人令牌}&recvId={group_id}&recvType=group&contentType=markdown',
        data = 生成器(消息流),
        headers = {'Host': 'chat-go.jwzhd.com'},
        verify = False
    )

