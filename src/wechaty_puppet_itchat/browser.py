"""
Python Wechaty - https://github.com/wechaty/python-wechaty

Authors:    Jingjing WU (吴京京) <https://github.com/wj-Mcat>

2020-now @ Copyright Wechaty

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

import os
import pickle
import random
import re
import time
from typing import Optional
from datetime import datetime

from requests import Session
from wechaty_puppet import get_logger
from dataclasses import dataclass, field

from wechaty_puppet.exceptions import WechatyPuppetError
from wechaty_puppet_itchat.config import (
    CACHE_DIR,
    BASE_URL,
    USER_AGENT,
    UOS_PATCH_EXTSPAM,
    UOS_PATCH_CLIENT_VERSION,
    LOGIN_TIMEOUT
)

logger = get_logger('Browser')

WX_UIN = 'wxuin'

@dataclass
class LoginCode:
    uuid: str
    datetime: datetime = field(default_factory=datetime.now)

    def is_timeout(self) -> bool:
        """check if the uuid is timeout"""
        now = datetime.now()
        return (now - self.datetime).seconds > LOGIN_TIMEOUT


class Browser:
    _session: Optional[Session] = None

    def __init__(self, session: Session):
        """every instance """
        self.session = session
        self.is_alive: bool = False

        self.login_info: dict = {
            'login_uuid': None
        }

        # 1. init login code
        uuid = self.get_qr_uuid()
        if not uuid:
            raise WechatyPuppetError('can"t fetch the login info from server ...')

        self.login_code: LoginCode = LoginCode(
            uuid=uuid
        )

    @staticmethod
    def instance() -> Browser:
        """singleton instance for global session"""
        if Browser._session:
            return Browser(Browser._session)

        # 1. load form
        os.makedirs(CACHE_DIR, exist_ok=True)
        cache_file = os.path.join(CACHE_DIR, 'session.pkl')
        if os.path.exists(cache_file):
            with open(cache_file, 'rb', encoding='utf-8') as f:
                session = pickle.load(f)
                assert isinstance(session, Session)
            return Browser(session)

        return Browser(Session())

    def get_login_uuid(self) -> Optional[str]:
        """get login uuid of qrcode"""
        logger.info('get login info ...')
        cookies: dict = self.session.cookies.get_dict()
        if WX_UIN in cookies:
            url = f'{BASE_URL}/cgi-bin/mmwebwx-bin/webwxpushloginurl?uin={cookies[WX_UIN]}'
            headers = {'User-Agent': USER_AGENT}
            r = self.session.get(url, headers=headers).json()
            if 'uuid' in r and r.get('ret') in (0, '0'):
                return r['uuid']
        return None

    def have_login(self, uuid: str) -> bool:
        url = '%s/cgi-bin/mmwebwx-bin/login' % BASE_URL
        local_time = int(time.time())
        params = 'loginicon=true&uuid=%s&tip=1&r=%s&_=%s' % (
            uuid, int(-local_time / 1579), local_time)
        headers = {'User-Agent': USER_AGENT}
        response = self.session.get(url, params=params, headers=headers)
        regx = r'window.code=(\d+)'
        data = re.search(regx, response.text)
        if data and data.group(1) == '200':
            self.init_login_info(response.text)
            return self.is_alive
        return False

    def init_login_info(self, login_str):
        regx = r'window.redirect_uri="(\S+)";'
        self.login_info['url'] = re.search(regx, login_str).group(1)
        headers = {'User-Agent': USER_AGENT,
                   'client-version': UOS_PATCH_CLIENT_VERSION,
                   'extspam': UOS_PATCH_EXTSPAM,
                   'referer': 'https://wx.qq.com/?&lang=zh_CN&target=t'
                   }

        response = self.session.get(
            self.login_info['url'],
            headers=headers,
            allow_redirects=False
        )

        self.login_info['url'] = self.login_info['url'][:self.login_info['url'].rfind('/')]
        for indexUrl, detailedUrl in (
            ("wx2.qq.com", ("file.wx2.qq.com", "webpush.wx2.qq.com")),
            ("wx8.qq.com", ("file.wx8.qq.com", "webpush.wx8.qq.com")),
            ("qq.com", ("file.wx.qq.com", "webpush.wx.qq.com")),
            ("web2.wechat.com", ("file.web2.wechat.com", "webpush.web2.wechat.com")),
            ("wechat.com", ("file.web.wechat.com", "webpush.web.wechat.com"))):
            file_url, sync_url = ['https://%s/cgi-bin/mmwebwx-bin' % url for url in detailedUrl]
            if indexUrl in self.login_info['url']:
                self.login_info['fileUrl'], self.login_info['syncUrl'] = \
                    file_url, sync_url
                break
        else:
            self.login_info['fileUrl'] = self.login_info['syncUrl'] = self.login_info['url']
        self.login_info['deviceid'] = 'e' + repr(random.random())[2:17]
        self.login_info['logintime'] = int(time.time() * 1e3)
        self.login_info['BaseRequest'] = {}
        cookies = self.session.cookies.get_dict()
        self.login_info['skey'] = self.login_info['BaseRequest']['Skey'] = ""
        self.login_info['wxsid'] = self.login_info['BaseRequest']['Sid'] = cookies["wxsid"]
        self.login_info['wxuin'] = self.login_info['BaseRequest']['Uin'] = cookies["wxuin"]
        self.login_info['pass_ticket'] = self.login_info['BaseRequest']['DeviceID'] = self.login_info['deviceid']
        if not all([key in self.login_info for key in ('skey', 'wxsid', 'wxuin', 'pass_ticket')]):
            logger.error('Your wechat account may be LIMITED to log in WEB wechat, error info:\n%s' % response.text)
            self.is_alive = False
        else:
            self.is_alive = True

    def get_qr_uuid(self) -> Optional[str]:
        url = '%s/jslogin' % BASE_URL
        params = {
            'appid': 'wx782c26e4c19acffb',
            'fun': 'new',
            'redirect_uri': 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage?mod=desktop',
            'lang': 'zh_CN'}
        headers = {'User-Agent': USER_AGENT}
        response = self.session.get(url, params=params, headers=headers)
        regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)";'
        data = re.search(regx, response.text)
        if data and data.group(1) == '200':
            return data.group(2)
        return None
