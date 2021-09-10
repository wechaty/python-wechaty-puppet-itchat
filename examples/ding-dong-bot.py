import asyncio

from wechaty import Wechaty, WechatyOptions
from wechaty_plugin_contrib import DingDongPlugin
from wechaty_puppet_itchat import PuppetItChat

from pyppeteer import launch


async def main():
    puppet = PuppetItChat(options=None)
    bot = Wechaty(options=WechatyOptions(puppet=puppet))

    plugin = DingDongPlugin()
    bot.use(plugin)

    await bot.start()

asyncio.run(main())
