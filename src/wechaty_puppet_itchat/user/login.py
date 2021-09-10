"""
Python Wechaty - https://github.com/wechaty/python-wechaty

Authors:    Jingjing WU (吴京京) <https://github.com/wj-Mcat>

2021-now @ Copyright Wechaty

Licensed under the Apache License, Version 2.0 (the 'License');
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an 'AS IS' BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from __future__ import annotations

import asyncio
from typing import Optional

from pyee import AsyncIOEventEmitter
from requests import Session
from wechaty_puppet import EventScanPayload, ScanStatus
from wechaty_puppet import get_logger
from wechaty_puppet.exceptions import WechatyPuppetError

from wechaty_puppet_itchat.config import LOGIN_TIMEOUT, USER_AGENT
from ..browser import Browser

try:
    from httplib import BadStatusLine
except ImportError:
    from http.client import BadStatusLine

logger = get_logger('Login')


class Login:
    def __init__(self, event_emitter: AsyncIOEventEmitter, browser: Browser):
        self.event_emitter: AsyncIOEventEmitter = event_emitter
        self.browser: Browser = browser

    async def login(self):
        logger.info('start login ...')

        if self.browser.is_alive:
            logger.warning('wechaty has already logged in. please don"t login again ...')
            return

        while not self.browser.is_alive:
            uuid: Optional[str] = self.browser.get_qr_uuid()
            if not uuid:
                raise WechatyPuppetError(f'can"t get qrcode from server')
            self.event_emitter.emit(
                'login',
                EventScanPayload(
                    status=ScanStatus.Waiting,
                    qrcode=uuid,
                    data=None
                )
            )
            await asyncio.sleep(LOGIN_TIMEOUT)

    def logout(self):
        if self.browser.is_alive:
            url = '%s/webwxlogout' % self.browser.login_info['url']
            params = {
                'redirect': 1,
                'type': 1,
                'skey': self.browser.login_info['skey'], }
            headers = {'User-Agent': USER_AGENT}
            self.browser.session.get(url, params=params, headers=headers)
            self.browser.is_alive = False
        self.browser.session.cookies.clear()
