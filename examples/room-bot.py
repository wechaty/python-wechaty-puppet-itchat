import asyncio
from typing import List, Optional

from wechaty_grpc.wechaty.puppet import MessageType

from wechaty_puppet_itchat.puppet import PuppetItChat, PuppetOptions

from wechaty import (
    Wechaty,
    Message,
    WechatyOptions,
    FileBox,
    Contact,
    Friendship
)
from loguru import logger

SUPPORTED_MESSAGE_FILE_TYPES: List[MessageType] = [
    MessageType.MESSAGE_TYPE_ATTACHMENT,
    MessageType.MESSAGE_TYPE_EMOTICON,
    MessageType.MESSAGE_TYPE_IMAGE,
    MessageType.MESSAGE_TYPE_VIDEO
]


class Bot(Wechaty):
    async def on_scan(self, qr_code: str, status,
                      data=None):
        pass

    async def on_login(self, contact: Contact):
        contact = self.Contact.load(contact_id='filehelper')
        await contact.say('hi')

    async def on_message(self, msg: Message):
        logger.info('receive on message event ...')
        text = msg.text()
        talker = msg.talker() if msg.room() is None else msg.room()

        if msg.type() in SUPPORTED_MESSAGE_FILE_TYPES:
            file_box: Optional[FileBox] = await msg.to_file_box()
            await file_box.to_file(file_box.name, overwrite=True)
            await talker.say(file_box)

        file_box = FileBox.from_url(
            'https://ss3.bdstatic.com/70cFv8Sh_Q1YnxGkpoWK1HF6hhy/it/'
            'u=1116676390,2305043183&fm=26&gp=0.jpg',
            name='ding-dong.jpg')

        file_box1 = FileBox.from_url(
            'https://arxiv.org/pdf/2102.03322.pdf',
            name='2102.03322.pdf')

        if text == 'ding':
            await talker.say('dong')
        if text == 'img':
            await talker.say(file_box)
        if text == 'file':
            await talker.say(file_box1)
        if text == 'get_room_topic':
            topic = await msg.room().topic()
            print(topic)
            await talker.say(topic)

    async def on_friendship(self, friendship: Friendship):
        await friendship.accept()


async def main():
    puppet = PuppetItChat(
        options=PuppetOptions()
    )
    bot = Bot(options=WechatyOptions(
        puppet=puppet,
    ))
    await bot.start()


asyncio.run(main())
