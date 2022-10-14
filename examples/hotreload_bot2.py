import asyncio
from quart import Quart
from wechaty import Wechaty, get_logger, ContactQueryFilter, WechatyOptions,Contact,FileBox,Message
# from wechaty_puppet_itchat import PuppetItChat
import sys
import os
if os.name == 'nt':
    sys.path.insert(0,os.path.realpath(f'{os.path.abspath(os.path.dirname(os.path.dirname(__file__)))}\src'))
    print(os.path.realpath(f'{os.path.abspath(os.path.dirname(os.path.dirname(__file__)))}\src'))
sys.path.insert(0,os.path.realpath(f'{os.path.abspath(os.path.dirname(os.path.dirname(__file__)))}/src'))
from wechaty_puppet_itchat.puppet import PuppetItChat
from pydantic import BaseModel
import os
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

        except:

            log.error('The network is not good, the bot will try to restart after 60 seconds.')
            await asyncio.sleep(60)
            await self.restart()
    async def register_blueprints(self,app):
        @app.get('/send_msg2')
        async def say_hello():
            return 'sucess'
# 创建一个bot实例
puppet = PuppetItChat(options=None)
bot = MyBot(options=WechatyOptions(puppet=puppet))
app = Quart(__name__)
# 设置web启动运行bot实例
@app.before_serving
async def bot_main():
    asyncio.create_task(bot.start())
    return '200'
# 
# 设置web退出关闭bot实例
@app.after_serving
async def bot_stop():
    asyncio.create_task(bot.stop())
    return '200'
# 设置发送消息函数
@app.get('/send_msg2')
async def bot_send():
    await send_msg2()
    return 'hello'
async def send_msg2():
    print('200')
# 设置发送消息函数

# 主程序启动web运行
if __name__ == '__main__':
    # hotreload_bot为python文件名称
    # 本地运行可设置host为127.0.0.1
    # 远程调用可设置host为0.0.0.1，Port需要放行（友情提示：如果用云主机需要在云端放行端口）
    # uvicorn.run(app="hotreload_bot:app", host="127.0.0.1", port=19002, reload=True, log_level="info",debug=True)
    app.run(host='127.0.0.1',port=19002,debug=True)
