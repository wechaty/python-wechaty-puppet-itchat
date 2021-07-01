"""
Python Wechaty - https://github.com/wechaty/python-wechaty

Authors:    Huan LI (李卓桓) <https://github.com/huan>
            Jingjing WU (吴京京) <https://github.com/wj-Mcat>

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
import os
# TODO: need to fix error -> found module but no type hints or library stubs
from wechaty_puppet import get_logger   # type: ignore

logger = get_logger('WechatyPuppetServiceConfig')


def get_token():
    """
    get the token from environment variable
    """
    return os.environ.get('WECHATY_PUPPET_SERVICE_TOKEN', None) or \
        os.environ.get('TOKEN', None) or \
        os.environ.get('token', None) or None


def get_endpoint():
    """
    get the endpoint from environment variable
    """
    return os.environ.get('WECHATY_PUPPET_SERVICE_ENDPOINT', None) or \
        os.environ.get('ENDPOINT', None) or \
        os.environ.get('endpoint', None) or None
