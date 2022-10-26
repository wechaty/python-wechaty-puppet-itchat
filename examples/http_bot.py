import asyncio
from quart import Quart
from wechaty import Wechaty, get_logger, ContactQueryFilter,RoomQueryFilter, WechatyOptions,Contact,FileBox,Message,WechatyPlugin,RoomQueryFilter
from quart import Quart,request
import sys
import os
if os.name == 'nt':
    sys.path.insert(0,os.path.realpath(f'{os.path.abspath(os.path.dirname(os.path.dirname(__file__)))}\src'))
sys.path.insert(0,os.path.realpath(f'{os.path.abspath(os.path.dirname(os.path.dirname(__file__)))}/src'))

from wechaty_puppet_itchat import PuppetItChat
from wechaty_plugin_contrib.contrib.ding_dong_plugin import DingDongPlugin
import os
os.environ['ASYNC_COMPONENTS'] = 'ITCHAT_UOS_ASYNC'
welcome = """=============== Powered by Python-Wechaty-puppet-itchat ===============
修改代码后可以热重启的bot示例。
"""
print(welcome)
log = get_logger('MyBot')
class httpbotplugin(WechatyPlugin):
    async def blueprint(self, app: Quart) -> None:
        
        @app.get('/send_msg2')
        async def say_hello():
            return 'sucess'
        @app.post('/send_msg')
        async def send_msg():
            item = await request.get_json()
            try:
                msg = get_file_url_str(item.get('msg'),None)
                await send_report(item.get('msg_type'), item.get('name'), msg)
                return '200'
            except Exception as e:
                log.exception(e)
                return 404

        async def send_report(msg_type, name, msg):
            log.info('Bot_' + 'send_report()')
            try:
                if msg_type == 'group_msg':
                    room = await self.bot.Room.find(query = RoomQueryFilter(topic = name))
                    await room.ready()
                    await room.say(msg)
                elif msg_type == 'private_msg':
                    contact = await self.bot.Contact.find(query=ContactQueryFilter(name = name))
                    await contact.say(msg)
                    return '200'
                else:
                    return '0'
            except Exception as e:
                log.exception(e)
        def get_file_url_str(path,base64_code=None):
            if base64_code is None:
                if path.startswith(('http://','https://','HTTP://','HTTPS://')):
                    if path.endswith(('.xls','.xlsx','.pdf','.txt','csv','.doc','.docx','.XLS','.XLSX','.PDF','.TXT','.CSV','.DOC','.DOCX')):
                        #获取url里的文件后缀
                        filename =  os.path.basename(path)
                        #传送网络文件
                        fileBox = FileBox.from_url(path,filename)
                        #fileBox=path+'1'
                    elif path.endswith(('BMP','JPG','JPEG','PNG','GIF','bmp','jpg','jpeg','png','gif')):
                        #传送网络图片
                        fileBox = FileBox.from_url(path,'linshi.jpg')
                        #fileBox=path+'2'
                    else:
                        #传送无后缀的网络图片
                        fileBox = FileBox.from_url(path,'linshi.jpg')
                        #fileBox=path+'3'
                        #发送本地文件
                        #fileBox = FileBox.from_file('/Users/fangjiyuan/Desktop/一组外呼情况汇总.xlsx')
            
                elif path.startswith('/') or path.startswith('\\',2):
                    if path.endswith(('.xls','.xlsx','.pdf','.txt','csv','.doc','.docx','.XLS','.XLSX','.PDF','.TXT','.CSV','.DOC','.DOCX')):
                        #获取本地路径里的文件后缀
                        filename =  os.path.basename(path)
                        #传送本地文件
                        fileBox = FileBox.from_file(path,filename)
                        #fileBox=path+'1'
                    elif path.endswith(('BMP','JPG','JPEG','PNG','GIF','bmp','jpg','jpeg','png','gif')):
                        #传送本地图片
                        fileBox = FileBox.from_file(path,'linshi.jpg')
                        #fileBox=path+'2'
                    elif path.endswith('silk'):
                        fileBox = FileBox.from_file(path,'linshi.silk')
                    elif path.endswith(('MP4','mp4')):
                        fileBox = FileBox.from_file(path,'tmp.mp4')
                    else:
                        #传送本地无后缀的图片
                        fileBox = FileBox.from_file(path,'linshi.jpg')
                else:
                    #发送纯文本
                    fileBox = path
            else:
                fileBox = FileBox.from_base64(base64_code,'linshi.jpg')
            return fileBox


# 主程序启动web运行
if __name__ == '__main__':
    puppet = PuppetItChat(options=None)
    bot = Wechaty(options=WechatyOptions(puppet=puppet,host='127.0.0.1',port=19002))
    bot.use([httpbotplugin(),DingDongPlugin()])
    asyncio.run(bot.start())
