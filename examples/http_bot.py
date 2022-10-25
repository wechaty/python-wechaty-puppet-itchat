import asyncio
from quart import Quart
from wechaty import Wechaty, get_logger, ContactQueryFilter, WechatyOptions,Contact,FileBox,Message,WechatyPlugin,RoomQueryFilter
# from wechaty_puppet_itchat import PuppetItChat
import sys
import os
if os.name == 'nt':
    sys.path.insert(0,os.path.realpath(f'{os.path.abspath(os.path.dirname(os.path.dirname(__file__)))}\src'))
sys.path.insert(0,os.path.realpath(f'{os.path.abspath(os.path.dirname(os.path.dirname(__file__)))}/src'))

from wechaty_puppet_itchat import PuppetItChat
from wechaty_plugin_contrib.contrib.httpplugin import httpbotplugin
from wechaty_plugin_contrib.contrib.ding_dong_plugin import DingDongPlugin
import os
os.environ['ASYNC_COMPONENTS'] = 'ITCHAT_UOS_ASYNC'
welcome = """=============== Powered by Python-Wechaty-puppet-itchat ===============
修改代码后可以热重启的bot示例。
"""
print(welcome)
log = get_logger('MyBot')


# 主程序启动web运行
if __name__ == '__main__':
    puppet = PuppetItChat(options=None)
    bot = Wechaty(options=WechatyOptions(puppet=puppet,host='127.0.0.1',port=19002))
    bot.use([httpbotplugin(),DingDongPlugin()])
    asyncio.run(bot.start())
