import asyncio
import uvicorn
from fastapi import Depends, FastAPI
from wechaty import Wechaty, get_logger, ContactQueryFilter, WechatyOptions
from wechaty_puppet_itchat import PuppetItChat
from pydantic import BaseModel

welcome = """=============== Powered by Python-Wechaty-puppet-itchat ===============
修改代码后可以热重启的bot示例。
"""
print(welcome)
log = get_logger('RoomBot')


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
@app.post('/send_msg')
async def send_msg(item: Item, bot=Depends(bot)):
    try:
        await send_report(bot, item.msg_type, item.name, item.contact_id)
        return 200
    except Exception as e:
        log.exception(e)
        return 404


async def send_report(bot, msg_type, name, msg):
    log.info('Bot_' + 'send_report()')
    try:
        if msg_type == 'group_msg':
            pass
        elif msg_type == 'private_msg':
            contact = await bot.Contact.find(query=ContactQueryFilter(name=name))
            await contact.say(msg)
        else:
            return 0
    except Exception as e:
        log.exception(e)


# 设置web退出关闭bot实例
@app.on_event("shutdown")
async def bot_stop():
    asyncio.create_task(bot.stop())
    return 200


# 主程序启动web运行
if __name__ == '__main__':
    # hotreload_bot为python文件名称
    # 本地运行可设置host为127.0.0.1
    # 远程调用可设置host为0.0.0.1，Port需要放行（友情提示：如果用云主机需要在云端放行端口）
    uvicorn.run(app="examples.hotreload_bot:app", host="127.0.0.1", port=19002, reload=True, log_level="info")
