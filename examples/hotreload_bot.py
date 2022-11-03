import asyncio
import uvicorn
from fastapi import Depends, FastAPI
from wechaty import Wechaty, get_logger, ContactQueryFilter, WechatyOptions,Contact,FileBox,Message,RoomQueryFilter
import sys
import os
if os.name == 'nt':
    sys.path.insert(0,os.path.realpath(f'{os.path.abspath(os.path.dirname(os.path.dirname(__file__)))}\src'))
    print(os.path.realpath(f'{os.path.abspath(os.path.dirname(os.path.dirname(__file__)))}\src'))
sys.path.insert(0,os.path.realpath(f'{os.path.abspath(os.path.dirname(os.path.dirname(__file__)))}/src'))

# sys.path.append('..\src\wechaty_puppet_itchat\itchat')
from wechaty_puppet_itchat import PuppetItChat
from grpclib.exceptions import StreamTerminatedError
from pydantic import BaseModel
import requests
import os
from wechaty_puppet.exceptions import WechatyPuppetError

os.environ['ASYNC_COMPONENTS'] = 'ITCHAT_UOS_ASYNC'
welcome = """=============== Powered by Python-Wechaty-puppet-itchat ===============
修改代码后可以热重启的bot示例。
"""
print(welcome)
log = get_logger('MyBot')

# 创建json数据模型
class Item(BaseModel):
    msg_type: str
    name: str = None
    msg: str = None
    imagebase64: bytes = None
    contact_id: str = None
    alias: str = None
    weixin: str = None


# 继承wechaty类，并设置回调函数
class MyBot(Wechaty):
    def __call__(self):
        return self
    async def start(self):
        """
        start wechaty bot
        :return:
        """
        try:

            await self.init_puppet()
            await self.init_puppet_event_bridge(self.puppet)

            log.info('starting puppet ...')
            await self.puppet.start()

            self.started = True

        except (requests.exceptions.ConnectionError, StreamTerminatedError, OSError):

            log.error('The network is not good, the bot will try to restart after 60 seconds.')
            await asyncio.sleep(60)
            await self.restart()

        else:
            pass

# 创建一个bot实例
puppet = PuppetItChat(options=None)
bot = MyBot(options=WechatyOptions(puppet=puppet))
app = FastAPI()


# 设置web启动运行bot实例
@app.on_event("startup")
async def bot_main():
    asyncio.create_task(bot.start())
    return 200

# 设置发送消息函数
@app.get('/send_msg2')
def send_msg2():
    return 200
# 设置发送消息函数
@app.post('/send_msg')
async def send_msg(item: Item, bot=Depends(bot)):
    try:
        await send_report(bot, item.msg_type, item.name, item.msg)
        return 200
    except Exception as e:
        log.exception(e)
        return 404

async def send_report(bot, msg_type, name, msg):
    log.info('Bot_' + 'send_report()')
    try:
        if msg_type == 'group_msg':
            # room = bot.puppet.itchat.search_chatrooms(name = name )
            # room = room[0]['UserName']
            # room = bot.Room.load(room)
            # await room.say(msg)
            room = await bot.Room.find(query=RoomQueryFilter(topic=name))
            await room.say(msg)
        elif msg_type == 'private_msg':
            contact = bot.puppet.itchat.search_friends(name=name)
            print(contact)
            # contact =await bot.Contact.find(query=ContactQueryFilter(name=name))
            contact = contact[0].get('UserName')
            contact = bot.Contact.load(contact)
            await contact.say(msg)
            # print(contact["contact_id"])
            # await bot.puppet.message_send_text(conversation_id=contact[1].get("UserName"),message=msg)
            # await bot.puppet.itchat.send_msg(msg = 'test', toUserName=name)
            return 200
        else:
            return 0
    except Exception as e:
        log.exception(e)
# 
# 设置web退出关闭bot实例
@app.on_event("shutdown")
async def bot_stop():
    asyncio.create_task(bot.stop())
    return 200
# async def main():
#     config = uvicorn.Config("hotreload_bot:app",port=19002,log_level='info',reload=True)
#     server = uvicorn.Server(config)
#     await server.serve()
# 
# 主程序启动web运行
if __name__ == '__main__':
    # hotreload_bot为python文件名称
    # 本地运行可设置host为127.0.0.1
    # 远程调用可设置host为0.0.0.1，Port需要放行（友情提示：如果用云主机需要在云端放行端口）
    uvicorn.run(app="hotreload_bot:app", host="127.0.0.1", port=19002, reload=True, log_level="info",debug=True)
    # asyncio.run(main())
